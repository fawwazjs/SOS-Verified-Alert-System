"""
rsa.py
====================================================================
Implementasi ALGORITMA RSA DARI NOL (from scratch).

ATURAN MUTLAK:
    Tidak memakai library kriptografi apa pun (crypto, cryptography,
    pycryptodome, hashlib, dsb). Semua algoritma ditulis manual.
    Python hanya dipakai karena mendukung bilangan besar secara native.

Setiap fungsi mengembalikan "log langkah" (list of dict) bila prosesnya
bertahap, supaya seluruh perhitungan RSA bisa ditampilkan di UI.

Pemetaan nama fungsi (snake_case Python -> nama pada spesifikasi tugas):
    is_prime              -> isPrime(n)
    gcd                   -> gcd(a, b)
    extended_euclidean    -> extendedEuclidean(a, b)
    mod_inverse           -> modInverse(e, phi)
    generate_key          -> generateKey(p, q, e)
    mod_pow               -> modPow(base, exp, mod)
    encrypt               -> encrypt(text, e, n)
    decrypt               -> decrypt(blocks, d, n)
    hash_message          -> hashMessage(text)
    sign_message          -> signMessage(text, d, n)
    verify_signature      -> verifySignature(text, signature, e, n)
    text_to_blocks        -> textToBlocks(text, n)
    blocks_to_text        -> blocksToText(blocks, n)
====================================================================
"""

# --------------------------------------------------------------------
# KONSTANTA
# --------------------------------------------------------------------
# hash = (jumlah ASCII) mod 10000  -> nilai hash maksimum 9999.
# n (modulus) HARUS > 10000 agar hash selalu muat, dan HARUS lebih besar
# dari nilai blok ASCII terbesar yang mungkin dibentuk.
HASH_MODULUS = 10000


# ====================================================================
# 1. PENGECEKAN BILANGAN PRIMA  (isPrime)
# ====================================================================
def is_prime(n):
    """Setara isPrime(n).

    Mengembalikan (hasil: bool, langkah: list).
    Menggunakan trial division sampai akar kuadrat n (ditulis manual,
    tanpa library). Cukup cepat karena p & q pada demo adalah bilangan
    kecil-menengah.
    """
    langkah = []
    n = int(n)

    if n <= 1:
        langkah.append({"cek": f"n = {n} <= 1", "hasil": "BUKAN prima"})
        return False, langkah

    if n <= 3:
        langkah.append({"cek": f"n = {n} ada di {{2,3}}", "hasil": "PRIMA"})
        return True, langkah

    if n % 2 == 0:
        langkah.append({"cek": f"n = {n} habis dibagi 2", "hasil": "BUKAN prima"})
        return False, langkah

    # uji pembagi ganjil dari 3 sampai akar(n)
    i = 3
    prima = True
    pembagi_ditemukan = None
    while i * i <= n:
        if n % i == 0:
            prima = False
            pembagi_ditemukan = i
            break
        i += 2

    if prima:
        langkah.append({
            "cek": f"Tidak ada pembagi dari 3 s/d akar({n})",
            "hasil": f"{n} PRIMA"
        })
    else:
        langkah.append({
            "cek": f"{n} = {pembagi_ditemukan} x {n // pembagi_ditemukan}",
            "hasil": f"{n} BUKAN prima"
        })
    return prima, langkah


# ====================================================================
# 2. GCD (Faktor Persekutuan Terbesar)  (gcd)
# ====================================================================
def gcd(a, b):
    """Setara gcd(a, b). Euclid dasar (berulang).

    Mengembalikan (hasil: int, langkah: list).
    """
    langkah = []
    a, b = int(a), int(b)
    langkah.append({"iterasi": f"gcd({a}, {b})"})
    while b != 0:
        q = a // b
        r = a % b
        langkah.append({
            "operasi": f"{a} = {q} x {b} + {r}",
            "sisa": r
        })
        a, b = b, r
    langkah.append({"hasil": f"gcd = {a}"})
    return a, langkah


