# -*- coding: utf-8 -*-
"""
gen_laporan.py
===================================================================
Pembangkit LAPORAN LENGKAP (DOCX) proyek SOS Verified Alert System.

Menghasilkan: Laporan_SOS_Verified_Alert_System.docx

Menjalankan:  venv\\Scripts\\python.exe gen_laporan.py
Butuh        : pip install python-docx
===================================================================
"""

import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
PIC = os.path.join(HERE, "picture")
OUT = os.path.join(HERE, "Laporan_SOS_Verified_Alert_System.docx")

ACCENT = RGBColor(0x00, 0x00, 0xCC)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x55, 0x55, 0x55)

doc = Document()

# --------------------------------------------------------------------
# Gaya dasar
# --------------------------------------------------------------------
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")


def _set_cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def h1(text):
    p = doc.add_heading(text, level=1)
    for r in p.runs:
        r.font.color.rgb = ACCENT
    return p


def h2(text):
    p = doc.add_heading(text, level=2)
    for r in p.runs:
        r.font.color.rgb = DARK
    return p


def h3(text):
    p = doc.add_heading(text, level=3)
    for r in p.runs:
        r.font.color.rgb = DARK
    return p


def para(text="", bold=False, italic=False, size=None, color=None, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    if align:
        p.alignment = align
    return p


def bullet(text, level=0):
    p = doc.add_paragraph(text, style="List Bullet")
    if level:
        p.paragraph_format.left_indent = Cm(1.9 + 0.6 * level)
    return p


def numbered(text):
    return doc.add_paragraph(text, style="List Number")


def code_block(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F2F2F2")
    pPr.append(shd)
    return p


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htxt in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(htxt)
        r.bold = True
        r.font.size = Pt(10)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val))
            r.font.size = Pt(9.5)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = MUTED
    return p


def add_image(fname, width_cm=15.5, cap=None):
    path = os.path.join(PIC, fname)
    if not os.path.exists(path):
        return
    doc.add_picture(path, width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if cap:
        caption(cap)


# ====================================================================
# HALAMAN JUDUL
# ====================================================================
for _ in range(3):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("LAPORAN PROYEK")
r.bold = True
r.font.size = Pt(16)
r.font.color.rgb = MUTED

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("SOS VERIFIED ALERT SYSTEM")
r.bold = True
r.font.size = Pt(30)
r.font.color.rgb = ACCENT

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Sistem Layanan Pesan Darurat dengan Verifikasi Lokasi dan\n"
              "Digital Signature Berbasis RSA (From Scratch)")
r.italic = True
r.font.size = Pt(14)
r.font.color.rgb = DARK

doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Proyek ETS Mata Kuliah Kriptografi")
r.bold = True
r.font.size = Pt(12)

for _ in range(4):
    doc.add_paragraph()

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Disusun oleh:")
r.bold = True
r.font.size = Pt(12)

table(
    ["Nama", "NRP", "Peran Utama"],
    [
        ["Ahmad Wildan Fawwaz", "5027241001", "Kriptografi & Pengujian"],
        ["Dimas Satya Andhika", "4027241032", "Backend & DevOps"],
        ["Daniswara Fausta Novanto", "5027241050", "Frontend & Demo"],
    ],
    widths=[6.5, 3.5, 6.0],
)

para("Tahun Akademik 2025/2026", align=WD_ALIGN_PARAGRAPH.CENTER, color=MUTED)

doc.add_page_break()

# ====================================================================
# DAFTAR ISI (manual)
# ====================================================================
h1("Daftar Isi")
toc_items = [
    "BAB 1  Pendahuluan",
    "BAB 2  Landasan Teori",
    "BAB 3  Analisis & Perancangan Sistem",
    "BAB 4  Implementasi Kriptografi (rsa.py)",
    "BAB 5  Implementasi Backend",
    "BAB 6  Implementasi Database",
    "BAB 7  Implementasi Frontend (UI/UX)",
    "BAB 8  Alur Sistem End-to-End",
    "BAB 9  Fitur Simulasi Serangan (Man-in-the-Middle)",
    "BAB 10 Pengujian (Test End-to-End)",
    "BAB 11 Dokumentasi Screenshot",
    "BAB 12 Panduan Menjalankan & Deployment",
    "BAB 13 Kepatuhan Tanpa Library Kriptografi",
    "BAB 14 Pembagian Kerja & Tahapan Build",
    "BAB 15 Kesimpulan & Saran",
]
for it in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.add_run(it).font.size = Pt(11)

doc.add_page_break()

# ====================================================================
# BAB 1 - PENDAHULUAN
# ====================================================================
h1("BAB 1  Pendahuluan")

h2("1.1  Latar Belakang")
para(
    "Layanan darurat (SOS) pada kenyataannya menghadapi tiga masalah utama. "
    "Pertama, maraknya laporan palsu (hoaks) yang membuang sumber daya penanganan. "
    "Kedua, isi pesan maupun koordinat lokasi dapat dimanipulasi di tengah jalur "
    "transmisi oleh pihak ketiga (man-in-the-middle). Ketiga, tidak adanya jaminan "
    "identitas dan keaslian data, sehingga pusat darurat tidak dapat memastikan siapa "
    "yang benar-benar mengirim laporan dan apakah datanya utuh."
)
para(
    "SOS Verified Alert System dibangun untuk menjawab ketiga masalah tersebut dengan "
    "menerapkan digital signature dan enkripsi RSA. Keunikan proyek ini adalah seluruh "
    "algoritma RSA ditulis dari nol (from scratch) tanpa satu pun library kriptografi "
    "siap pakai, baik di sisi backend maupun frontend."
)

