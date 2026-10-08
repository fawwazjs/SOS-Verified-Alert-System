# SOS Verified Alert System

**Sistem Layanan Pesan Darurat dengan Verifikasi Lokasi dan Digital Signature Berbasis RSA**

Proyek **Mata Kuliah Kriptografi** — aplikasi web full-stack yang mengimplementasikan
**algoritma RSA dari nol (from scratch)** tanpa satu pun library kriptografi siap pakai.
Seluruh tahapan RSA (pembangkitan kunci, hashing, digital signature, enkripsi, dekripsi,
verifikasi) ditampilkan **langkah demi langkah** di UI.

**Kriptografi (B)**<br>
**Anggota Kelompok:**<br>
**Kelompok 11**
| Nama | NRP |
|------|-----|
| Ahmad Wildan Fawwaz | 5027241001 |
| Dimas Satya Andhika | 4027241032 |
| Daniswara Fausta Novanto | 5027241050 |

---

## Latar Belakang

Laporan darurat (SOS) sering bermasalah: banyak **hoax**, isi pesan bisa
**dimanipulasi** di tengah jalan, dan **identitas/lokasi pengirim** tidak jelas.

**Solusi:**
1. Pengirim **menandatangani** payload dengan *private key*-nya (digital signature RSA).
2. Payload dienkripsi dengan *public key* **Pusat Darurat**.
3. Pusat Darurat mendekripsi, lalu **memverifikasi** signature dengan *public key* pengirim.
4. Perubahan 1 karakter pun membuat hash tidak cocok → sistem menandai
   **SOS TIDAK VALID / kemungkinan hoax**.

---

## Konsep RSA yang Diimplementasikan

### 1. Key Generation
```
n = p × q
phi(n) = (p − 1)(q − 1)
e   dengan 1 < e < phi(n) dan gcd(e, phi(n)) = 1
d   = invers e mod phi(n)   (Extended Euclidean)
Public Key = (e, n)   ·   Private Key = (d, n)
```

### 2. Enkripsi & Dekripsi
```
cipher = blok^e mod n     (public key penerima)
blok   = cipher^d mod n   (private key penerima)
```
Sebelum dienkripsi, payload dipecah jadi blok: setiap karakter jadi **3 digit ASCII**
(`'A'` → `065`), beberapa karakter digabung jadi satu blok. Ukuran blok dihitung
otomatis agar **nilai blok selalu < n**.

### 3. Digital Signature & Verifikasi
```
hash           = (jumlah ASCII payload) mod 10000
signature      = hash^d mod n                     (private key PENGIRIM)
verifiedHash   = signature^e mod n                (public key PENGIRIM)
recomputedHash = (jumlah ASCII payload hasil dekripsi) mod 10000
valid          = verifiedHash == recomputedHash
```

### 4. Modular Exponentiation
Semua pangkat modular memakai **square-and-multiply manual** (biner eksponen) —
`pow(a, b, n)` bawaan bahasa **tidak dipakai**.

---

## Struktur Folder

```
SOS-Verified-Alert-System/
├── rsa.py            # RSA murni dari nol (tanpa import Flask/DB sama sekali)
├── db.py             # Koneksi & query (psycopg2, parameterized) + fallback in-memory
├── app.py            # Routing Flask (endpoint REST + halaman)
├── schema.sql        # Skema tabel Supabase PostgreSQL
├── test_e2e.py       # Uji end-to-end otomatis (79 kasus)
├── requirements.txt  # Flask, psycopg2-binary, gunicorn, python-dotenv
├── .env.example      # Template environment variable (TANPA kredensial)
├── Procfile          # Perintah production: gunicorn app:app
├── README.md
├── docs/             # Dokumentasi tambahan (lihat docs/README.md)
├── picture/          # Screenshot dokumentasi alur demo (lihat bagian Screenshot)
├── templates/
│   ├── index.html    # Landing (pilih peran)
│   ├── sender.html   # Halaman Pengirim    → route /sender
│   ├── attacker.html # Halaman Penyadap    → route /attacker
│   └── center.html   # Halaman Pusat Darurat → route /center
└── static/
    ├── style.css     # Tema dark mode merah/oranye, responsif
    ├── common.js     # Utilitas UI + render log keygen (bersama)
    ├── sender.js     # Alur pengirim: keygen → sign → encrypt → send
    ├── attacker.js   # Alur penyadap: sadap → payload palsu → serang/reset
    └── center.js     # Alur pusat: keygen → inbox → decrypt → verify
```