# ====================================================================
# 3. EXTENDED EUCLIDEAN ALGORITHM  (extendedEuclidean)
# ====================================================================
def extended_euclidean(a, b):
    """Setara extendedEuclidean(a, b).

    Mencari x, y sehingga a*x + b*y = gcd(a, b).
    Mengembalikan (gcd_val, x, y, langkah).

    Tabel langkah memuat tiap baris iterasi (qi, ri, xi, yi) supaya
    pembentukan koefisien Bezout terlihat jelas di UI.
    """
    langkah = []
    a0, b0 = int(a), int(b)

    # Koefisien awal: r0 = a = a*1 + b*0 ; r1 = b = a*0 + b*1
    old_r, r = a0, b0
    old_s, s = 1, 0
    old_t, t = 0, 1

    langkah.append({"iterasi": 0, "r": old_r, "x": old_s, "y": old_t})
    langkah.append({"iterasi": 1, "r": r, "x": s, "y": t})

    step = 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
        step += 1
        if r != 0:
            langkah.append({"iterasi": step, "r": r, "x": old_s, "y": old_t})

    langkah.append({
        "hasil": f"gcd = {old_r}, x = {old_s}, y = {old_t}",
        "identitas": f"({a0})*({old_s}) + ({b0})*({old_t}) = {old_r}"
    })
    return old_r, old_s, old_t, langkah


# ====================================================================
# 4. MODULAR INVERSE  (modInverse)
# ====================================================================
def mod_inverse(e, phi):
    """Setara modInverse(e, phi).

    Mencari d sehingga (e * d) mod phi = 1 dengan memanfaatkan
    extended Euclidean. Mengembalikan (d, langkah).
    Jika gcd(e, phi) != 1 -> d = None (invers tidak ada).
    """
    g, x, _y, langkah = extended_euclidean(e, phi)
    langkah.insert(0, {
        "info": f"Mencari invers dari e={e} terhadap phi={phi}"
    })
    if g != 1:
        langkah.append({
            "hasil": f"gcd({e},{phi}) = {g} != 1 -> invers TIDAK ADA"
        })
        return None, langkah

    d = x % phi  # pastikan positif
    langkah.append({
        "rumus": "d = x mod phi",
        "substitusi": f"d = {x} mod {phi}",
        "hasil": f"d = {d}"
    })
    langkah.append({
        "verifikasi": f"({e} x {d}) mod {phi} = {(e * d) % phi}"
    })
    return d, langkah


# ====================================================================
# 5. PEMBANGKITAN KUNCI  (generateKey)
# ====================================================================
def generate_key(p, q, e):
    """Setara generateKey(p, q, e).

    Mengembalikan dictionary lengkap:
      - valid : bool
      - error : pesan kesalahan (bila tidak valid)
      - public : {"e":.., "n":..}
      - private: {"d":.., "n":..}
      - logs   : seluruh langkah perhitungan
    """
    logs = []
    p, q, e = int(p), int(q), int(e)

    # --- 1. cek p prima ---
    p_prima, log_p = is_prime(p)
    logs.append({"tahap": "Cek p prima", "nilai": p, "langkah": log_p})

    # --- 2. cek q prima ---
    q_prima, log_q = is_prime(q)
    logs.append({"tahap": "Cek q prima", "nilai": q, "langkah": log_q})

    if not p_prima or not q_prima:
        pesan = []
        if not p_prima:
            pesan.append(f"p = {p} bukan bilangan prima")
        if not q_prima:
            pesan.append(f"q = {q} bukan bilangan prima")
        return {"valid": False, "error": "; ".join(pesan), "logs": logs}

    # --- 3. p != q ---
    if p == q:
        return {
            "valid": False,
            "error": f"p dan q tidak boleh sama (p = q = {p})",
            "logs": logs
        }
    logs.append({"tahap": "Cek p != q", "langkah": [{"hasil": f"{p} != {q} -> OK"}]})

    # --- 4. n = p * q ---
    n = p * q
    logs.append({
        "tahap": "Hitung n = p x q",
        "langkah": [{"rumus": f"n = {p} x {q} = {n}"}]
    })

    # --- 5. phi(n) = (p-1)(q-1) ---
    phi = (p - 1) * (q - 1)
    logs.append({
        "tahap": "Hitung phi(n) = (p-1)(q-1)",
        "langkah": [{"rumus": f"phi = ({p}-1) x ({q}-1) = {p - 1} x {q - 1} = {phi}"}]
    })

    # --- 6. gcd(e, phi) harus 1 ---
    g, log_g = gcd(e, phi)
    logs.append({"tahap": "Cek gcd(e, phi(n)) = 1", "langkah": log_g})
    if g != 1:
        return {
            "valid": False,
            "error": (
                f"gcd(e, phi(n)) = gcd({e}, {phi}) = {g}, harus sama dengan 1. "
                f"Pilih e lain (mis. 3, 5, 17, atau 65537)."
            ),
            "logs": logs
        }
    if e <= 1 or e >= phi:
        return {
            "valid": False,
            "error": f"e harus memenuhi 1 < e < phi(n) = {phi}",
            "logs": logs
        }

    # --- 7. d = modInverse(e, phi) ---
    d, log_d = mod_inverse(e, phi)
    logs.append({"tahap": "Hitung d = modular inverse e mod phi(n)", "langkah": log_d})

    # --- 8. VALIDASI n > 10000 DAN n > nilai blok ASCII maksimum ---
    if n <= HASH_MODULUS:
        return {
            "valid": False,
            "error": (
                f"n = {n} harus lebih besar dari {HASH_MODULUS} (nilai hash maksimum "
                f"adalah 9999). Gunakan p dan q yang lebih besar."
            ),
            "logs": logs
        }

    # cek pula n harus > blok ASCII terbesar (2 digit blok -> maksimum 999999 hanya
    # jika per-karakter 3 digit; di sini kita pakai skema per-karakter 3 digit).
    blok_maks = 999  # satu karakter ASCII 3 digit -> 000..255 -> maksimum 255 sebenarnya
    if n <= 999:
        return {
            "valid": False,
            "error": f"n = {n} terlalu kecil untuk menampung blok ASCII 3 digit.",
            "logs": logs
        }

    logs.append({
        "tahap": "Validasi modulus n",
        "langkah": [{
            "hasil": f"n = {n} > {HASH_MODULUS} (hash) dan > {blok_maks} (blok dasar) -> LAYAK"
        }]
    })

    return {
        "valid": True,
        "error": None,
        "p": p, "q": q, "e": e,
        "n": n,
        "phi": phi,
        "d": d,
        "public": {"e": e, "n": n},
        "private": {"d": d, "n": n},
        "logs": logs,
    }