h2("1.2  Rumusan Masalah")
bullet("Bagaimana mengamankan kerahasiaan pesan darurat dari penyadap di jaringan?")
bullet("Bagaimana memastikan keaslian pengirim dan integritas isi pesan (anti-manipulasi)?")
bullet("Bagaimana mengimplementasikan algoritma RSA secara manual, lengkap, dan dapat divisualisasikan langkah demi langkah?")
bullet("Bagaimana mensimulasikan serangan man-in-the-middle untuk membuktikan sistem dapat mendeteksinya?")

h2("1.3  Tujuan")
bullet("Membangun aplikasi web full-stack yang mengimplementasikan RSA from scratch.")
bullet("Menerapkan digital signature untuk membuktikan keaslian dan integritas pesan.")
bullet("Menerapkan enkripsi untuk menjaga kerahasiaan isi pesan darurat.")
bullet("Menyediakan simulasi serangan penyadap (MITM) yang menunjukkan kegagalan manipulasi.")
bullet("Menampilkan setiap langkah perhitungan RSA secara transparan di antarmuka.")

h2("1.4  Manfaat")
bullet("Bagi akademik: menjadi contoh nyata penerapan teori RSA tanpa bantuan library.")
bullet("Bagi praktik: memberikan pola verifikasi anti-hoaks untuk laporan darurat.")
bullet("Bagi pembelajaran: memperlihatkan keterkaitan matematika diskrit dan kriptografi secara visual.")

h2("1.5  Batasan Proyek")
bullet("RSA dibuat manual, sehingga modulus (n) sengaja berukuran kecil-menengah untuk keperluan demo/pembelajaran — bukan untuk keamanan produksi nyata.")
bullet("Hash yang dipakai adalah hash sederhana (jumlah ASCII mod 10000), bukan fungsi hash kriptografis seperti SHA-256.")
bullet("Private key disimpan di localStorage browser dan tidak pernah dikirim ke database.")
bullet("Tidak ada autentikasi/login; ketiga peran diakses melalui tab terpisah pada origin yang sama.")

# ====================================================================
# BAB 2 - LANDASAN TEORI
# ====================================================================
h1("BAB 2  Landasan Teori")

h2("2.1  Kriptografi Kunci Asimetris")
para(
    "Kriptografi kunci asimetris (public-key cryptography) memakai sepasang kunci yang "
    "matematis berhubungan: kunci publik yang boleh diketahui siapa saja, dan kunci "
    "privat yang hanya diketahui pemiliknya. RSA adalah algoritma asimetris paling "
    "terkenal, diperkenalkan oleh Rivest, Shamir, dan Adleman pada 1977."
)

h2("2.2  Algoritma RSA")
para("RSA bertumpu pada dua fakta matematis: sulitnya memfaktorkan bilangan besar, dan "
     "kemudahan komputasi pangkat modular.")

h3("2.2.1  Pembangkitan Kunci (generateKey)")
code_block(
    "n        = p x q\n"
    "phi(n)   = (p - 1)(q - 1)\n"
    "e        dengan 1 < e < phi(n) dan gcd(e, phi(n)) = 1\n"
    "d        = e^(-1) mod phi(n)     (via Extended Euclidean)\n"
    "\n"
    "Public Key  = (e, n)\n"
    "Private Key = (d, n)"
)

h3("2.2.2  Enkripsi & Dekripsi")
code_block(
    "cipher = blok^e mod n      (menggunakan public key penerima)\n"
    "blok   = cipher^d mod n    (menggunakan private key penerima)"
)

h3("2.2.3  Digital Signature & Verifikasi")
code_block(
    "hash           = (jumlah ASCII payload) mod 10000\n"
    "signature      = hash^d mod n              (private key PENGIRIM)\n"
    "verifiedHash   = signature^e mod n         (public key PENGIRIM)\n"
    "recomputedHash = hash(payload hasil dekripsi)\n"
    "valid          = (verifiedHash == recomputedHash)"
)

h2("2.3  Extended Euclidean Algorithm")
para(
    "Algoritma Extended Euclidean mencari koefisien Bezout x dan y sehingga "
    "a*x + b*y = gcd(a, b). Dari identitas ini diperoleh kunci privat d sebagai "
    "invers modular e terhadap phi(n)."
)
code_block(
    "old_r, r = a, b\n"
    "old_s, s = 1, 0\n"
    "old_t, t = 0, 1\n"
    "while r != 0:\n"
    "    q = old_r // r\n"
    "    old_r, r = r, old_r - q*r\n"
    "    old_s, s = s, old_s - q*s\n"
    "    old_t, t = t, old_t - q*t\n"
    "# hasil: old_r = gcd, old_s = x, old_t = y"
)

h2("2.4  Modular Exponentiation (Square-and-Multiply)")
para(
    "Menghitung base^exp mod n secara efisien dengan membaca representasi biner "
    "eksponen. Setiap bit: kuadratkan hasil (square), dan bila bit = 1, kalikan dengan "
    "basis (multiply). Proyek ini TIDAK memakai fungsi pow(a, b, n) bawaan."
)
code_block(
    "result = 1\n"
    "for bit in bin(exp)[2:]:\n"
    "    result = (result * result) % mod       # square\n"
    "    if bit == '1':\n"
    "        result = (result * base) % mod     # multiply"
)

