"""
test_e2e.py - Uji end-to-end SOS Verified Alert System (arsitektur baru)

Menjalankan alur lengkap lewat API:
keygen -> users -> sign -> encrypt -> send -> inbox -> decrypt -> verify
+ skenario manipulasi pesan/lokasi + reset + validasi input salah.

Jalankan sambil server hidup:  python app.py  lalu  python test_e2e.py
"""

import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:5000"

# data demo teruji
SENDER_PQE = (1009, 1013, 17)
CENTER_PQE = (31627, 31649, 13)
PAYLOAD = "Fwxz|-7.275847|112.794702|2026-10-07 13:20:15|Terjadi kecelakaan lalu lintas"


def post(path, body=None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body or {}).encode(),
        headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def get(path):
    r = urllib.request.urlopen(BASE + path, timeout=30)
    return r.status, (json.loads(r.read()) if "/api" in path or path == "/health"
                      else r.read().decode())


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if detail else ""))


# ====================================================================
# 1. HALAMAN & HEALTH
# ====================================================================
s, html = get("/")
check("GET / landing", s == 200 and "Pengirim" in html and "Pusat Darurat" in html)
s, html = get("/sender")
check("GET /sender terpisah", s == 200 and "Key Generation" in html and "Generate Signature" in html)
s, html = get("/center")
check("GET /center terpisah", s == 200 and "Inbox" in html and "Verifikasi Signature" in html)
s, html = get("/attacker")
check("GET /attacker terpisah", s == 200 and "Penyadap" in html and "Serang" in html
      and "attack-cap-grid" in html)
check("pusat darurat tanpa tombol serangan", "btn-atk-msg" not in html)
s, d = get("/health")
check("/health ok", s == 200 and d["ok"] is True, d.get("database"))
check("db mode in-memory (lokal)", d["database"]["mode"] in ("in-memory", "postgresql"),
      d["database"]["mode"])

# ====================================================================
# 2. KEYGEN (termasuk validasi salah)
# ====================================================================
s, d = post("/api/keygen", {"p": SENDER_PQE[0], "q": SENDER_PQE[1], "e": SENDER_PQE[2]})
check("keygen pengirim ok", s == 200 and d["ok"], d.get("errors"))
SENDER = {"private": d["private"], "public": d["public"]}
check("pub/priv sebagai STRING", isinstance(d["public"]["n"], str) and isinstance(d["private"]["d"], str))
check("n pengirim = 1022117", d["n"] == "1022117", d["n"])
check("d pengirim = 180017", d["private"]["d"] == "180017")
check("(e*d) mod phi = 1", d["ed_mod_phi"] == "1", d["ed_mod_phi"])
check("logs keygen lengkap", any("phi" in str(l.get("tahap", "")) for l in d["logs"]))

s, d = post("/api/keygen", {"p": CENTER_PQE[0], "q": CENTER_PQE[1], "e": CENTER_PQE[2]})
check("keygen pusat ok", s == 200 and d["ok"], d.get("errors"))
CENTER = {"private": d["private"], "public": d["public"]}
check("n pusat = 1000962923", d["n"] == "1000962923", d["n"])
check("d pusat = 615938245", d["private"]["d"] == "615938245")

for case, body, needle in [
    ("p bukan prima", {"p": 1008, "q": 1013, "e": 17}, "prima"),
    ("gcd != 1", {"p": 1009, "q": 1013, "e": 16}, "gcd"),
    ("p == q", {"p": 1009, "q": 1009, "e": 17}, "sama"),
    ("n terlalu kecil", {"p": 2, "q": 3, "e": 5}, "phi"),
    ("input bukan angka", {"p": "abc", "q": 1013, "e": 17}, "bulat"),
]:
    s, d = post("/api/keygen", body)
    msg = " ".join(d.get("errors") or [])
    check(f"validasi: {case}", s == 400 and needle in msg, msg[:70])

# ====================================================================
# 3. REGISTRASI USER (public key saja ke database)
# ====================================================================
s, d = post("/api/users", {"name": "Fwxz", "role": "sender",
                           "pub_e": SENDER["public"]["e"], "pub_n": SENDER["public"]["n"]})
check("daftar user pengirim", s == 201 and d["ok"], d.get("errors"))
SENDER_ID = d["user"]["id"]
check("tanpa field private", "private" not in json.dumps(d["user"]).lower() or
      '"d"' not in json.dumps(d["user"]))

s, d = post("/api/users", {"name": "Pusat Darurat Surabaya", "role": "center",
                           "pub_e": CENTER["public"]["e"], "pub_n": CENTER["public"]["n"]})