# ====================================================================
# 6. MODULAR EXPONENTIATION  (modPow) - Square and Multiply
# ====================================================================
def mod_pow(base, exp, mod):
    """Setara modPow(base, exp, mod).

    Menggunakan algoritma square-and-multiply secara manual.
    DILARANG memakai pow(a, b, n) bawaan. Mengembalikan (hasil, langkah).
    """
    langkah = []
    base = int(base) % int(mod)
    exp = int(exp)
    mod = int(mod)

    binary = bin(exp)[2:]  # representasi biner pangkat
    langkah.append({
        "info": f"{base}^{exp} mod {mod}",
        "biner_pangkat": binary
    })

    result = 1
    step = 0
    # iterasi dari bit paling kiri (MSB) ke kanan
    for bit in binary:
        step += 1
        # langkah 1: square -> pangkat dikali 2
        result = (result * result) % mod
        aksi = "square"
        nilai = f"{result}"
        if bit == "1":
            # langkah 2: multiply (karena bit = 1)
            result = (result * base) % mod
            aksi = "square + multiply"
            nilai = f"{result}"
        langkah.append({
            "iterasi": step,
            "bit": bit,
            "aksi": aksi,
            "nilai": nilai
        })

    langkah.append({"hasil": f"{base}^{exp} mod {mod} = {result}"})
    return result, langkah


# ====================================================================
# 7. KONVERSI TEKS <-> BLOK
# ====================================================================
def _block_size(n):
    """Menghitung berapa banyak ASCII (masing-masing 3 digit) yang boleh
    digabung dalam satu blok agar nilai blok SELALU < n.

    Satu karakter diwakili 3 digit (0..255 -> '000'..'255').
    k karakter -> maksimum 10^(3k) - 1, jadi butuh 10^(3k) - 1 < n.
    """
    k = 1
    while (10 ** (3 * (k + 1)) - 1) < n:
        k += 1
    return k


def text_to_blocks(text, n):
    """Setara textToBlocks(text, n).

    Mengubah tiap karakter menjadi 3 digit ASCII, lalu menggabungkan
    beberapa karakter per blok. Mengembalikan (blocks, info, langkah).

    info berisi: size (karakter per blok), digits (digit per blok),
    ascii (daftar nilai ASCII tiap karakter).
    """
    langkah = []
    size = _block_size(n)
    digits = 3 * size
    ascii_list = [ord(c) for c in text]

    langkah.append({
        "info": (
            f"Skema encoding: SETIAP karakter -> 3 digit ASCII (contoh 'A'=065). "
            f"n = {n} memuat {digits} digit -> {size} karakter per blok."
        )
    })

    # bangun string digit: setiap karakter di-pad 3 digit
    digit_string = "".join(f"{a:03d}" for a in ascii_list)

    blocks = []
    detail = []
    for i in range(0, len(digit_string), digits):
        chunk = digit_string[i:i + digits]
        if len(chunk) < digits:
            # padding kanan dengan 0 agar panjang penuh
            chunk = chunk + "0" * (digits - len(chunk))
        blok_val = int(chunk)
        blocks.append(blok_val)
        detail.append({"digits": chunk, "nilai": blok_val})

    langkah.append({
        "total_karakter": len(text),
        "digit_string": digit_string,
        "jumlah_blok": len(blocks)
    })
    info = {
        "size": size,
        "digits": digits,
        "ascii": ascii_list,
        "digit_string": digit_string
    }
    return blocks, info, langkah