h2("2.5  Skema Encoding Blok Teks")
para(
    "Teks diubah menjadi blok angka dengan skema ASCII 3 digit. Setiap karakter "
    "diwakili 3 digit ('A' -> 065). Beberapa karakter digabung menjadi satu blok, "
    "dengan ukuran blok dihitung otomatis sehingga nilai blok selalu lebih kecil dari n."
)
code_block(
    "'A' = 065, 'B' = 066, ... , 'z' = 122\n"
    "k karakter  -> maksimum 10^(3k) - 1, jadi butuh 10^(3k) - 1 < n"
)

# ====================================================================
# BAB 3 - ANALISIS & PERANCANGAN
# ====================================================================
h1("BAB 3  Analisis & Perancangan Sistem")

h2("3.1  Gambaran Umum")
para(
    "Sistem terdiri dari tiga peran yang dipisah menjadi tiga halaman web (tab) berbeda "
    "pada origin yang sama: Pengirim (/sender), Penyadap (/attacker), dan Pusat Darurat "
    "(/center). Pemisahan ini dibuat agar demonstrasi tiga peran terasa nyata."
)

h2("3.2  Format Payload")
para("Payload pesan darurat digabung dengan pembatas pipa (|):")
code_block("Nama|Latitude|Longitude|Waktu|Pesan\n"
           "Contoh: Fwxz|-7.275847|112.794702|2026-10-07 13:20:15|Terjadi kecelakaan lalu lintas")

h2("3.3  Arsitektur Tiga Lapis (Backend)")
code_block(
    "rsa.py   -> algoritma RSA murni (tanpa import Flask/DB)\n"
    "db.py    -> koneksi & query database (psycopg2, parameterized) + fallback in-memory\n"
    "app.py   -> routing HTTP + validasi input + orkestrasi rsa/db"
)

h2("3.4  Diagram Arsitektur")
code_block(
    "BROWSER (satu origin, tiga tab peran)\n"
    "  /sender            /attacker           /center\n"
    "  keygen -> sign     sadap -> payload    inbox -> decrypt -> verify\n"
    "  -> encrypt         palsu -> serang\n"
    "  localStorage:      TANPA private      localStorage: private pusat\n"
    "  private pengirim   key apa pun        (tak pernah ke database)\n"
    "        |                  |                  |\n"
    "        +------------------+------------------+\n"
    "                           | JSON (angka RSA = STRING)\n"
    "                           v\n"
    "  RENDER (Python) - gunicorn app:app\n"
    "  app.py (routing) -> rsa.py (RSA from scratch)\n"
    "        \\-> db.py (psycopg2, parameterized)\n"
    "                           | DATABASE_URL (Session Pooler)\n"
    "                           v\n"
    "  SUPABASE PostgreSQL\n"
    "  users  +  sos_messages"
)

h2("3.5  Prinsip Perancangan Penting")
bullet("Semua angka RSA dikirim & disimpan sebagai STRING agar JavaScript tidak kehilangan presisi (aman terhadap batas Number 2^53).")
bullet("Private key tidak pernah disimpan di database maupun di-log. Hanya berada di localStorage browser dan dikirim sekali per request.")
bullet("Query database sepenuhnya parameterized (%s) untuk mencegah SQL injection.")
bullet("Pusat darurat murni sebagai penanggap — tidak memiliki tombol serangan.")

# ====================================================================
# BAB 4 - IMPLEMENTASI rsa.py
# ====================================================================
h1("BAB 4  Implementasi Kriptografi (rsa.py)")
para(
    "Modul rsa.py berisi seluruh algoritma RSA dari nol. Tidak mengimpor Flask maupun "
    "database. Setiap fungsi mengembalikan 'log langkah' (list of dict) bila prosesnya "
    "bertahap, supaya seluruh perhitungan dapat ditampilkan di UI."
)

h2("4.1  Daftar Fungsi")
table(
    ["Fungsi (Python)", "Nama Spesifikasi", "Keterangan"],
    [
        ["is_prime(n)", "isPrime(n)", "Trial division sampai akar n, manual."],
        ["gcd(a, b)", "gcd(a, b)", "Algoritma Euclid dasar + log langkah."],
        ["extended_euclidean(a, b)", "extendedEuclidean(a, b)", "Koefisien Bezout + tabel iterasi."],
        ["mod_inverse(e, phi)", "modInverse(e, phi)", "e^-1 mod phi via EEA."],
        ["generate_key(p, q, e)", "generateKey(p, q, e)", "Validasi + seluruh log tahapan."],
        ["mod_pow(base, exp, mod)", "modPow(base, exp, mod)", "Square-and-multiply manual + tabel."],
        ["text_to_blocks(text, n)", "textToBlocks(text, n)", "ASCII 3 digit menjadi blok < n."],
        ["blocks_to_text(blocks, n)", "blocksToText(blocks, n)", "Blok kembali menjadi teks."],
        ["encrypt(text, e, n)", "encrypt(text, e, n)", "blok^e mod n per blok."],
        ["decrypt(blocks, d, n)", "decrypt(blocks, d, n)", "cipher^d mod n per blok."],
        ["hash_message(text)", "hashMessage(text)", "Sigma ASCII mod 10000."],
        ["sign_message(text, d, n)", "signMessage(text, d, n)", "hash^d mod n."],
        ["verify_signature(text, sig, e, n)", "verifySignature(...)", "sig^e mod n vs hash ulang."],
    ],
    widths=[5.5, 5.0, 6.0],
)