### Penjelasan Singkat Tiap File

| File | Fungsi |
|------|--------|
| `rsa.py` | Seluruh algoritma RSA manual + *log langkah* untuk UI. Tidak mengimpor Flask maupun database. |
| `db.py` | Koneksi `DATABASE_URL` (Supabase Session Pooler), query **parameterized**, tabel `users` & `sos_messages`. Tanpa `DATABASE_URL` → mode in-memory (demo lokal tanpa DB). |
| `app.py` | Routing saja: validasi input, memanggil `rsa.py` & `db.py`, serialisasi angka ke **string**. |
| `schema.sql` | Definisi tabel untuk SQL Editor Supabase. |
| `sender.js` / `attacker.js` / `center.js` | Logika tiap peran; private key dibaca dari `localStorage`, dikirim per request, tidak pernah disimpan server. |
| `test_e2e.py` | 79 uji otomatis: halaman, keygen, validasi, sign/encrypt/send, inbox, decrypt/verify, serangan penyadap, reset. |

---

## Pembagian Kerja

| Tanggung Jawab | Penanggung Jawab |
|----------------|------------------|
| **Backend & DevOps** — rancangan arsitektur 3 lapis, `db.py`, `schema.sql`, seluruh endpoint REST, validasi input, `.env.example`, `Procfile`, deployment Supabase + Render, penanganan *cold start* | **Dimas Satya Andhika** (4027241032) |
| **Kriptografi & Pengujian** — `rsa.py` seluruh algoritma dari nol (prima, gcd, EEA, modInverse, modPow, blok, hash, sign, verify) lengkap dengan log langkah, skema encoding blok, `test_e2e.py` (79 kasus), analisis skenario serangan | **Ahmad Wildan Fawwaz** (5027241001) |
| **Frontend & Demo** — halaman Pengirim/Penyadap/Pusat Darurat terpisah, landing page, `style.css` dark theme, `common.js`/`sender.js`/`attacker.js`/`center.js`, visualisasi tabel langkah + stepper, geolocation, alur serangan MITM, skenario demo | **Daniswara Fausta Novanto** (5027241050) |

---

## Tahapan Build (dari 0 sampai jadi)

| # | Tahap | Isi Pekerjaan | Penanggung Jawab |
|---|-------|---------------|------------------|
| 0 | **Setup environment** | Install Python 3.13 + venv, `pip install flask`, inisialisasi git, `.gitignore`, susun struktur folder (`rsa/db/app`, `templates/`, `static/`) | Semua |
| 1 | **Analisis & desain** | Studi kasus, format payload `nama\|lat\|lon\|waktu\|pesan`, diagram alur tanda tangan + enkripsi, daftar fungsi wajib, aturan larangan library kriptografi, desain UI 5 panel + stepper | Ahmad & Dimas |
| 2 | **RSA dari nol (`rsa.py`)** | `is_prime`, `gcd`, `extended_euclidean` (tabel Bezout), `mod_inverse`, `generate_key`, `mod_pow` (square-and-multiply + tabel iterasi), `text_to_blocks`/`blocks_to_text` (ASCII 3 digit, ukuran blok otomatis), `encrypt`, `decrypt`, `hash_message`, `sign_message`, `verify_signature` — semua mengembalikan *log langkah*. Uji manual: ditemukan parameter demo (pengirim 1009×1013/e17, pusat 31627×31649/e13) | Dimas |
| 3 | **Backend MVP + UI 5 panel** | `app.py` versi awal (state in-memory), `index.html` 5 panel, `app.js` render tabel langkah, geolocation, tombol serangan. Uji pertama: skenario valid & manipulasi dinyatakan berfungsi | Daniswara & Ahmad |
| 4 | **Refaktorisasi arsitektur** | Pisahkan `rsa.py` (murni) / `db.py` (koneksi & query parameterized) / `app.py` (routing), tulis `schema.sql`, semua angka RSA dikirim & disimpan sebagai **string**, private key **tidak lagi** di server → hanya `localStorage` browser | Ahmad |
| 5 | **Halaman peran terpisah** | `/sender`, `/center`, dan landing `/` dipisah + `common.js`/`sender.js`/`center.js`, registrasi `users` (public key saja), inbox Pusat Darurat dimuat dari **database** | Daniswara |
| 6 | **Halaman Penyadap + kadaluwarsa** | `/attacker` sebagai pihak ketiga MITM (sadap paket → payload palsu → serang/reset), `ciphertext` vs `original_ciphertext` di tabel pesan → endpoint tamper/reset; cek alert kedaluwarsa > 5 menit; status `pending/valid/invalid` tersimpan | Ahmad & Daniswara |
| 7 | **Pengujian menyeluruh** | `test_e2e.py` — 79 kasus lulus (validasi input salah, alur normal, serangan penyadap, manipulasi lokasi, reset, kompatibilitas gaya lama). Scan repo: tidak ada `hashlib/secrets/crypto/cryptography` | Dimas |
| 8 | **Dokumentasi & deploy** | README lengkap, `.env.example`, `Procfile`, panduan Supabase + Render, catatan geolocation & *cold start* | Ahmad & Daniswara |