check("daftar user pusat", s == 201 and d["ok"], d.get("errors"))
CENTER_ID = d["user"]["id"]

s, d = get("/api/users?role=center")
check("GET /api/users?role=center", s == 200 and d["ok"] and
      any(u["id"] == CENTER_ID for u in d["users"]))
check("users hanya berisi public key", all(
      k in u for u in d["users"] for k in ("pub_e", "pub_n")))

s, d = post("/api/users", {"name": "", "role": "hacker", "pub_e": "1", "pub_n": "2"})
check("validasi user ditolak", s == 400)

# ====================================================================
# 4. SIGN
# ====================================================================
s, d = post("/api/sign", {"payload": PAYLOAD, "private": SENDER["private"]})
check("POST /api/sign ok", s == 200 and d["ok"], d.get("errors"))
check("hash = 5753 (string)", d["hash"] == "5753", d["hash"])
check("signature = 118799 (string)", d["signature"] == "118799", d["signature"])
check("log modPow tampil", len(d["pow_log"]) > 5)
check("private tidak di-echo", "private" not in d and '"d"' not in json.dumps(d))

s, d = post("/api/sign", {"payload": "", "private": SENDER["private"]})
check("sign payload kosong ditolak", s == 400)
s, d = post("/api/sign", {"payload": PAYLOAD, "private": {}})
check("sign tanpa private ditolak", s == 400)

# ====================================================================
# 5. ENCRYPT (public key pusat)
# ====================================================================
s, d = post("/api/encrypt", {"text": PAYLOAD,
                             "e": CENTER["public"]["e"], "n": CENTER["public"]["n"]})
check("POST /api/encrypt ok", s == 200 and d["ok"], d.get("errors"))
CIPHER = d["ciphertext"]
check("26 blok", d["num_blocks"] == "26", d["num_blocks"])
check("ukuran blok 3 karakter", d["block_size"] == "3", d["block_size"])
check("semua blok STRING", all(isinstance(x, str) for x in CIPHER))
check("digit stream awal 070119120", d["digit_string"].startswith("070119120"))
check("tabel langkah tersedia", bool(d["steps"] and d["steps"][-1].get("tabel")))

# ====================================================================
# 6. SEND + INBOX
# ====================================================================
s, d = post("/api/send", {"sender_id": SENDER_ID, "center_id": CENTER_ID,
                          "ciphertext": CIPHER, "original_ciphertext": CIPHER,
                          "signature": "118799"})
check("POST /api/send ok", s == 201 and d["ok"], d.get("errors"))
MSG_ID = d["message"]["id"]
check("status pending", d["message"]["status"] == "pending")
check("tampered false", d["message"]["tampered"] is False)
check("ciphertext terimpan sebagai list string",
      isinstance(d["message"]["ciphertext"], list) and
      all(isinstance(x, str) for x in d["message"]["ciphertext"]))

s, d = post("/api/send", {"sender_id": 99999, "center_id": CENTER_ID,
                          "ciphertext": CIPHER, "signature": "1"})
check("send user tak dikenal ditolak", s == 400)

s, d = get(f"/api/inbox?center_id={CENTER_ID}")
check("GET /api/inbox ok", s == 200 and d["ok"])
check("inbox berisi 1 pesan", len(d["messages"]) == 1, len(d["messages"]))
check("inbox menyertakan nama pengirim", d["messages"][0]["sender_name"] == "Fwxz")

# ====================================================================
# 7. DECRYPT
# ====================================================================
s, d = post(f"/api/inbox/{MSG_ID}/decrypt", {"private": CENTER["private"]})
check("POST decrypt ok", s == 200 and d["ok"], d.get("errors"))
check("plaintext sesuai payload", d["plain"] == PAYLOAD, repr(d["plain"])[:50])
check("field terpecah", d["fields"]["nama"] == "Fwxz" and
      d["fields"]["pesan"] == "Terjadi kecelakaan lalu lintas")
check("cek kedaluwarsa ada", d["expiry"]["checked"])
check("blok hasil sebagai string", all(isinstance(x, str) for x in d["blocks"]))

s, d = post(f"/api/inbox/{MSG_ID}/decrypt", {"private": {"d": "5", "n": "999"}})
check("private key salah ditolak", s == 400, d.get("errors"))

# ====================================================================
# 8. VERIFY - SKENARIO VALID
# ====================================================================
s, d = post(f"/api/inbox/{MSG_ID}/verify", {"private": CENTER["private"]})
check("POST verify ok", s == 200 and d["ok"], d.get("errors"))
check("SOS VALID", d["valid"] is True, f'{d["verified_hash"]} vs {d["recomputed_hash"]}')
check("hash sama = 5753", d["verified_hash"] == "5753" and d["recomputed_hash"] == "5753")
check("status valid tersimpan", d["status"] == "valid")
check("log verifikasi tampil", len(d["pow_log"]) > 5)