h2("4.2  Validasi pada generate_key")
para("Fungsi generate_key memvalidasi masukan secara berurutan dan mengembalikan pesan "
     "kesalahan yang jelas apabila tidak valid:")
numbered("p harus bilangan prima (dicek dengan is_prime).")
numbered("q harus bilangan prima.")
numbered("p tidak boleh sama dengan q.")
numbered("gcd(e, phi(n)) harus sama dengan 1.")
numbered("e harus memenuhi 1 < e < phi(n).")
numbered("n harus lebih besar dari 10000 (nilai hash maksimum adalah 9999).")
numbered("n harus cukup besar untuk menampung blok ASCII 3 digit.")

h2("4.3  Skema Pembentukan Blok")
para("Ukuran blok dihitung dengan fungsi _block_size(n): menemukan jumlah karakter k "
     "terbanyak sehingga nilai blok maksimum 10^(3k)-1 masih lebih kecil dari n. Untuk "
     "n pusat demo (1.000.962.923), diperoleh k = 3 karakter per blok (9 digit).")

h2("4.4  Hash Sederhana")
para("Fungsi hash_message menjumlahkan seluruh nilai ASCII karakter payload lalu "
     "mengambil modulo 10000 (HASH_MODULUS). Karena nilai hash maksimum 9999, modulus n "
     "wajib lebih besar dari 10000.")

# ====================================================================
# BAB 5 - BACKEND
# ====================================================================
h1("BAB 5  Implementasi Backend (app.py)")
para(
    "app.py adalah lapisan routing. Tugasnya hanya menerima request, memvalidasi "
    "masukan, memanggil rsa.py/db.py, lalu mengembalikan JSON. Tidak ada library "
    "kriptografi yang diimpor. Semua input divalidasi dan semua angka diserialisasi ke "
    "string melalui helper B()."
)

h2("5.1  Helper Penting")
bullet("B(value): rekursif mengubah int menjadi str (bool dibiarkan) untuk menjaga presisi angka RSA.")
bullet("to_int(value, name): konversi input ke int dengan pesan error yang jelas.")
bullet("_load_message(msg_id): mengambil pesan + relasi kunci publik pengirim & pusat.")
bullet("_center_private(body): mengambil private key pusat dari request (sekali pakai).")
bullet("_decrypt_message(msg, center, d, n): dekripsi + validasi kecocokan private key.")
bullet("_check_expiry(waktu_str): cek kedaluwarsa alert (batas 5 menit).")

h2("5.2  Daftar Endpoint REST")
table(
    ["Method", "Endpoint", "Fungsi"],
    [
        ["GET", "/", "Landing page (pilih peran)"],
        ["GET", "/sender", "Halaman Pengirim"],
        ["GET", "/attacker", "Halaman Penyadap (man-in-the-middle)"],
        ["GET", "/center", "Halaman Pusat Darurat"],
        ["GET", "/health", "Status aplikasi + koneksi database"],
        ["POST", "/api/keygen", "Pembangkitan kunci {p,q,e} -> public/private + log"],
        ["POST", "/api/users", "Daftarkan user + public key saja"],
        ["GET", "/api/users?role=", "Daftar user (data publik)"],
        ["POST", "/api/sign", "Hash + signature {payload, private}"],
        ["POST", "/api/encrypt", "Enkripsi {text, e, n} -> daftar blok cipher"],
        ["POST", "/api/send", "Simpan paket SOS (ciphertext, original_ciphertext, signature)"],
        ["GET", "/api/inbox?center_id=", "Inbox pusat; tanpa center_id -> semua paket (sadap)"],
        ["POST", "/api/inbox/<id>/decrypt", "Dekripsi dengan private key pusat"],
        ["POST", "/api/inbox/<id>/verify", "Verifikasi signature -> simpan status"],
        ["POST", "/api/inbox/<id>/tamper", "Penyadap mengganti isi (payload palsu / gaya lama)"],
        ["POST", "/api/inbox/<id>/reset", "Kembalikan ciphertext ke original_ciphertext"],
    ],
    widths=[2.0, 6.0, 8.5],
)

h2("5.3  Contoh Alur Endpoint Verifikasi")
para("Saat /api/inbox/<id>/verify dipanggil:")
numbered("Server memuat pesan dan memasangkan public key pengirim dari database.")
numbered("Server mendekripsi ciphertext dengan private key pusat.")
numbered("Server menghitung verifiedHash = signature^e mod n (public key pengirim).")
numbered("Server menghitung ulang hash dari hasil dekripsi.")
numbered("Bila sama -> status 'valid'; bila berbeda -> status 'invalid' (tersimpan di DB).")

# ====================================================================
# BAB 6 - DATABASE
# ====================================================================
h1("BAB 6  Implementasi Database (db.py & schema.sql)")
para(
    "db.py menyediakan akses database menggunakan driver psycopg2 (hanya driver, bukan "
    "library kriptografi). Koneksi diambil dari environment variable DATABASE_URL. Bila "
    "DATABASE_URL tidak di-set, modul otomatis memakai penyimpanan in-memory agar demo "
    "lokal tetap berjalan tanpa database."
)