---

## Arsitektur Backend & Deploy

```
┌────────────────────────────────────────────────────────────────────────┐
│  BROWSER (satu origin, tiga tab peran)                                 │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────────────┐   │
│  │ /sender      │  │ /attacker       │  │ /center                  │   │
│  │ keygen → sign│  │ sadap → payload │  │ inbox → decrypt → verify │   │
│  │ → encrypt    │  │ palsu → serang  │  │ (murni penanggapan)      │   │
│  └──────┬───────┘  └────────┬────────┘  └────────────┬─────────────┘   │
│   localStorage: private  TANPA private   localStorage: private key     │
│   key pengirim           key apa pun     pusat                          │
│   (TIDAK pernah ke database)                                            │
└───────────────┬───────────────────┬───────────────────┬────────────────┘
                │  JSON (angka RSA = STRING)            │
                ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│  RENDER (Python)  —  gunicorn app:app                                  │
│  app.py (routing) ──▶ rsa.py (RSA from scratch, murni)                 │
│        │                                                               │
│        └──────────▶ db.py (psycopg2, query parameterized)              │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ DATABASE_URL (Session Pooler)
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│  SUPABASE PostgreSQL                                                   │
│  users(id, name, role, pub_e, pub_n, created_at)                       │
│  sos_messages(id, sender_id, center_id, ciphertext JSONB,              │
│               original_ciphertext JSONB, signature, status,            │
│               tampered, created_at)                                    │
└────────────────────────────────────────────────────────────────────────┘
```

**Prinsip penting:**

- **Backend: Flask** → deploy ke **Render** dengan `gunicorn app:app`.
- **Database: Supabase PostgreSQL**, diakses lewat `psycopg2` memakai `DATABASE_URL`
  dari **environment variable** (Session Pooler). **Tidak ada kredensial yang di-hardcode.**
- **Pemisahan file:** `rsa.py` (murni RSA, tanpa import Flask/DB) ·
  `db.py` (koneksi & query, **parameterized**) · `app.py` (routing) · `schema.sql`.
- **Semua angka RSA disimpan & dikirim sebagai STRING** (`pub_e`, `pub_n`, `d`,
  `signature`, blok `ciphertext`) agar JavaScript tidak kehilangan presisi
  (aman terhadap batas `Number` 2^53).
- **PRIVATE KEY tidak pernah disimpan di database atau log.** Private key hanya ada di
  `localStorage` browser, dikirim sekali per request (`/api/sign`, `/api/inbox/*/decrypt`),
  dipakai, lalu dibuang oleh server.
- **Tiga halaman peran dipisah** — `/sender` (pengirim), `/attacker` (penyadap/MITM),
  `/center` (pusat darurat) — supaya demo tiga peran terlihat nyata.
  Pusat darurat **murni sebagai penanggap** (tanpa tombol serangan); penyadap tidak
  punya private key apa pun. Inbox pusat dimuat dari database.
- **Larangan crypto tetap berlaku:** tanpa `hashlib`, `secrets`, `crypto`,
  `cryptography`, dll. `psycopg2` **hanya driver database** — diizinkan.

