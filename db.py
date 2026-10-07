"""
db.py
====================================================================
Lapisan akses database SOS Verified Alert System.

* Driver: psycopg2 (hanya driver database, BUKAN library kriptografi).
* Koneksi diambil dari environment variable DATABASE_URL
  (Supabase PostgreSQL - Session Pooler). JANGAN hardcode kredensial.
* SEMUA query memakai parameterized query (%s) -> aman dari SQL injection.
* Jika DATABASE_URL tidak di-set, modul otomatis memakai penyimpanan
  in-memory agar demo lokal tetap jalan tanpa database.

BATASAN KEAMANAN:
* PRIVATE KEY RSA tidak pernah disimpan lewat modul ini.
* Semua angka RSA (pub_e, pub_n, signature, blok cipher) berbentuk STRING.
====================================================================
"""

import json
import os
import threading

# --------------------------------------------------------------------
# Konfigurasi koneksi (jangan hardcode kredensial!)
# --------------------------------------------------------------------
try:  # python-dotenv opsional untuk pengembangan lokal
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

_mem_lock = threading.Lock()
_mem = {
    "users": {},        # id -> dict
    "messages": {},     # id -> dict
    "seq": {"users": 0, "messages": 0},
}


def using_postgres():
    """True bila terhubung ke PostgreSQL (Supabase)."""
    return bool(DATABASE_URL)


def _pg():
    """Buat koneksi psycopg2. Import dilakukan lazy agar mode in-memory
    tetap bisa dipakai tanpa psycopg2 terpasang."""
    import psycopg2
    return psycopg2.connect(DATABASE_URL)


# ====================================================================
# USERS  (id, name, role, pub_e, pub_n, created_at)
# ====================================================================
def create_user(name, role, pub_e, pub_n):
    """Simpan pengguna baru (sender | center) beserta PUBLIC KEY-nya.
    pub_e dan pub_n wajib berupa string."""
    if role not in ("sender", "center"):
        raise ValueError("role harus 'sender' atau 'center'")

    if using_postgres():
        sql = """
            INSERT INTO users (name, role, pub_e, pub_n)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, role, pub_e, pub_n, created_at
        """
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, (name, role, str(pub_e), str(pub_n)))
            row = cur.fetchone()
            conn.commit()
            return _row_to_user(row)

    with _mem_lock:
        _mem["seq"]["users"] += 1
        uid = _mem["seq"]["users"]
        user = {
            "id": uid, "name": name, "role": role,
            "pub_e": str(pub_e), "pub_n": str(pub_n),
            "created_at": _now_iso(),
        }
        _mem["users"][uid] = user
        return dict(user)


def get_users(role=None):
    """Daftar pengguna (opsional difilter per role), hanya berisi data publik."""
    if using_postgres():
        if role:
            sql = """
                SELECT id, name, role, pub_e, pub_n, created_at
                FROM users WHERE role = %s ORDER BY id
            """
            params = (role,)
        else:
            sql = """
                SELECT id, name, role, pub_e, pub_n, created_at
                FROM users ORDER BY id
            """
            params = ()
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            return [_row_to_user(r) for r in cur.fetchall()]

    with _mem_lock:
        users = [dict(u) for u in _mem["users"].values()]
    if role:
        users = [u for u in users if u["role"] == role]
    return sorted(users, key=lambda u: u["id"])


def get_user(user_id):
    """Ambil satu pengguna berdasarkan id (data publik saja)."""
    if using_postgres():
        sql = """
            SELECT id, name, role, pub_e, pub_n, created_at
            FROM users WHERE id = %s
        """
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, (int(user_id),))
            row = cur.fetchone()
            return _row_to_user(row) if row else None

    with _mem_lock:
        u = _mem["users"].get(int(user_id))
        return dict(u) if u else None


def _row_to_user(row):
    if row is None:
        return None
    return {
        "id": row[0], "name": row[1], "role": row[2],
        "pub_e": row[3], "pub_n": row[4],
        "created_at": row[5].isoformat() if row[5] else None,
    }