h2("6.1  Struktur Tabel")
h3("Tabel users")
table(
    ["Kolom", "Tipe", "Keterangan"],
    [
        ["id", "BIGSERIAL PK", "Identitas unik user"],
        ["name", "TEXT", "Nama pengirim / pusat"],
        ["role", "TEXT", "sender | center (CHECK)"],
        ["pub_e", "TEXT", "Eksponen publik (string)"],
        ["pub_n", "TEXT", "Modulus publik (string)"],
        ["created_at", "TIMESTAMPTZ", "Waktu dibuat"],
    ],
    widths=[3.5, 3.5, 9.0],
)

h3("Tabel sos_messages")
table(
    ["Kolom", "Tipe", "Keterangan"],
    [
        ["id", "BIGSERIAL PK", "Identitas paket"],
        ["sender_id", "BIGINT FK", "Referensi ke users"],
        ["center_id", "BIGINT FK", "Referensi ke users"],
        ["ciphertext", "JSONB", "Blok cipher saat ini (bisa sudah ditamper)"],
        ["original_ciphertext", "JSONB", "Blok cipher asli (untuk Reset)"],
        ["signature", "TEXT", "Signature RSA (string)"],
        ["status", "TEXT", "pending | valid | invalid"],
        ["tampered", "BOOLEAN", "Penanda sudah dimanipulasi"],
        ["created_at", "TIMESTAMPTZ", "Waktu masuk"],
    ],
    widths=[4.0, 3.0, 9.0],
)

h2("6.2  Mode Ganda (Postgres / In-Memory)")
bullet("Dengan DATABASE_URL -> terhubung ke Supabase PostgreSQL (data persisten).")
bullet("Tanpa DATABASE_URL -> mode in-memory (data hilang saat server berhenti, cocok untuk demo).")
bullet("Semua query memakai parameterized query (%s) untuk keamanan.")

h2("6.3  Catatan Penyimpanan Angka RSA")
para("Semua angka RSA (pub_e, pub_n, signature, blok ciphertext) disimpan sebagai TEXT / "
     "JSONB berisi string supaya tidak ada kehilangan presisi saat dibaca JavaScript.")

# ====================================================================
# BAB 7 - FRONTEND
# ====================================================================
h1("BAB 7  Implementasi Frontend (UI/UX)")

h2("7.1  Landasan Teknologi")
para("Frontend memakai HTML5 + CSS3 (dark theme) + JavaScript murni (fetch, geolocation, "
     "localStorage). Tidak ada framework dan tidak ada library kriptografi di browser — "
     "semua perhitungan dikerjakan di server lalu ditampilkan.")

h2("7.2  File Frontend")
table(
    ["File", "Fungsi"],
    [
        ["templates/index.html", "Landing page (pilih peran) + panduan demo"],
        ["templates/sender.html", "Halaman Pengirim (3 panel)"],
        ["templates/attacker.html", "Halaman Penyadap (3 panel)"],
        ["templates/center.html", "Halaman Pusat Darurat (5 panel)"],
        ["static/style.css", "Tema dark mode, responsif, tabel langkah"],
        ["static/common.js", "Utilitas UI bersama (api, toast, block, kv, renderKeyLogs)"],
        ["static/sender.js", "Alur pengirim: keygen -> sign -> encrypt -> send"],
        ["static/attacker.js", "Alur penyadap: sadap -> payload palsu -> serang/reset"],
        ["static/center.js", "Alur pusat: keygen -> inbox -> decrypt -> verify"],
    ],
    widths=[5.5, 11.0],
)

h2("7.3  Pola UI: Stepper & Panel Terkunci")
para("Setiap halaman memiliki stepper di bagian atas dan panel yang terbuka bertahap. "
     "Panel terkunci memakai class .locked (opacity rendah + pointer-events: none) "
     "sehingga pengguna mengikuti alur secara berurutan.")

h2("7.4  Pengelolaan Private Key di Browser")
para("Private key disimpan di localStorage melalui objek STORE pada common.js. Private "
     "key dikirim per request, dipakai, lalu dibuang oleh server — tidak pernah "
     "dipersistensikan ke database.")

h2("7.5  Geolocation")
para("Tombol 'Ambil Lokasi Saya' memakai navigator.geolocation.getCurrentPosition, yang "
     "hanya diizinkan browser pada origin aman (localhost/127.0.0.1 atau HTTPS). Jika "
     "izin ditolak, tersedia input manual lat/lon sebagai fallback.")

# ====================================================================
# BAB 8 - ALUR END-TO-END
# ====================================================================
h1("BAB 8  Alur Sistem End-to-End")
code_block(
    "[ /sender ]                [ /attacker ]              [ /center ]\n"
    " Panel 1 Keygen pengirim   1 Muat paket disadap       Panel 1 Keygen pusat\n"
    "      |                     (ciphertext + signature        | (public key -> DB)\n"
    " Panel 2 Payload -> HASH    terbuka, isi tertutup)          |\n"
    "      |  -> SIGN                   |                       |\n"
    " Panel 3 Enkripsi (pub pusat)     |                       |\n"
    "      |                           |                       |\n"
    "      +-- paket -- INSERT --> sos_messages <-- sadap -----+\n"
    "                                 |      2 Serang: payload palsu\n"
    "                                 |        (enkripsi pub pusat + signature lama)\n"
    "                    GET /api/inbox (dari database)\n"
    "                                 |\n"
    "              DEKRIPSI (priv pusat) -> VERIFIKASI (pub pengirim)\n"
    "                                 |\n"
    "                    UPDATE status: valid / invalid"
)