### Daftar Endpoint

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/` | Landing page (pilih peran) |
| GET | `/sender` | Halaman Pengirim |
| GET | `/attacker` | Halaman Penyadap (man-in-the-middle) |
| GET | `/center` | Halaman Pusat Darurat |
| GET | `/health` | Status aplikasi + koneksi database |
| POST | `/api/keygen` | Pembangkitan kunci `{p,q,e}` → public/private + log |
| POST | `/api/users` | Daftarkan user + **public key** saja |
| GET | `/api/users?role=` | Daftar user (data publik) |
| POST | `/api/sign` | Hash + signature `{payload, private}` |
| POST | `/api/encrypt` | Enkripsi `{text, e, n}` → daftar blok cipher |
| POST | `/api/send` | Simpan paket SOS (`ciphertext`, `original_ciphertext`, `signature`) |
| GET | `/api/inbox?center_id=` | Inbox pusat darurat · **tanpa `center_id`** → semua paket (untuk disadap) |
| POST | `/api/inbox/<id>/decrypt` | Dekripsi dengan private key pusat |
| POST | `/api/inbox/<id>/verify` | Verifikasi signature → simpan status |
| POST | `/api/inbox/<id>/tamper` | Penyadap mengganti isi: `{payload: {nama,lat,lon,waktu,pesan}}` (atau gaya lama `mode`+`plaintext`) |
| POST | `/api/inbox/<id>/reset` | Kembalikan ciphertext ke `original_ciphertext` |

### Struktur Tabel

```sql
users(id, name, role[sender|center], pub_e, pub_n, created_at)
sos_messages(id, sender_id, center_id, ciphertext JSONB,
             original_ciphertext JSONB, signature,
             status[pending|valid|invalid], tampered, created_at)
```

---

## Cara Menjalankan (Lokal)

```bash
python -m venv venv
venv\Scripts\activate            # Windows: source venv/bin/activate
pip install -r requirements.txt

python app.py                    # buka http://127.0.0.1:5000
python test_e2e.py               # uji 79 kasus (server harus hidup)
```

**Mode database:**

- **Tanpa `DATABASE_URL`** → otomatis mode **in-memory** (cocok untuk latihan/UI;
  data hilang saat server berhenti). Cek lewat `GET /health`.
- **Dengan `DATABASE_URL`** → terhubung ke Supabase PostgreSQL.
  Salin `.env.example` menjadi `.env` lalu isi nilainya (file `.env` sudah
  masuk `.gitignore`).

> **Catatan geolocation:** tombol "Ambil Lokasi Saya" memakai
> `navigator.geolocation.getCurrentPosition`, yang hanya diizinkan browser pada origin
> aman: **`http://localhost` / `127.0.0.1`** atau **`https://`**. Jalankan lokal lewat
> `http://127.0.0.1:5000`. Jika izin ditolak, tersedia **input manual** lat/lon.

---

## Langkah Deploy

### A. Supabase (database)