# ====================================================================
# SOS MESSAGES (id, sender_id, center_id, ciphertext, original_ciphertext,
#               signature, status, tampered, created_at)
# ====================================================================
def create_message(sender_id, center_id, ciphertext, original_ciphertext, signature):
    """Simpan paket SOS yang dikirim pengirim ke pusat darurat.
    ciphertext / original_ciphertext: list blok (semuanya string)."""
    cipher_json = json.dumps(list(ciphertext))
    orig_json = json.dumps(list(original_ciphertext))

    if using_postgres():
        sql = """
            INSERT INTO sos_messages
                (sender_id, center_id, ciphertext, original_ciphertext, signature)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
            RETURNING id, sender_id, center_id, ciphertext, original_ciphertext,
                      signature, status, tampered, created_at
        """
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, (int(sender_id), int(center_id),
                              cipher_json, orig_json, str(signature)))
            row = cur.fetchone()
            conn.commit()
            return _row_to_message(row)

    with _mem_lock:
        _mem["seq"]["messages"] += 1
        mid = _mem["seq"]["messages"]
        msg = {
            "id": mid, "sender_id": int(sender_id), "center_id": int(center_id),
            "ciphertext": [str(x) for x in ciphertext],
            "original_ciphertext": [str(x) for x in original_ciphertext],
            "signature": str(signature),
            "status": "pending", "tampered": False, "created_at": _now_iso(),
        }
        _mem["messages"][mid] = msg
        return dict(msg)


def get_message(msg_id):
    """Ambil satu pesan SOS berdasarkan id."""
    if using_postgres():
        sql = """
            SELECT id, sender_id, center_id, ciphertext, original_ciphertext,
                   signature, status, tampered, created_at
            FROM sos_messages WHERE id = %s
        """
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, (int(msg_id),))
            row = cur.fetchone()
            return _row_to_message(row) if row else None

    with _mem_lock:
        m = _mem["messages"].get(int(msg_id))
        return dict(m) if m else None


def list_messages(center_id=None):
    """Daftar pesan SOS (terbaru dulu) untuk satu pusat darurat."""
    if using_postgres():
        if center_id is not None:
            sql = """
                SELECT id, sender_id, center_id, ciphertext, original_ciphertext,
                       signature, status, tampered, created_at
                FROM sos_messages WHERE center_id = %s
                ORDER BY id DESC
            """
            params = (int(center_id),)
        else:
            sql = """
                SELECT id, sender_id, center_id, ciphertext, original_ciphertext,
                       signature, status, tampered, created_at
                FROM sos_messages ORDER BY id DESC
            """
            params = ()
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            return [_row_to_message(r) for r in cur.fetchall()]

    with _mem_lock:
        msgs = [dict(m) for m in _mem["messages"].values()]
    if center_id is not None:
        msgs = [m for m in msgs if m["center_id"] == int(center_id)]
    return sorted(msgs, key=lambda m: m["id"], reverse=True)


def update_message(msg_id, **fields):
    """Perbarui sebagian kolom pesan. Hanya kolom yang diizini:
    ciphertext, original_ciphertext, signature, status, tampered."""
    allowed = {"ciphertext", "original_ciphertext", "signature", "status", "tampered"}
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"Kolom tidak diizinkan: {unknown}")
    if not fields:
        return get_message(msg_id)

    sets, params = [], []
    for key, val in fields.items():
        if key in ("ciphertext", "original_ciphertext"):
            sets.append(f"{key} = %s::jsonb")
            params.append(json.dumps(list(val)))
        else:
            sets.append(f"{key} = %s")
            params.append(val)

    if using_postgres():
        params.append(int(msg_id))
        sql = f"""
            UPDATE sos_messages SET {', '.join(sets)}
            WHERE id = %s
            RETURNING id, sender_id, center_id, ciphertext, original_ciphertext,
                      signature, status, tampered, created_at
        """
        with _pg() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            conn.commit()
            return _row_to_message(row) if row else None

    with _mem_lock:
        msg = _mem["messages"].get(int(msg_id))
        if not msg:
            return None
        for key, val in fields.items():
            if key in ("ciphertext", "original_ciphertext"):
                msg[key] = [str(x) for x in val]
            else:
                msg[key] = val
        return dict(msg)


def _row_to_message(row):
    if row is None:
        return None
    return {
        "id": row[0], "sender_id": row[1], "center_id": row[2],
        "ciphertext": _json_loads(row[3]),
        "original_ciphertext": _json_loads(row[4]),
        "signature": row[5], "status": row[6], "tampered": bool(row[7]),
        "created_at": row[8].isoformat() if row[8] else None,
    }


def _json_loads(val):
    if isinstance(val, (list, dict)):
        return val
    return json.loads(val) if val else []


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def health():
    """Status koneksi database untuk endpoint /health."""
    if not using_postgres():
        return {"mode": "in-memory",
                "note": "DATABASE_URL belum di-set; data hilang saat server restart."}
    try:
        with _pg() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return {"mode": "postgresql", "ok": True}
    except Exception as exc:  # pragma: no cover
        return {"mode": "postgresql", "ok": False, "error": str(exc)}
