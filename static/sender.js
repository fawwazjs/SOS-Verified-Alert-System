/* ==================================================================
   sender.js - Halaman Pengirim
   Alur: Keygen -> Hash+Signature -> Enkripsi -> Kirim ke database
   Private key pengirim hanya hidup di localStorage + dikirim per request.
   ================================================================== */

const state = {
  payload: null,
  signature: null,
  centers: {},   // id -> {id, name, pub_e, pub_n}
};

/* ---------------- Panel 1: Key Generation ---------------- */
$("#btn-fill").addEventListener("click", () => {
  $("#s-p").value = 1009;
  $("#s-q").value = 1013;
  $("#s-e").value = 17;
});

$("#btn-genkey").addEventListener("click", async () => {
  const box = $("#key-result");
  const { status, data } = await api("/api/keygen", {
    p: $("#s-p").value, q: $("#s-q").value, e: $("#s-e").value,
  });
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal membuat kunci."]);
    toast("Pembangkitan kunci gagal", "err");
    return;
  }

  // simpan pasangan kunci di BROWSER saja (tidak pernah ke server/database)
  STORE.set("sender", {
    userId: null, name: null,
    private: data.private,     // {d, n}
    public: data.public,       // {e, n}
  });

  box.classList.remove("hidden");
  box.innerHTML = `<div class="msg-ok">✓ Kunci pengirim dibuat &amp; disimpan di localStorage.</div>` +
    renderKeyLogs("Kunci Pengirim", data);

  unlock("panel-2");
  setStepper(2);
  $("#btn-sign").disabled = false;
  loadCenters();
  toast("Kunci pengirim siap", "ok");
});

/* ---------------- daftar pusat darurat ---------------- */
async function loadCenters(silent = false) {
  const sel = $("#f-center");
  const { data } = await apiGet("/api/users?role=center");
  if (!data.ok) return;
  sel.innerHTML = "";
  if (!data.users.length) {
    sel.innerHTML = `<option value="">— belum ada pusat darurat —</option>`;
    if (!silent) toast("Buka tab Pusat Darurat & buat kunci dulu", "err");
    return;
  }
  const prev = sel.value;
  state.centers = {};
  data.users.forEach((u) => {
    state.centers[u.id] = u;
    const op = document.createElement("option");
    op.value = u.id;
    op.textContent = `${u.name} (id ${u.id})`;
    sel.appendChild(op);
  });
  // pilih pusat sebelumnya bila masih ada, selain itu pusat terbaru
  const ids = data.users.map((u) => u.id);
  sel.value = ids.includes(Number(prev)) ? prev : ids[ids.length - 1];
}

/* otomatis muat ulang daftar pusat tiap berpindah tab/kembali ke halaman */
window.addEventListener("focus", () => loadCenters(true));

/* ---------------- Geolocation ---------------- */
$("#btn-geo").addEventListener("click", () => {
  const hint = $("#geo-hint");
  if (!navigator.geolocation) {
    hint.textContent = "Geolocation tidak didukung. Isi lat/lon manual.";
    return;
  }
  hint.textContent = "Mengambil lokasi...";
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      $("#f-lat").value = pos.coords.latitude.toFixed(6);
      $("#f-lon").value = pos.coords.longitude.toFixed(6);
      hint.textContent = `Lokasi diperoleh (±${Math.round(pos.coords.accuracy)} m).`;
    },
    () => { hint.textContent = "Izin ditolak/gagal — silakan isi manual."; },
    { enableHighAccuracy: true, timeout: 8000 }
  );
});

/* ---------------- Panel 2: Sign ---------------- */
$("#btn-sign").addEventListener("click", async () => {
  const box = $("#sign-result");
  const keys = STORE.get("sender");
  if (!keys || !keys.private) {
    showErrors(box, ["Private key tidak ada di localStorage. Jalankan Panel 1."]);
    return;
  }
  const payload = [$("#f-nama").value.trim(), $("#f-lat").value.trim(),
                   $("#f-lon").value.trim(), $("#f-waktu").value.trim(),
                   $("#f-pesan").value.trim()].join("|");
  if (payload.split("|").some((v) => v === "")) {
    showErrors(box, ["Semua field wajib diisi (nama, lokasi, waktu, pesan)."]);
    return;
  }

  const { status, data } = await api("/api/sign", {
    payload, private: keys.private,   // private key sekali pakai per request
  });
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal menandatangani."]);
    toast("Signature gagal", "err");
    return;
  }

  state.payload = data.payload;
  state.signature = data.signature;

  box.classList.remove("hidden");
  box.innerHTML =
    `<div class="msg-ok">✓ Signature dibuat dengan <strong>private key pengirim</strong>
      (dikirim per request, lalu dibuang — tidak disimpan server).</div>` +

    block("PAYLOAD", `<div class="mono break">${esc(data.payload)}</div>`) +

    block("HASH &mdash; (jumlah ASCII) mod 10000", `
      <div class="chips">${chipsFromAscii(data.ascii, data.payload)}</div>
      <div style="margin-top:10px">
        ${kv("jumlah karakter", data.hash_log.jumlah_karakter)}
        ${kv("jumlah total ASCII", data.hash_log.total_ascii)}
        ${kv("perhitungan", data.hash_log.rumus)}
        ${kv("NILAI HASH", data.hash)}
      </div>`) +

    block("SIGNATURE &mdash; hash<sup>d</sup> mod n", `
      ${kv("hash", data.hash)}
      ${kv("private key n pengirim", data.public.n)}
      ${kv("SIGNATURE", data.signature)}
      <div style="margin-top:10px;color:var(--muted);font-size:12px">
        Proses square-and-multiply:</div>
      ${powTable(data.pow_log)}`);

  $("#btn-send").disabled = false;
  setStepper(3);
  toast("Signature valid dibuat", "ok");
});

