"""
app.py
====================================================================
Routing layer SOS Verified Alert System.

Pembagian tanggung jawab (arsitektur bersih):
    rsa.py  -> algoritma RSA murni (tanpa import Flask/DB)
    db.py   -> koneksi & query database (parameterized, psycopg2)
    app.py  -> routing HTTP + validasi input + orkestrasi rsa/db

ATURAN:
* Tidak ada library kriptografi sama sekali di file ini.
* PRIVATE KEY TIDAK pernah disimpan ke database dan tidak pernah di-log.
  Private key hanya diterima dari request, dipakai, lalu dibuang.
* Semua angka RSA dikirim sebagai STRING (serialize via B()) agar
  JavaScript tidak kehilangan presisi (Number di JS aman < 2^53).

Endpoint:
    GET  /                          landing page
    GET  /sender                    halaman Pengirim
    GET  /center                    halaman Pusat Darurat
    GET  /attacker                  halaman Penyadap (man-in-the-middle)
    GET  /health                    status aplikasi + database
    POST /api/keygen                pembangkitan kunci (Pengirim/Pusat)
    POST /api/users                 daftarkan user + public key
    GET  /api/users?role=...        daftar user (data publik saja)
    POST /api/sign                  hash + digital signature
    POST /api/encrypt               enkripsi payload -> blok cipher
    POST /api/send                  simpan paket SOS ke database
    GET  /api/inbox?center_id=...   inbox Pusat Darurat dari database
    POST /api/inbox/<id>/decrypt    dekripsi dengan private key pusat
    POST /api/inbox/<id>/verify     verifikasi signature (status disimpan)
    POST /api/inbox/<id>/tamper     simulasi manipulasi data
    POST /api/inbox/<id>/reset      kembalikan ciphertext ke asli
====================================================================
"""

from datetime import datetime

from flask import Flask, jsonify, render_template, request

import db
import rsa

app = Flask(__name__)
# selalu kirim file statis terbaru (penting saat demo)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

EXPIRED_SECONDS = 5 * 60  # alert dianggap kadaluarsa setelah 5 menit