h2("8.1  Peta Panel ke Kunci yang Dipakai")
table(
    ["Halaman", "Panel", "Kunci yang Dipakai"],
    [
        ["/sender", "1 Key Generation", "Pasangan kunci pengirim"],
        ["/sender", "2 Sender SOS", "Hash + signature: private key pengirim"],
        ["/sender", "3 Encryption Process", "Enkripsi: public key pusat darurat"],
        ["/attacker", "1 Paket Disadap", "Tanpa kunci — hanya metadata terbuka"],
        ["/attacker", "2 Susun & Serang", "Enkripsi ulang: public key pusat + signature lama"],
        ["/center", "1 Key Generation", "Pasangan kunci pusat"],
        ["/center", "4 Emergency Center", "Inbox DB + dekripsi: private key pusat"],
        ["/center", "5 Verification Result", "Verifikasi: public key pengirim (dari DB)"],
    ],
    widths=[3.0, 5.0, 8.5],
)

# ====================================================================
# BAB 9 - SERANGAN
# ====================================================================
h1("BAB 9  Fitur Simulasi Serangan (Man-in-the-Middle)")
para(
    "Serangan disimulasikan dari sudut pandang pihak ketiga (penyadap), bukan pusat "
    "darurat. Penyerang tidak memiliki private key apa pun — hanya dapat melihat "
    "metadata terbuka dan mengganti isi dengan signatur lama yang ditempel."
)

h2("9.1  Kapabilitas & Batasan Penyerang")
bullet("Bisa MELIHAT: id paket, pengirim, ukuran, dan signature (semuanya terbuka di jalan).")
bullet("Tidak bisa MEMBACA isi: dekripsi butuh private key pusat darurat.")
bullet("Bisa MENGGANTI isi: enkripsi butuh public key pusat yang memang terbuka.")
bullet("Tidak bisa MENANDATANGANI: signature baru butuh private key pengirim.")

h2("9.2  Aksi pada Halaman Penyadap")
table(
    ["Aksi", "Mekanisme"],
    [
        ["Muat Paket Disadap", "Melihat metadata paket; signature terlihat, isi tertutup."],
        ["Serang — Ganti Isi Paket", "Menyusun payload palsu, enkripsi dengan public key pusat, tempel signature lama."],
        ["Reset ke Paket Asli", "Ciphertext dipulihkan dari original_ciphertext."],
    ],
    widths=[5.0, 11.5],
)

h2("9.3  Mengapa Serangan Terdeteksi")
para(
    "Saat pusat darurat memverifikasi, verifiedHash (= signature^e mod n) menghasilkan "
    "hash dari isi ASLI, sedangkan hash ulang dari isi PALSU berbeda. Akibatnya status "
    "menjadi invalid dan flag tampered tersimpan di database. Setelah tombol Reset, "
    "verifikasi kembali valid — membuktikan RSA menjaga kerahasiaan sekaligus integritas."
)

h2("9.4  Catatan Perbaikan Bug")
para(
    "Pada pengembangan ditemukan bug: klik baris paket di halaman Penyadap tidak membuka "
    "panel serangan. Penyebabnya adalah perbandingan id dengan strict equality antara "
    "string (dari server, hasil serialisasi B()) dan number (dari dataset HTML), "
    "sehingga paket tidak ditemukan. Perbaikan: membandingkan id sebagai string "
    "(String(p.id) === String(id)) dan mengaktifkan tombol Reset saat paket dipilih."
)

# ====================================================================
# BAB 10 - PENGUJIAN
# ====================================================================
h1("BAB 10  Pengujian (Test End-to-End)")
para("Pengujian otomatis dilakukan lewat test_e2e.py yang menjalankan alur lengkap via "
     "API: keygen -> users -> sign -> encrypt -> send -> inbox -> decrypt -> verify, "
     "termasuk skenario manipulasi dan validasi input salah. Seluruh 79 kasus uji lulus.")

h2("10.1  Cakupan Pengujian")
table(
    ["Kelompok Uji", "Contoh Kasus"],
    [
        ["Halaman & Health", "GET /, /sender, /center, /attacker, /health; pusat tanpa tombol serangan"],
        ["Keygen", "valid pengirim/pusat; p bukan prima; gcd != 1; p == q; n terlalu kecil; input bukan angka"],
        ["Registrasi User", "daftar pengirim/pusat; hanya public key yang tersimpan; validasi role"],
        ["Sign", "hash 5753; signature 118799; private tidak di-echo; payload kosong ditolak"],
        ["Encrypt", "26 blok; ukuran blok 3 karakter; semua blok string; digit stream"],
        ["Send & Inbox", "status pending; tampered false; user tak dikenal ditolak"],
        ["Decrypt", "plaintext sesuai; field terpecah; private key salah ditolak"],
        ["Verify (valid)", "SOS VALID; hash sama; status valid tersimpan"],
        ["Serangan Payload Palsu", "isi berubah; tampered true; TIDAK VALID; status invalid"],
        ["Serangan Lokasi Palsu", "koordinat berubah; TIDAK VALID"],
        ["Reset", "tampered false; kembali VALID"],
        ["Kompatibilitas Gaya Lama", "mode message/location + plaintext tetap jalan"],
    ],
    widths=[5.0, 11.5],
)

h2("10.2  Parameter Demo Teruji")
h3("Kunci Pengirim (p/q/e = 1009/1013/17)")
table(
    ["Parameter", "Nilai"],
    [["n", "1.022.117"], ["phi(n)", "1.020.096"], ["d", "180.017"]],
    widths=[5.0, 8.0],
)
h3("Kunci Pusat Darurat (p/q/e = 31627/31649/13)")
table(
    ["Parameter", "Nilai"],
    [["n", "1.000.962.923"], ["phi(n)", "1.000.899.648"], ["d", "615.938.245"]],
    widths=[5.0, 8.0],
)