def blocks_to_text(blocks, n):
    """Setara blocksToText(blocks, n).

    Mengubah blok angka kembali menjadi teks. Mengembalikan (text, langkah).
    """
    langkah = []
    size = _block_size(n)
    digits = 3 * size

    digit_string = ""
    for b in blocks:
        s = str(int(b)).zfill(digits)
        digit_string += s

    langkah.append({"info": f"Gabung semua blok (padded {digits} digit)"})

    # potong per 3 digit -> ASCII
    chars = []
    ascii_terpakai = []
    for i in range(0, len(digit_string), 3):
        trio = digit_string[i:i + 3]
        if len(trio) < 3:
            break
        val = int(trio)
        ascii_terpakai.append(val)
        # 0 adalah padding; berhenti di situ
        if val == 0:
            break
        chars.append(chr(val))

    langkah.append({
        "ascii": ascii_terpakai,
        "teks": "".join(chars)
    })
    return "".join(chars), langkah


# ====================================================================
# 8. ENKRIPSI  (encrypt)
# ====================================================================
def encrypt(text, e, n):
    """Setara encrypt(text, e, n).

    cipher_blok = blok^e mod n untuk setiap blok.
    Mengembalikan (cipher_list, info, langkah).
    """
    blocks, info, log_teks = text_to_blocks(text, n)
    cipher = []
    tabel = []
    for b in blocks:
        c, log_pow = mod_pow(b, e, n)
        cipher.append(c)
        tabel.append({
            "blok": b,
            "cipher": c,
            "log": log_pow
        })
    langkah = log_teks + [{"tabel": tabel}]
    return cipher, info, langkah


# ====================================================================
# 9. DEKRIPSI  (decrypt)
# ====================================================================
def decrypt(cipher_blocks, d, n):
    """Setara decrypt(blocks, d, n).

    blok = cipher^d mod n untuk setiap ciphertext.
    Mengembalikan (plain_text, info, langkah).
    """
    plain_blocks = []
    tabel = []
    for c in cipher_blocks:
        m, log_pow = mod_pow(c, d, n)
        plain_blocks.append(m)
        tabel.append({
            "cipher": c,
            "blok": m,
            "log": log_pow
        })
    text, log_text = blocks_to_text(plain_blocks, n)
    info = {"blocks": plain_blocks}
    langkah = [{"tabel": tabel}] + log_text
    return text, info, langkah


# ====================================================================
# 10. HASH  (hashMessage)
# ====================================================================
def hash_message(text):
    """Setara hashMessage(text).

    hash = (jumlah seluruh nilai ASCII) mod 10000.
    Mengembalikan (hash_value, langkah).
    """
    ascii_list = [ord(c) for c in text]
    total = sum(ascii_list)
    h = total % HASH_MODULUS
    langkah = [{
        "total_ascii": total,
        "jumlah_karakter": len(text),
        "rumus": f"{total} mod {HASH_MODULUS} = {h}",
        "hash": h
    }]
    return h, langkah


# ====================================================================
# 11. DIGITAL SIGNATURE  (signMessage)
# ====================================================================
def sign_message(text, d, n):
    """Setara signMessage(text, d, n).

    signature = hash^d mod n (private key PENGIRIM).
    Mengembalikan (signature, hash, langkah).
    """
    h, log_hash = hash_message(text)
    sig, log_pow = mod_pow(h, d, n)
    langkah = [{"hash": h, "log_hash": log_hash}, {"log_pow": log_pow}]
    return sig, h, langkah


# ====================================================================
# 12. VERIFIKASI SIGNATURE  (verifySignature)
# ====================================================================
def verify_signature(text, signature, e, n):
    """Setara verifySignature(text, signature, e, n).

    verifiedHash = signature^e mod n, lalu dibandingkan dengan hash
    yang dihitung ulang dari teks.
    Mengembalikan (valid: bool, verified_hash, recomputed_hash, langkah).
    """
    verified_hash, log_pow = mod_pow(signature, e, n)
    recomputed_hash, log_hash = hash_message(text)
    valid = (verified_hash == recomputed_hash)
    langkah = [
        {"log_pow": log_pow},
        {"verified_hash": verified_hash, "recomputed_hash": recomputed_hash},
        {"valid": valid}
    ]
    return valid, verified_hash, recomputed_hash, langkah