# --------------------------------------------------------------------
# Helper serialisasi: SEMUA angka (int) -> string.
# Menjaga presisi angka RSA saat melewati JavaScript.
# --------------------------------------------------------------------
def B(value):
    """Rekursif mengubah int menjadi str (bool dibiarkan sebagai bool)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, dict):
        return {k: B(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [B(v) for v in value]
    return value


def ok(data, code=200):
    return jsonify(B({"ok": True, **data})), code


def fail(errors, code=400, **extra):
    return jsonify(B({"ok": False, "errors": errors, **extra})), code


def to_int(value, name):
    """Konversi input (boleh string) ke int. Mengembalikan (nilai, error)."""
    try:
        return int(str(value).strip()), None
    except (ValueError, TypeError):
        return None, f"Nilai {name} harus berupa bilangan bulat."


def _body():
    return request.get_json(silent=True) or {}


# ====================================================================
# HALAMAN
# ====================================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sender")
def page_sender():
    return render_template("sender.html")


@app.route("/center")
def page_center():
    return render_template("center.html")


@app.route("/attacker")
def page_attacker():
    return render_template("attacker.html")


# ====================================================================
# GET /health
# ====================================================================
@app.route("/health")
def health():
    return ok({
        "app": "SOS Verified Alert System",
        "rsa": "manual from-scratch (tanpa library kriptografi)",
        "database": db.health(),
        "time": datetime.now().isoformat(timespec="seconds"),
    })


# ====================================================================
# POST /api/keygen  ->  generateKey(p, q, e)
# Private key HANYA dikembalikan sekali ke klien (untuk localStorage),
# tidak pernah disimpan di database maupun log.
# ====================================================================
@app.route("/api/keygen", methods=["POST"])
def api_keygen():
    data = _body()
    p, e1 = to_int(data.get("p"), "p")
    q, e2 = to_int(data.get("q"), "q")
    e, e3 = to_int(data.get("e"), "e")
    errors = [x for x in (e1, e2, e3) if x]
    if errors:
        return fail(errors)

    result = rsa.generate_key(p, q, e)
    if not result["valid"]:
        return fail([result["error"]], detail=result["logs"])

    return ok({
        "public": {"e": result["e"], "n": result["n"]},
        "private": {"d": result["d"], "n": result["n"]},  # -> localStorage klien
        "p": result["p"], "q": result["q"], "e": result["e"],
        "n": result["n"], "phi": result["phi"],
        # verifikasi (e*d) mod phi = 1 dihitung di server agar presisi
        "ed_mod_phi": (result["e"] * result["d"]) % result["phi"],
        "logs": result["logs"],
    })


# ====================================================================
# POST /api/users  &  GET /api/users
# ====================================================================
@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = _body()
    name = str(data.get("name", "")).strip()
    role = str(data.get("role", "")).strip()
    pub_e = str(data.get("pub_e", "")).strip()
    pub_n = str(data.get("pub_n", "")).strip()

    errors = []
    if not name:
        errors.append("name wajib diisi.")
    if role not in ("sender", "center"):
        errors.append("role harus 'sender' atau 'center'.")
    if not pub_e or not pub_n:
        errors.append("pub_e dan pub_n wajib diisi (public key).")
    if errors:
        return fail(errors)

    user = db.create_user(name, role, pub_e, pub_n)
    return ok({"user": user}, code=201)


@app.route("/api/users", methods=["GET"])
def api_list_users():
    role = request.args.get("role")
    if role and role not in ("sender", "center"):
        return fail(["role harus 'sender' atau 'center'."])
    users = db.get_users(role)
    return ok({"users": users})


# ====================================================================
# POST /api/sign  ->  hashMessage + signMessage
# Body: { payload, private: { d, n } }  (private key dari localStorage,
# dipakai sekali lalu dibuang - TIDAK disimpan/di-log).
# ====================================================================
@app.route("/api/sign", methods=["POST"])
def api_sign():
    data = _body()
    payload = str(data.get("payload", "")).strip()
    private = data.get("private") or {}

    if not payload:
        return fail(["Payload tidak boleh kosong."])

    d, e1 = to_int(private.get("d"), "private.d")
    n, e2 = to_int(private.get("n"), "private.n")
    errors = [x for x in (e1, e2) if x]
    if errors:
        return fail(errors)
    if d is None or n is None:
        return fail(["Private key pengirim tidak ditemukan di request "
                     "(cek localStorage)."])

    signature, hash_val, log_sign = rsa.sign_message(payload, d, n)
    hash_log = log_sign[0]["log_hash"]
    return ok({
        "payload": payload,
        "hash": hash_val,
        "hash_log": hash_log,
        "ascii": [ord(c) for c in payload],
        "signature": signature,
        "pow_log": log_sign[1]["log_pow"],
        "public": {"n": n},  # n dipakai UI menampilkan rumus; d TIDAK dikirim balik
    })


# ====================================================================
# POST /api/encrypt  ->  textToBlocks + encrypt (public key PUSAT)
# Body: { text, e, n }
# ====================================================================
@app.route("/api/encrypt", methods=["POST"])
def api_encrypt():
    data = _body()
    text = str(data.get("text", ""))
    e, e1 = to_int(data.get("e"), "e")
    n, e2 = to_int(data.get("n"), "n")
    errors = [x for x in (e1, e2) if x]
    if errors:
        return fail(errors)
    if not text:
        return fail(["Teks yang akan dienkripsi kosong."])

    blocks, info, steps = rsa.encrypt(text, e, n)
    return ok({
        "ciphertext": blocks,
        "block_size": info["size"],
        "digits": info["digits"],
        "digit_string": info["digit_string"],
        "num_blocks": len(blocks),
        "steps": steps,
        "public": {"e": e, "n": n},
    })


# ====================================================================
# POST /api/send  ->  simpan paket SOS
# Body: { sender_id, center_id, ciphertext[], original_ciphertext[], signature }
# ====================================================================
@app.route("/api/send", methods=["POST"])
def api_send():
    data = _body()
    sender_id, e1 = to_int(data.get("sender_id"), "sender_id")
    center_id, e2 = to_int(data.get("center_id"), "center_id")
    signature = data.get("signature")
    ciphertext = data.get("ciphertext")
    original = data.get("original_ciphertext") or ciphertext

    errors = [x for x in (e1, e2) if x]
    if errors:
        return fail(errors)
    if not isinstance(ciphertext, list) or not ciphertext:
        return fail(["ciphertext harus berupa daftar blok."])
    if signature in (None, ""):
        return fail(["signature wajib diisi."])
    if str(signature).lstrip("-").isdigit() is False:
        return fail(["signature harus berupa angka (string)."])
    try:
        ciphertext = [str(x) for x in ciphertext]
        original = [str(x) for x in original]
    except (ValueError, TypeError):
        return fail(["Blok ciphertext harus berupa angka/string angka."])

    sender = db.get_user(sender_id)
    center = db.get_user(center_id)
    if not sender or sender["role"] != "sender":
        return fail(["sender_id tidak ditemukan atau bukan role sender."])
    if not center or center["role"] != "center":
        return fail(["center_id tidak ditemukan atau bukan role center."])

    msg = db.create_message(sender_id, center_id, ciphertext, original, signature)
    return ok({"message": msg}, code=201)


# ====================================================================
# GET /api/inbox?center_id=...
# ====================================================================
@app.route("/api/inbox", methods=["GET"])
def api_inbox():
    """Tanpa center_id -> semua paket (dipakai halaman Penyadap untuk
    'menyadap' trafik; isinya memang metadata terbuka)."""
    center_arg = request.args.get("center_id")
    if center_arg is None:
        messages = db.list_messages()
    else:
        center_id, err = to_int(center_arg, "center_id")
        if err:
            return fail([err])
        center = db.get_user(center_id)
        if not center or center["role"] != "center":
            return fail(["center_id tidak ditemukan atau bukan role center."])
        messages = db.list_messages(center_id)

    # lampirkan nama pengirim & pusat (data publik) untuk keperluan tampilan
    out = []
    for m in messages:
        sender = db.get_user(m["sender_id"])
        center = db.get_user(m["center_id"])
        out.append({**m,
                    "sender_name": sender["name"] if sender else "?",
                    "center_name": center["name"] if center else "?"})
    return ok({"messages": out})


# --------------------------------------------------------------------
# Helper bersama untuk endpoint decrypt/verify
# --------------------------------------------------------------------
def _load_message(msg_id):
    """Ambil pesan + pasangan kunci publik pengirim & pusat dari DB."""
    msg, err = to_int(msg_id, "id")
    if err:
        return None, None, None, [err]
    msg = db.get_message(msg)
    if not msg:
        return None, None, None, ["Pesan tidak ditemukan."]
    center = db.get_user(msg["center_id"])
    sender = db.get_user(msg["sender_id"])
    if not center or not sender:
        return None, None, None, ["Relasi user pesan tidak ditemukan."]
    return msg, center, sender, None


def _center_private(body):
    """Ambil private key pusat darurat dari request (sekali pakai)."""
    private = (body or {}).get("private") or {}
    d, e1 = to_int(private.get("d"), "private.d")
    n, e2 = to_int(private.get("n"), "private.n")
    errors = [x for x in (e1, e2) if x]
    if errors:
        return None, None, errors
    if d is None or n is None:
        return None, None, ["Private key pusat darurat tidak ditemukan di request."]
    return d, n, None


def _parse_payload(payload):
    parts = payload.split("|", 4)
    if len(parts) < 5:
        return {"nama": "-", "lat": "-", "lon": "-", "waktu": "-", "pesan": payload}
    return {"nama": parts[0], "lat": parts[1], "lon": parts[2],
            "waktu": parts[3], "pesan": parts[4]}


def _check_expiry(waktu_str):
    """Cek kedaluwarsa alert 5 menit (fitur tambahan, di luar RSA)."""
    try:
        t = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return {"checked": False,
                "reason": "Format timestamp tidak dikenali (butuh YYYY-MM-DD HH:mm:ss)."}
    delta = int((datetime.now() - t).total_seconds())
    return {"checked": True, "expired": abs(delta) > EXPIRED_SECONDS,
            "delta_seconds": delta, "limit_seconds": EXPIRED_SECONDS}


def _decrypt_message(msg, center, d, n):
    """Dekripsi ciphertext pesan dengan private key pusat darurat."""
    if str(n) != str(center["pub_n"]):
        return None, ["Private key tidak cocok dengan public key pusat darurat "
                      "untuk pesan ini."]
    cipher = [int(x) for x in msg["ciphertext"]]
    plain, info, steps = rsa.decrypt(cipher, d, n)
    return {"plain": plain, "blocks": info["blocks"], "steps": steps}, None


# ====================================================================
# POST /api/inbox/<id>/decrypt
# ====================================================================
@app.route("/api/inbox/<int:msg_id>/decrypt", methods=["POST"])
def api_decrypt(msg_id):
    msg, center, sender, errs = _load_message(msg_id)
    if errs:
        return fail(errs)
    d, n, errs = _center_private(_body())
    if errs:
        return fail(errs)

    result, errs = _decrypt_message(msg, center, d, n)
    if errs:
        return fail(errs)

    fields = _parse_payload(result["plain"])
    cipher = [int(x) for x in msg["ciphertext"]]
    tabel = [{"cipher": c, "blok": b} for c, b in zip(cipher, result["blocks"])]

    return ok({
        "id": msg["id"],
        "cipher": msg["ciphertext"],
        "tabel": tabel,
        "plain": result["plain"],
        "blocks": result["blocks"],
        "steps": result["steps"],
        "fields": fields,
        "expiry": _check_expiry(fields["waktu"]),
        "status": msg["status"],
        "tampered": msg["tampered"],
        "center_public": {"e": center["pub_e"], "n": center["pub_n"]},
        "sender_public": {"e": sender["pub_e"], "n": sender["pub_n"]},
    })


# ====================================================================
# POST /api/inbox/<id>/verify  ->  verifikasi signature + update status
# ====================================================================
@app.route("/api/inbox/<int:msg_id>/verify", methods=["POST"])
def api_verify(msg_id):
    msg, center, sender, errs = _load_message(msg_id)
    if errs:
        return fail(errs)
    d, n, errs = _center_private(_body())
    if errs:
        return fail(errs)

    result, errs = _decrypt_message(msg, center, d, n)
    if errs:
        return fail(errs)

    plain = result["plain"]
    signature = int(msg["signature"])
    sender_e = int(sender["pub_e"])
    sender_n = int(sender["pub_n"])

    valid, verified_hash, recomputed_hash, log_verify = rsa.verify_signature(
        plain, signature, sender_e, sender_n)

    status = "valid" if valid else "invalid"
    msg = db.update_message(msg_id, status=status)

    fields = _parse_payload(plain)
    return ok({
        "id": msg["id"],
        "valid": valid,
        "status": msg["status"],
        "tampered": msg["tampered"],
        "verified_hash": verified_hash,
        "recomputed_hash": recomputed_hash,
        "signature": msg["signature"],
        "sender_public": {"e": sender_e, "n": sender_n},
        "center_public": {"e": center["pub_e"], "n": center["pub_n"]},
        "verified_text": plain,
        "fields": fields,
        "expiry": _check_expiry(fields["waktu"]),
        "pow_log": log_verify[0]["log_pow"],
    })


# ====================================================================
# POST /api/inbox/<id>/tamper  ->  simulasi serangan (halaman Penyadap)
#
# Dua cara (kompatibel):
#   a) GAYA BARU (halaman /attacker): { payload: {nama,lat,lon,waktu,pesan} }
#      Penyerang menyusun payload PALSU sendiri — TIDAK butuh isi asli
#      (memang tidak bisa membaca isi; hanya butuh public key pusat untuk
#      mengenkripsi ulang + signature lama hasil sadapan).
#   b) GAYA LAMA: { mode: message|location, plaintext, ... }
#
# Menyimpan ciphertext BARU, ciphertext asli tetap ada di
# original_ciphertext sehingga tombol Reset bisa mengembalikan.
# ====================================================================
@app.route("/api/inbox/<int:msg_id>/tamper", methods=["POST"])
def api_tamper(msg_id):
    msg, center, sender, errs = _load_message(msg_id)
    if errs:
        return fail(errs)

    data = _body()
    new_text, mode = None, None

    payload = data.get("payload")
    if isinstance(payload, dict):
        # --- gaya baru: payload palsu hasil susunan penyerang ---
        fields = {k: str(payload.get(k, "")).strip()
                  for k in ("nama", "lat", "lon", "waktu", "pesan")}
        if not fields["nama"] or not fields["pesan"]:
            return fail(["nama dan pesan pada payload palsu wajib diisi."])
        new_text = "|".join([fields["nama"], fields["lat"], fields["lon"],
                             fields["waktu"], fields["pesan"]])
        mode = str(data.get("mode", "payload-palsu"))
    else:
        # --- gaya lama: ubah sebagian dari plaintext hasil dekripsi ---
        plaintext = str(data.get("plaintext", "")).strip()
        if not plaintext:
            return fail(["payload (payload palsu) atau plaintext wajib dikirim."])
        old = _parse_payload(plaintext)
        mode = data.get("mode")
        if mode == "message":
            pesan = str(data.get("pesan", "Terjadi kebakaran")).strip()
            new_text = "|".join([old["nama"], old["lat"], old["lon"],
                                 old["waktu"]]) + "|" + pesan
        elif mode == "location":
            lat = str(data.get("lat", "-6.200000")).strip()
            lon = str(data.get("lon", "106.816666")).strip()
            new_text = "|".join([old["nama"], lat, lon, old["waktu"],
                                 old["pesan"]])
        else:
            return fail(["mode harus 'message' atau 'location', "
                         "atau kirim objek 'payload'."])

    # Penyerang TIDAK punya private key -> cukup enkripsi ulang dengan
    # public key pusat darurat, tetapi TIDAK bisa membuat signature valid.
    e = int(center["pub_e"])
    n = int(center["pub_n"])
    new_cipher, *_ = rsa.encrypt(new_text, e, n)

    msg = db.update_message(msg_id, ciphertext=new_cipher, tampered=True,
                            status="pending")
    return ok({
        "id": msg["id"],
        "mode": mode,
        "text": new_text,
        "cipher": msg["ciphertext"],
        "tampered": msg["tampered"],
        "status": msg["status"],
    })


# ====================================================================
# POST /api/inbox/<id>/reset  ->  kembalikan ciphertext ke asli
# ====================================================================
@app.route("/api/inbox/<int:msg_id>/reset", methods=["POST"])
def api_reset(msg_id):
    msg, center, sender, errs = _load_message(msg_id)
    if errs:
        return fail(errs)

    msg = db.update_message(msg_id,
                            ciphertext=msg["original_ciphertext"],
                            tampered=False,
                            status="pending")
    return ok({
        "id": msg["id"],
        "cipher": msg["ciphertext"],
        "tampered": msg["tampered"],
        "status": msg["status"],
    })


# ====================================================================
if __name__ == "__main__":
    import os
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))  # Render menyuntikkan PORT
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
