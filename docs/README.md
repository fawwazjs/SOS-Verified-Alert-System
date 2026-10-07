# Screenshot

Letakkan file screenshot di folder ini sesuai nama berikut agar link di `README.md`
menampilkan gambar:

| File | Isi screenshot |
|------|----------------|
| `01-landing.png` | Landing page `/` (3 kartu peran: Pengirim / Penyadap / Pusat Darurat + panduan demo) |
| `02-sender-keygen.png` | `/sender` Panel 1 — tabel EEA, public/private key |
| `03-sender-sign.png` | `/sender` Panel 2 — daftar ASCII, hash, tabel modPow signature |
| `04-sender-encrypt.png` | `/sender` Panel 3 — blok, tabel ciphertext, konfirmasi terkirim |
| `05-attacker-sadap-serang.png` | `/attacker` — daftar paket disadap (signature terlihat) + payload palsu terkirim |
| `06-center-inbox-decrypt.png` | `/center` — inbox database + hasil dekripsi + field + cek kadaluarsa |
| `07-center-valid.png` | `/center` Panel 5 — banner **SOS VALID** (5753 = 5753) |
| `08-center-invalid-tamper.png` | `/center` Panel 5 — banner **SOS TIDAK VALID** setelah diserang penyadap |
| `09-deploy.png` | Dashboard Render menampilkan deploy sukses / `GET /health` |

## Cara mengambil

1. Jalankan `python app.py`, buka `http://127.0.0.1:5000`.
2. Ikuti *Urutan Demo untuk Presentasi* di README (center → sender → inbox →
   verifikasi valid → **attacker serang** → verifikasi invalid → reset → valid).
3. Screenshot tiap tahap dengan nama di atas.