h2("10.3  Hasil Skenario")
table(
    ["Tahap", "Hasil"],
    [
        ["Hash payload", "5753"],
        ["Signature (hash^d mod n pengirim)", "118799"],
        ["Blok ciphertext", "26 blok (3 karakter/blok)"],
        ["Verifikasi normal", "SOS VALID — 5753 = 5753, status valid"],
        ["Serangan ganti isi", "TIDAK VALID — 5753 != 6990, status invalid + tampered"],
        ["Serangan ganti pesan", "TIDAK VALID — 5753 != 7015, status invalid"],
        ["Setelah Reset", "SOS VALID kembali"],
    ],
    widths=[6.0, 10.5],
)

# ====================================================================
# BAB 11 - SCREENSHOT
# ====================================================================
h1("BAB 11  Dokumentasi Screenshot")
para("Bagian ini menampilkan tangkapan layar alur demo end-to-end. Seluruh berkas gambar "
     "tersimpan pada folder picture/ di repositori proyek.")

h2("11.1  Landing Page")
add_image("SOS_LandingPage.png", 15.5, "Gambar 11.1 — Halaman landing (pemilihan peran).")

h2("11.2  Halaman Pengirim")
add_image("SOS_Pengirim_KeyGeneration.png", 15.5, "Gambar 11.2 — Generate Keys pengirim.")
add_image("SOS_Pengirim_KeyGenerationSuccess.png", 15.5, "Gambar 11.3 — Kunci pengirim berhasil dibuat.")
add_image("SOS_Pengirim_SenderSOS.png", 15.5, "Gambar 11.4 — Formulir pesan SOS.")
add_image("SOS_Pengirim_EncryptProcess.png", 15.5, "Gambar 11.5 — Proses hash, signature, dan enkripsi.")
add_image("SOS_Pengirim_EncryptnSend.png", 15.5, "Gambar 11.6 — Enkripsi & kirim paket.")
add_image("SOS_Pengirim_EncryptnSend2.png", 15.5, "Gambar 11.7 — Konfirmasi paket terkirim.")

h2("11.3  Halaman Penyadap (Man-in-the-Middle)")
add_image("SOS_Penyadap_PaketPenyadap.png", 15.5, "Gambar 11.8 — Memuat paket yang disadap.")
add_image("SOS_Penyadap_PaketPenyadapSucess.png", 15.5, "Gambar 11.9 — Paket berhasil disadap & dipilih.")
add_image("SOS_Penyadap_PayloadPalsu.png", 15.5, "Gambar 11.10 — Menyusun payload palsu & menyerang.")

h2("11.4  Halaman Pusat Darurat")
add_image("SOS_PusatDarurat_KeyGeneration.png", 15.5, "Gambar 11.11 — Generate & daftarkan kunci pusat.")
add_image("SOS_PusatDarurat_SOSValid.png", 15.5, "Gambar 11.12 — Verifikasi SOS VALID.")
add_image("SOS_PusatDarurat_Terserang.png", 15.5, "Gambar 11.13 — Pesan terdeteksi telah dimanipulasi.")
add_image("SOS_PusatDarurat_SOSTidakValid.png", 15.5, "Gambar 11.14 — Verifikasi SOS TIDAK VALID.")
add_image("SOS_PusatDarurat_TidakTerserang.png", 15.5, "Gambar 11.15 — Setelah reset, SOS kembali VALID.")

# ====================================================================
# BAB 12 - MENJALANKAN & DEPLOY
# ====================================================================
h1("BAB 12  Panduan Menjalankan & Deployment")

h2("12.1  Menjalankan Secara Lokal")
code_block(
    "python -m venv venv\n"
    "venv\\Scripts\\activate            # Windows (Linux: source venv/bin/activate)\n"
    "pip install -r requirements.txt\n"
    "\n"
    "python app.py                    # buka http://127.0.0.1:5000\n"
    "python test_e2e.py               # uji end-to-end (server harus hidup)"
)
para("Mode database:")
bullet("Tanpa DATABASE_URL -> otomatis mode in-memory (data hilang saat server berhenti).")
bullet("Dengan DATABASE_URL -> terhubung ke Supabase PostgreSQL (salin .env.example menjadi .env).")

h2("12.2  Deployment")
h3("A. Supabase (database)")
numbered("Buat project baru di supabase.com, pilih region terdekat.")
numbered("Buka SQL Editor, jalankan seluruh isi schema.sql.")
numbered("Salin connection string Session Pooler (port 6543).")
numbered("Simpan sebagai nilai DATABASE_URL (jangan di-commit).")

h3("B. Render (aplikasi)")
numbered("Push repositori ke GitHub.")
numbered("Buat Web Service baru di render.com dan hubungkan repositori.")
numbered("Build Command: pip install -r requirements.txt")
numbered("Start Command: gunicorn app:app")
numbered("Tambahkan environment variable DATABASE_URL dan FLASK_DEBUG=0.")
numbered("Buka /health untuk memastikan database mode postgresql, ok true.")

h3("C. Catatan Cold Start")
bullet("Pada free tier, Render menonaktifkan service setelah ~15 menit idle.")
bullet("Request pertama setelah idle dapat memakan 30-60 detik (normal).")
bullet("Data tidak hilang karena tersimpan di Supabase; private key aman di localStorage.")