1. Buka [supabase.com](https://supabase.com) → **New project** → beri nama
   (mis. `sos-verified-alert`), pilih region terdekat (mis. *Singapore*), simpan
   **database password**.
2. Tunggu provisioning selesai, lalu buka **SQL Editor** → **New query** →
   paste **seluruh isi `schema.sql`** → **Run**. Pesan `Success. No rows returned`
   berarti tabel `users` & `sos_messages` sudah jadi.
3. Buka **Settings → Database → Connection string** → tab **Session pooler**
   → pilih **URI** → salin connection string-nya.
   - Gunakan **Session pooler (port 6543)**, bukan *Direct connection* (port 5432):
     pooler mendukung koneksi IPv4 dan pooling — persis yang dibutuhkan Render.
   - Formatnya kira-kira:
     `postgresql://postgres.XXXX:[PASSWORD]@aws-0-xx-xx.pooler.supabase.com:6543/postgres?sslmode=require`
4. **Jangan commit connection string ini.** Simpan sebagai nilai `DATABASE_URL`.

### B. Render (aplikasi)

1. Push repo ke **GitHub**.
2. Buka [render.com](https://render.com) → **New → Web Service** → hubungkan repo.
3. Isi:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
     (Render juga otomatis mendeteksi `Procfile` yang berisi `web: gunicorn app:app`)
4. Di tab **Environment** tambahkan *secret*:
   - `DATABASE_URL` = connection string Session pooler Supabase (step A.3)
   - `FLASK_DEBUG` = `0`
5. **Create Web Service** → tunggu build & deploy → buka
   `https://<nama-service>.onrender.com/health` untuk memastikan
   `"database": {"mode": "postgresql", "ok": true}`.

### C. Catatan *Cold Start* Render

- Pada **free tier**, Render mematikan service setelah ~15 menit tanpa akses.
  Request pertama setelah idle biasanya butuh **30–60 detik** (fase *Provisioning/Spin
  Up*) — ini **normal**, bukan error. Cukup tunggu, halaman akan termuat.
- Data tidak pernah hilang oleh *cold start* karena tersimpan di Supabase
  (berbeda dengan mode in-memory). Private key juga aman di `localStorage` browser.
- Setelah *idle* pertama, service kembali normal untuk sesi berikutnya.

### D. Setelah Deploy

Login bukan diperlukan untuk demo: buka **`/center`** → *Generate & Daftarkan* kunci
pusat, lalu buka **`/sender`** → *Generate Keys* → isi form → *Generate Signature*
→ *Encrypt & Send* → kembali ke `/center` → *Muat Inbox* → pilih pesan →
*Verifikasi Signature* (**✓ SOS VALID**) → buka **`/attacker`** → *Muat Paket
Disadap* → *Serang* → kembali ke `/center` → *Verifikasi* lagi
(**✗ SOS TIDAK VALID**) → `/attacker` → *Reset* → *Verifikasi* (**✓ VALID**
kembali).

---

## Alur Sistem (End-to-End)

```
[Halaman /sender]          [Halaman /attacker]         [Halaman /center]
 Panel 1 Keygen pengirim    1 Muat paket disadap        Panel 1 Keygen pusat
      │                     (ciphertext+signature        │ (public key → DB)
 Panel 2 Payload → HASH      terbuka, isi tertutup)      │
      │   → SIGN (priv pengirim)       │                 │
 Panel 3 Enkripsi (pub pusat)          │                 │
      │                                │                 │
      └── paket ──── INSERT ──▶ sos_messages ◀── sadap ──┘
                                    │        2 Serang: payload palsu
                                    │           (enkripsi pub pusat +
                                    │            signature lama)
                          GET /api/inbox (dari database)
                                    │
                    DEKRIPSI (priv pusat) → VERIFIKASI (pub pengirim)
                                    │
                        UPDATE status: valid / invalid
```

**Peta ke panel tampilan:**

| Halaman | Panel | Kunci yang Dipakai |
|---------|-------|--------------------|
| `/sender` | 1 Key Generation | Pasangan kunci pengirim |
| `/sender` | 2 Sender SOS | Hash + signature: **private key pengirim** |
| `/sender` | 3 Encryption Process | Enkripsi: **public key pusat darurat** |
| `/attacker` | 1 Paket Disadap | **Tanpa kunci** — hanya melihat metadata terbuka |
| `/attacker` | 2 Susun & Serang | Enkripsi ulang: **public key pusat** + signature lama |
| `/center` | 1 Key Generation | Pasangan kunci pusat |
| `/center` | 4 Emergency Center | Inbox DB + dekripsi: **private key pusat** |
| `/center` | 5 Verification Result | Verifikasi: **public key pengirim** (dari DB) |

---

## Fitur Simulasi Serangan (Halaman Penyadap `/attacker`)

Serangan ditampilkan dari sudut pandang **pihak ketiga MITM** — bukan pusat darurat —
karena pusat darurat adalah pihak yang dirugikan. Penyerang **tidak punya private key
apa pun**:

| Aksi di `/attacker` | Mekanisme |
|---------------------|-----------|
| **Muat Paket Disadap** | Melihat metadata paket di jalan: id, pengirim, ukuran, **signature** (terbuka) — tetapi **tidak bisa membaca isi** (butuh private key pusat) |
| **Serang — Ganti Isi Paket** | Menyusun **payload palsu** sendiri (nama/lokasi/waktu/pesan bebas) → dienkripsi dengan **public key pusat** (terbuka) → **signature lama ditempel apa adanya** |
| **Reset ke Paket Asli** | `ciphertext` dipulihkan dari `original_ciphertext` |

Setelah serangan, buka `/center` → *Muat Inbox* → *Verifikasi Signature*:

> **✗ SOS TIDAK VALID — SIGNATURE TIDAK VALID**
> `verifiedHash` tetap hash pesan asli (`5753`) sedangkan hash ulang isi palsu
> berbeda (mis. `7015`) → status `invalid` + flag `tampered` **tersimpan di database**.

Setelah *Reset* → verifikasi ulang → **✓ SOS VALID kembali**. Ini membuktikan dua hal:
**RSA menjaga kerahasiaan** (penyerang tak bisa baca) dan **integritas**
(penyerang tak bisa ganti isi tanpa ketahuan).

---

## Daftar Fungsi RSA Manual (`rsa.py`)

| Fungsi (Python) | Nama di Spesifikasi | Keterangan |
|-----------------|---------------------|------------|
| `is_prime(n)` | `isPrime(n)` | Trial division sampai √n |
| `gcd(a, b)` | `gcd(a, b)` | Algoritma Euclid + log langkah |
| `extended_euclidean(a, b)` | `extendedEuclidean(a, b)` | Koefisien Bezout + tabel iterasi |
| `mod_inverse(e, phi)` | `modInverse(e, phi)` | `e⁻¹ mod phi` via EEA |
| `generate_key(p, q, e)` | `generateKey(p, q, e)` | Validasi + seluruh log tahapan |
| `mod_pow(base, exp, mod)` | `modPow(base, exp, mod)` | Square-and-multiply manual + tabel |
| `text_to_blocks(text, n)` | `textToBlocks(text, n)` | ASCII 3 digit → blok `< n` |
| `blocks_to_text(blocks, n)` | `blocksToText(blocks, n)` | Blok → teks kembali |
| `encrypt(text, e, n)` | `encrypt(text, e, n)` | `blok^e mod n` per blok |
| `decrypt(blocks, d, n)` | `decrypt(blocks, d, n)` | `cipher^d mod n` per blok |
| `hash_message(text)` | `hashMessage(text)` | `Σ ASCII mod 10000` |
| `sign_message(text, d, n)` | `signMessage(text, d, n)` | `hash^d mod n` |
| `verify_signature(text, sig, e, n)` | `verifySignature(...)` | `sig^e mod n` vs hash ulang |

---

## Skenario Demo Siap Pakai (Sudah Teruji — 79/79 test lulus)

### Kunci Pengirim (`/sender` → Isi Contoh)

| Parameter | Nilai |
|-----------|-------|
| p / q / e | **1009 / 1013 / 17** |
| n | 1.022.117 |
| phi(n) | 1.020.096 |
| **d** | **180.017** |

### Kunci Pusat Darurat (`/center` → Isi Contoh)

| Parameter | Nilai |
|-----------|-------|
| p / q / e | **31627 / 31649 / 13** |
| n | 1.000.962.923 |
| phi(n) | 1.000.899.648 |
| **d** | **615.938.245** |

### Data Darurat

```
Fwxz|-7.275847|112.794702|2026-10-07 13:20:15|Terjadi kecelakaan lalu lintas
```

### Hasil Terverifikasi

| Tahap | Hasil |
|-------|-------|
| Hash payload | `5753` |
| Signature (hash^d mod n pengirim) | `118799` |
| Blok ciphertext | 26 blok (3 karakter/blok, digit stream awal `070119120`) |
| Dekripsi | identik dengan payload asli |
| **Verifikasi normal** | **✓ SOS VALID** — `5753 = 5753`, status `valid` |
| **Penyadap: ganti isi (default form — lokasi diganti)** | **✗ TIDAK VALID** — `5753 ≠ 6990`, status `invalid` + `tampered` |
| **Penyadap: ganti pesan saja (lokasi dipertahankan)** | **✗ TIDAK VALID** — `5753 ≠ 7015`, status `invalid` |
| **Setelah Reset** | **✓ SOS VALID** kembali |

> Nilai hash isi palsu bergantung pada payload yang diketik penyadap; angka `6990`/`7015`
> sesuai nilai bawaan form dan 79 test otomatis.

### Urutan Demo untuk Presentasi (± 6 menit)

1. `/center` → **Generate & Daftarkan** kunci pusat (perhatikan tabel EEA & `d`).
2. `/sender` → **Generate Keys** kunci pengirim → pilih pusat di dropdown →
   isi form (atau *Ambil Lokasi Saya*) → **Generate Signature**
   (lihat daftar ASCII, hash, tabel square-and-multiply).
3. **Encrypt & Send** → lihat pembentukan blok + tabel ciphertext + "Paket terkirim".
4. `/center` → **Muat Inbox** → klik baris pesan → dekripsi tampil
   (tabel blok, field, cek kadaluarsa) → **Verifikasi Signature** →
   banner **✓ SOS VALID** (5753 = 5753).
5. `/attacker` → **Muat Paket Disadap** → klik baris (signature terlihat, isi tertutup)
   → **Serang — Ganti Isi Paket** (payload palsu terisi otomatis) →
   penjelasan mengapa serangan tetap akan ketahuan.
6. Kembali `/center` → **Muat Inbox** → klik paket (label *DITAMPER*) →
   **Verifikasi** → **✗ SOS TIDAK VALID** (5753 ≠ 6990).
7. `/attacker` → **Reset** → `/center` → verifikasi lagi → **✓ SOS VALID**.

> Agar status kedaluwarsa "masih berlaku", biarkan timestamp default (terisi otomatis
> saat halaman dibuka) atau edit ke waktu sekarang.

---

## Kepatuhan (Tanpa Library Kriptografi)

Proyek ini **TIDAK** memakai: `crypto`, `cryptography`, `pycryptodome`, OpenSSL,
`java.security`, `node-rsa`, `forge`, `crypto-js`, `hashlib`, `secrets`, maupun
library signature lain — **berlaku untuk kode frontend maupun backend**.

Ditulis manual di `rsa.py`:
- pengecekan bilangan prima · `gcd` · Extended Euclidean · modular inverse
- pembangkitan public/private key · modular exponentiation (square-and-multiply,
  tanpa `pow(a,b,n)`) · enkripsi & dekripsi · hash sederhana · signature & verifikasi

**Flask** hanya untuk routing/serving · **psycopg2** hanya driver database ·
frontend memakai **HTML + CSS + JavaScript murni**.

---

## Screenshot

> Dokumentasi tangkapan layar alur demo end-to-end. Berkas gambar tersimpan di folder
> [`picture/`](picture/).

### 1. Landing Page
![Landing Page](picture/SOS_LandingPage.png)

### 2. Halaman Pengirim

#### 2.1 Generate Keys
![Generate Keys](picture/SOS_Pengirim_KeyGeneration.png)

#### 2.2 Keys Berhasil Dibuat
![Keys Berhasil](picture/SOS_Pengirim_KeyGenerationSuccess.png)

#### 2.3 Formulir Pesan SOS
![Formulir SOS](picture/SOS_Pengirim_SenderSOS.png)

#### 2.4 Proses Enkripsi
![Proses Enkripsi](picture/SOS_Pengirim_EncryptProcess.png)

#### 2.5 Enkripsi & Kirim
![Encrypt & Send](picture/SOS_Pengirim_EncryptnSend.png)

![Encrypt & Send — Terkirim](picture/SOS_Pengirim_EncryptnSend2.png)

### 3. Halaman Penyadap (Man-in-the-Middle)

#### 3.1 Muat Paket yang Disadap
![Muat Paket Disadap](picture/SOS_Penyadap_PaketPenyadap.png)

#### 3.2 Paket Berhasil Disadap
![Paket Disadap Sukses](picture/SOS_Penyadap_PaketPenyadapSucess.png)

#### 3.3 Susun Payload Palsu & Serang
![Payload Palsu](picture/SOS_Penyadap_PayloadPalsu.png)

### 4. Halaman Pusat Darurat

#### 4.1 Generate & Daftarkan Kunci
![Keygen Pusat Darurat](picture/SOS_PusatDarurat_KeyGeneration.png)

#### 4.2 Verifikasi — SOS VALID
![SOS Valid](picture/SOS_PusatDarurat_SOSValid.png)

#### 4.3 Terdeteksi Serangan (Terkena Serangan)
![Terserang](picture/SOS_PusatDarurat_Terserang.png)

#### 4.4 Verifikasi — SOS TIDAK VALID
![SOS Tidak Valid](picture/SOS_PusatDarurat_SOSTidakValid.png)

#### 4.5 Setelah Reset — SOS Kembali VALID
![Tidak Terserang](picture/SOS_PusatDarurat_TidakTerserang.png)

---

## Teknologi

| Lapisan | Teknologi |
|---------|-----------|
| Backend | Python 3 + Flask (routing) · gunicorn (production) |
| Kriptografi | RSA **from scratch** (`rsa.py`, tanpa library) |
| Database | Supabase PostgreSQL · `psycopg2` (parameterized) |
| Frontend | HTML5 + CSS3 (dark theme) + JavaScript murni (fetch, geolocation, localStorage) |
| Deploy | Render (Web Service) + Supabase (Session Pooler) |