# ====================================================================
# 9. SERANGAN: PENYADAP MENGGANTI ISI (payload palsu, tanpa isi asli)
# ====================================================================
s, d = get("/api/inbox")
check("GET /api/inbox tanpa filter (sadap)", s == 200 and d["ok"] and len(d["messages"]) >= 1)
check("inbox memuat nama pusat", all("center_name" in m for m in d["messages"]))

FAKE = {"nama": "Fwxz", "lat": "-7.275847", "lon": "112.794702",
        "waktu": "2026-10-07 13:20:15",
        "pesan": "Terjadi kebakaran hebat di gedung pusat kota"}
s, d = post(f"/api/inbox/{MSG_ID}/tamper", {"mode": "payload-palsu", "payload": FAKE})
check("tamper payload-palsu ok", s == 200 and d["ok"], d.get("errors"))
check("isi berubah total", "Terjadi kebakaran hebat" in d["text"], d["text"][-50:])
check("ditandai tampered", d["tampered"] is True)

s, d = post(f"/api/inbox/{MSG_ID}/decrypt", {"private": CENTER["private"]})
check("dekapripsi hasil tamper", "Terjadi kebakaran hebat" in d["plain"])

s, d = post(f"/api/inbox/{MSG_ID}/verify", {"private": CENTER["private"]})
check("serangan penyadap -> TIDAK VALID", d["valid"] is False,
      f'{d["verified_hash"]} vs {d["recomputed_hash"]}')
check("verifiedHash tetap hash asli 5753", d["verified_hash"] == "5753", d["verified_hash"])
check("recomputedHash beda", d["recomputed_hash"] != "5753", d["recomputed_hash"])
check("status invalid tersimpan", d["status"] == "invalid")
check("signature tidak diubah penyerang", d["signature"] == "118799")

# kompatibilitas gaya lama (mode + plaintext) tetap berfungsi
post(f"/api/inbox/{MSG_ID}/reset")
s, d = post(f"/api/inbox/{MSG_ID}/tamper",
            {"mode": "message", "plaintext": PAYLOAD, "pesan": "Terjadi kebakaran"})
check("gaya lama (mode+plaintext) masih jalan", s == 200 and d["ok"], d.get("errors"))
post(f"/api/inbox/{MSG_ID}/reset")

s, d = post(f"/api/inbox/{MSG_ID}/tamper", {"payload": {"nama": "", "pesan": ""}})
check("payload palsu kosong ditolak", s == 400)

# ====================================================================
# 10. RESET -> VALID LAGI
# ====================================================================
s, d = post(f"/api/inbox/{MSG_ID}/reset")
check("reset ok", s == 200 and d["ok"])
check("tampered false lagi", d["tampered"] is False)
s, d = post(f"/api/inbox/{MSG_ID}/verify", {"private": CENTER["private"]})
check("setelah reset -> VALID", d["valid"] is True, f'{d["verified_hash"]} vs {d["recomputed_hash"]}')

# ====================================================================
# 11. SERANGAN: PENYADAP MEMALSUKAN LOKASI
# ====================================================================
FAKE_LOC = {**FAKE, "lat": "-6.200000", "lon": "106.816666"}
s, d = post(f"/api/inbox/{MSG_ID}/tamper", {"payload": FAKE_LOC})
check("tamper lokasi ok", s == 200 and d["ok"], d.get("errors"))
check("koordinat berubah", "-6.200000|106.816666" in d["text"], d["text"][:45])

s, d = post(f"/api/inbox/{MSG_ID}/verify", {"private": CENTER["private"]})
check("manipulasi lokasi -> TIDAK VALID", d["valid"] is False,
      f'{d["verified_hash"]} vs {d["recomputed_hash"]}')

# kembalikan
post(f"/api/inbox/{MSG_ID}/reset")
s, d = post(f"/api/inbox/{MSG_ID}/verify", {"private": CENTER["private"]})
check("reset akhir -> VALID", d["valid"] is True)

# ====================================================================
# RINGKASAN
# ====================================================================
print("\n" + "=" * 60)
passed = sum(1 for _, okk in results if okk)
total = len(results)
print(f"RESULT: {passed}/{total} test PASSED")
if passed != total:
    print("GAGAL:")
    for name, okk in results:
        if not okk:
            print(" -", name)