# ====================================================================
# BAB 13 - KEPATUHAN
# ====================================================================
h1("BAB 13  Kepatuhan Tanpa Library Kriptografi")
para("Proyek ini TIDAK memakai library kriptografi apa pun, baik di backend maupun "
     "frontend: tidak ada crypto, cryptography, pycryptodome, OpenSSL, java.security, "
     "node-rsa, forge, crypto-js, hashlib, secrets, maupun library signature lain.")
para("Ditulis manual di rsa.py:", bold=True)
bullet("Pengecekan bilangan prima (trial division).")
bullet("GCD dan Extended Euclidean (koefisien Bezout).")
bullet("Modular inverse.")
bullet("Pembangkitan public/private key.")
bullet("Modular exponentiation (square-and-multiply, tanpa pow(a,b,n)).")
bullet("Enkripsi & dekripsi.")
bullet("Hash sederhana.")
bullet("Digital signature & verifikasi.")
para("Flask hanya untuk routing/serving · psycopg2 hanya driver database · frontend "
     "memakai HTML + CSS + JavaScript murni.")

# ====================================================================
# BAB 14 - PEMBAGIAN KERJA
# ====================================================================
h1("BAB 14  Pembagian Kerja & Tahapan Build")

h2("14.1  Pembagian Tanggung Jawab")
table(
    ["Tanggung Jawab", "Penanggung Jawab"],
    [
        ["Backend & DevOps — arsitektur 3 lapis, db.py, schema.sql, seluruh endpoint REST, validasi, .env.example, Procfile, deployment Supabase + Render, penanganan cold start",
         "Dimas Satya Andhika (4027241032)"],
        ["Kriptografi & Pengujian — rsa.py seluruh algoritma dari nol + log langkah, skema encoding blok, test_e2e.py (79 kasus), analisis skenario serangan",
         "Ahmad Wildan Fawwaz (5027241001)"],
        ["Frontend & Demo — halaman Pengirim/Penyadap/Pusat, landing page, style.css, common.js/sender.js/attacker.js/center.js, visualisasi langkah + stepper, geolocation, alur MITM",
         "Daniswara Fausta Novanto (5027241050)"],
    ],
    widths=[10.5, 5.5],
)

h2("14.2  Tahapan Build dari 0")
table(
    ["#", "Tahap", "Isi Pekerjaan"],
    [
        ["0", "Setup environment", "Python + venv, git init, .gitignore, struktur folder"],
        ["1", "Analisis & desain", "Studi kasus, format payload, diagram alur, desain UI 5 panel"],
        ["2", "RSA dari nol", "isPrime, gcd, EEA, modInverse, generateKey, modPow, blok, encrypt, decrypt, hash, sign, verify"],
        ["3", "Backend MVP + UI", "app.py versi awal, 5 panel, render tabel langkah, geolocation"],
        ["4", "Refaktorisasi", "Pisah rsa.py/db.py/app.py, schema.sql, angka RSA sebagai string, private key ke localStorage"],
        ["5", "Halaman peran", "/sender, /center, landing + common.js/sender.js/center.js, registrasi users, inbox dari DB"],
        ["6", "Halaman Penyadap", "/attacker MITM, ciphertext vs original_ciphertext, endpoint tamper/reset, cek kedaluwarsa"],
        ["7", "Pengujian menyeluruh", "test_e2e.py 79 kasus lulus, scan repo tanpa library kriptografi"],
        ["8", "Dokumentasi & deploy", "README lengkap, .env.example, Procfile, panduan Supabase + Render"],
    ],
    widths=[1.0, 4.0, 11.5],
)

# ====================================================================
# BAB 15 - KESIMPULAN
# ====================================================================
h1("BAB 15  Kesimpulan & Saran")

h2("15.1  Kesimpulan")
numbered("Sistem berhasil mengimplementasikan RSA (keygen, enkripsi, dekripsi, hash, signature, verifikasi) sepenuhnya dari nol tanpa library kriptografi.")
numbered("Digital signature terbukti menjaga integritas: perubahan satu karakter pun membuat hash berbeda sehingga pesan ditolak sebagai tidak valid.")
numbered("Enkripsi dengan public key pusat terbukti menjaga kerahasiaan: penyadap tidak dapat membaca isi pesan.")
numbered("Simulasi serangan man-in-the-middle berhasil membuktikan bahwa manipulasi isi selalu terdeteksi, dan fitur reset memulihkan pesan asli.")
numbered("Seluruh 79 kasus uji end-to-end lulus, mencakup alur normal, serangan, reset, dan validasi input salah.")

h2("15.2  Saran Pengembangan")
bullet("Mengganti hash sederhana dengan fungsi hash kriptografis yang juga diimplementasikan manual (mis. pendekatan MD5/SHA sederhana) agar tahan terhadap collision.")
bullet("Memperbesar ukuran modulus dan menerapkan padding (mis. OAEP) untuk keamanan menuju skenario nyata.")
bullet("Menambahkan skema hybrid encryption (RSA untuk kunci sesi + AES untuk data) agar efisien untuk pesan besar.")
bullet("Menambahkan autentikasi pengguna dan manajemen kunci yang lebih aman.")

# ====================================================================
# FOOTER
# ====================================================================
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("— Akhir Laporan —")
r.bold = True
r.font.color.rgb = MUTED

doc.save(OUT)
print("Laporan tersimpan:", OUT)