/* ---------------- Panel 3: Encrypt & Send ---------------- */
$("#btn-send").addEventListener("click", async () => {
  const box = $("#encrypt-result");
  const keys = STORE.get("sender");
  const centerId = $("#f-center").value;

  if (!state.payload || !state.signature) {
    showErrors(box, ["Belum ada signature. Klik [Generate Signature] dulu."]);
    return;
  }
  if (!centerId || !state.centers[centerId]) {
    showErrors(box, ["Pilih Pusat Darurat tujuan (buka tab Pusat Darurat bila kosong)."]);
    return;
  }
  const center = state.centers[centerId];

  // 1) enkripsi dengan PUBLIC KEY pusat darurat
  const enc = await api("/api/encrypt", {
    text: state.payload, e: center.pub_e, n: center.pub_n,
  });
  if (enc.status !== 200 || !enc.data.ok) {
    showErrors(box, enc.data.errors || ["Gagal mengenkripsi."]);
    return;
  }
  const e = enc.data;

  // 2) daftarkan user pengirim bila belum ada (public key saja)
  let me = keys;
  if (!me.userId) {
    const name = $("#f-nama").value.trim() || "Pengirim";
    const u = await api("/api/users", {
      name, role: "sender", pub_e: me.public.e, pub_n: me.public.n,
    });
    if (u.status !== 201 || !u.data.ok) {
      showErrors(box, u.data.errors || ["Gagal mendaftarkan pengirim."]);
      return;
    }
    me.userId = u.data.user.id;
    me.name = u.data.user.name;
    STORE.set("sender", me);
  }

  // 3) kirim paket (ciphertext + signature + public key pengirim implicit via sender_id)
  const snd = await api("/api/send", {
    sender_id: me.userId,
    center_id: center.id,
    ciphertext: e.ciphertext,
    original_ciphertext: e.ciphertext,   // salinan asli untuk tombol Reset
    signature: state.signature,
  });
  if (snd.status !== 201 && !snd.data.ok) {
    showErrors(box, snd.data.errors || ["Gagal mengirim paket."]);
    return;
  }

  const rows = (e.steps.find((s) => s.tabel).tabel || [])
    .map((t) => `<tr><td class="num break">${t.blok}</td><td class="num break">${t.cipher}</td></tr>`)
    .join("");

  const charChips = [...state.payload]
    .map((c) => `<span class="chip">${esc(c)}=${String(c.charCodeAt(0)).padStart(3, "0")}</span>`)
    .join("");

  box.classList.remove("hidden");
  box.innerHTML =
    block("1. PLAINTEXT", `<div class="mono break">${esc(state.payload)}</div>`) +
    block("2. KONVERSI ASCII (3 digit/karakter)", `<div class="chips">${charChips}</div>`) +
    block("3. PEMBENTUKAN BLOK", `
      <div style="color:var(--muted);font-size:12.5px">
        n pusat = ${e.public.n} memuat ${e.digits} digit →
        <strong>${e.block_size} karakter per blok</strong> (nilai blok &lt; n).</div>
      <div class="mono break" style="margin-top:8px">${esc(e.digit_string)}</div>
      <div class="kv">jumlah blok: <b>${e.num_blocks}</b></div>`) +
    block(`4. CIPHER = BLOK<sup>e</sup> MOD N (e=${e.public.e}, n=${e.public.n})`, `
      <div class="scroll-x"><table class="tbl">
        <thead><tr><th>Nilai Blok</th><th>Ciphertext</th></tr></thead>
        <tbody>${rows}</tbody></table></div>`) +
    block("PAKET TERKIRIM", `
      ${kv("id pesan (database)", snd.data.message.id)}
      ${kv("tujuan", center.name + " (id " + center.id + ")")}
      ${kv("ciphertext", e.num_blocks + " blok")}
      ${kv("signature", state.signature)}
      ${kv("public key pengirim", "(e=" + keys.public.e + ", n=" + keys.public.n + ")")}
      <div class="mono break" style="margin-top:8px;color:var(--muted);font-size:12px">
        ${esc(e.ciphertext.join(", "))}</div>
      <div class="msg-ok" style="margin-top:12px">
        Tersimpan di database — buka tab <strong>Pusat Darurat</strong> untuk
        mendekripsi &amp; memverifikasi.</div>`);

  setStepper(4);
  toast("Paket SOS terkirim ke pusat darurat", "ok");
});

/* ---------------- init ---------------- */
window.addEventListener("DOMContentLoaded", () => {
  $("#f-waktu").value = nowStamp();
  const stored = STORE.get("sender");
  if (stored && stored.private) {
    unlock("panel-2");
    $("#btn-sign").disabled = false;
    if (stored.name) $("#f-nama").value = stored.name;
    toast("Kunci pengirim tersimpan di browser", "ok");
  }
  loadCenters();
  setStepper(1);
});
