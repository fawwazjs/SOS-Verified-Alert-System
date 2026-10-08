# Screenshot

Tangkapan layar dokumentasi alur demo tersimpan di folder **[`../picture/`](../picture/)**
(direferensikan dari bagian **Screenshot** di `README.md`).

## Daftar file

| File | Isi screenshot |
|------|----------------|
| `SOS_LandingPage.png` | Landing page `/` (kartu peran: Pengirim / Penyadap / Pusat Darurat + panduan demo) |
| `SOS_Pengirim_KeyGeneration.png` | `/sender` — formulir pembangkitan kunci (p, q, e) |
| `SOS_Pengirim_KeyGenerationSuccess.png` | `/sender` — tabel EEA & public/private key berhasil dibuat |
| `SOS_Pengirim_SenderSOS.png` | `/sender` — formulir pesan SOS (nama, waktu, pesan, GPS) |
| `SOS_Pengirim_EncryptProcess.png` | `/sender` — daftar ASCII, hash & tabel modPow signature |
| `SOS_Pengirim_EncryptnSend.png` | `/sender` — blok & tabel ciphertext sebelum dikirim |
| `SOS_Pengirim_EncryptnSend2.png` | `/sender` — konfirmasi paket terkirim ke pusat darurat |
| `SOS_Penyadap_PaketPenyadap.png` | `/attacker` — daftar paket disadap (signature terlihat, isi tersembunyi) |
| `SOS_Penyadap_PaketPenyadapSucess.png` | `/attacker` — paket berhasil dimuat & dipilih |
| `SOS_Penyadap_PayloadPalsu.png` | `/attacker` — payload palsu disusun lalu dikirim (serangan) |
| `SOS_PusatDarurat_KeyGeneration.png` | `/center` — pembangkitan & registrasi public key pusat ke database |
| `SOS_PusatDarurat_SOSValid.png` | `/center` — banner **SOS VALID** (hash cocok) |
| `SOS_PusatDarurat_Terserang.png` | `/center` — pesan terdeteksi telah dimanipulasi penyadap |
| `SOS_PusatDarurat_SOSTidakValid.png` | `/center` — banner **SOS TIDAK VALID** setelah diserang |
| `SOS_PusatDarurat_TidakTerserang.png` | `/center` — setelah reset, verifikasi kembali **SOS VALID** |

## Cara mengambil

1. Jalankan `python app.py`, buka `http://127.0.0.1:5000`.
2. Ikuti *Urutan Demo untuk Presentasi* di README (center → sender → inbox →
   verifikasi valid → **attacker serang** → verifikasi invalid → reset → valid).
3. Simpan screenshot ke folder `picture/` dengan nama seperti daftar di atas,
   lalu pastikan direferensikan di bagian **Screenshot** pada `README.md`.
