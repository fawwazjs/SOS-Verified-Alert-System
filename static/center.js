/* ==================================================================
   center.js - Halaman Pusat Darurat
   Alur: Keygen pusat -> Inbox (database) -> Dekripsi -> Verifikasi
   Private key pusat hanya di localStorage; dikirim per request lalu dibuang.
   ================================================================== */

const state = {
  me: null,            // {userId, name, private, public}
  selectedId: null,
  plaintext: null,     // hasil dekripsi terakhir (untuk tombol serangan)
};

const privateBody = () => state.me ? { private: state.me.private } : {};

/* ---------------- Panel: Key Generation ---------------- */
$("#btn-fill").addEventListener("click", () => {
  $("#c-p").value = 31627;
  $("#c-q").value = 31649;
  $("#c-e").value = 13;
});

$("#btn-genkey").addEventListener("click", async () => {
  const box = $("#key-result");
  const { status, data } = await api("/api/keygen", {
    p: $("#c-p").value, q: $("#c-q").value, e: $("#c-e").value,
  });
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal membuat kunci."]);
    toast("Pembangkitan kunci gagal", "err");
    return;
  }

  // daftarkan pusat darurat (hanya PUBLIC KEY yang masuk database)
  const name = $("#c-nama").value.trim() || "Pusat Darurat";
  const u = await api("/api/users", {
    name, role: "center", pub_e: data.public.e, pub_n: data.public.n,
  });
  if (u.status !== 201 || !u.data.ok) {
    showErrors(box, u.data.errors || ["Gagal mendaftarkan pusat darurat."]);
    return;
  }

  state.me = {
    userId: u.data.user.id, name: u.data.user.name,
    private: data.private, public: data.public,
  };
  STORE.set("center", state.me);   // private key -> localStorage saja

  box.classList.remove("hidden");
  box.innerHTML = `<div class="msg-ok">✓ Kunci pusat darurat dibuat (id user ${u.data.user.id}).
    Public key terdaftar di database; private key hanya di browser.</div>` +
    renderKeyLogs("Kunci Pusat Darurat", data);

  unlock("panel-4");
  $("#btn-inbox").disabled = false;
  setStepper(2);
  toast("Pusat darurat siap menerima", "ok");
});

/* ---------------- Inbox (dari database) ---------------- */
$("#btn-inbox").addEventListener("click", loadInbox);

async function loadInbox() {
  if (!state.me) { toast("Buat kunci pusat darurat dulu", "err"); return; }
  const box = $("#inbox-result");
  const { status, data } = await apiGet(`/api/inbox?center_id=${state.me.userId}`);
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal memuat inbox."]);
    return;
  }
  $("#inbox-hint").textContent = `${data.messages.length} pesan · pusat #${state.me.userId}`;

  if (!data.messages.length) {
    box.classList.remove("hidden");
    box.innerHTML = block("INBOX",
      `<em>Inbox kosong. Kirim dulu pesan dari tab <strong>Pengirim</strong>.</em>`);
    return;
  }

  const rows = data.messages.map((m) => {
    const st = m.status === "valid" ? `<span class="chip ok">VALID</span>`
      : m.status === "invalid" ? `<span class="chip bad">INVALID</span>`
      : `<span class="chip">pending</span>`;
    const tam = m.tampered ? ` <span class="chip bad">DITAMPER</span>` : "";
    return `<tr class="row-click" data-id="${m.id}">
      <td class="num">${m.id}</td>
      <td>${esc(m.sender_name)}</td>
      <td class="num">${m.ciphertext.length} blok</td>
      <td>${st}${tam}</td>
      <td class="break" style="font-size:11px">${esc(String(m.signature).slice(0, 18))}…</td>
      <td>${esc((m.created_at || "").replace("T", " ").slice(0, 19))}</td>
    </tr>`;
  }).join("");

  box.classList.remove("hidden");
  box.innerHTML = block("INBOX (klik baris untuk dekripsi)", `
    <div class="scroll-x"><table class="tbl">
      <thead><tr><th>Id</th><th>Pengirim</th><th>Ukuran</th><th>Status</th>
        <th>Signature</th><th>Masuk</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`);

  box.querySelectorAll(".row-click").forEach((tr) =>
    tr.addEventListener("click", () => selectMessage(Number(tr.dataset.id))));
}

async function selectMessage(id) {
  state.selectedId = id;
  toast(`Pesan #${id} dipilih — mendekripsi...`, "ok");
  const okDec = await doDecrypt();
  if (okDec) {
    unlock("panel-5");
    $("#btn-verify").disabled = false;
    setStepper(3);
  }
}

/* ---------------- Dekripsi ---------------- */
async function doDecrypt() {
  const box = $("#decrypt-result");
  if (!state.selectedId) {
    showErrors(box, ["Pilih pesan dari inbox dulu."]);
    return false;
  }
  const { status, data } = await api(`/api/inbox/${state.selectedId}/decrypt`, privateBody());
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal mendekripsi."]);
    return false;
  }

  state.plaintext = data.plain;

  const rows = data.tabel.map((t) =>
    `<tr><td class="num break">${t.cipher}</td><td class="num break">${t.blok}</td>
      <td class="break">${t.blok}</td></tr>`).join("");

  let expiry = "";
  if (data.expiry.checked) {
    expiry = data.expiry.expired
      ? `<div class="msg-error"><strong>Alert Kadaluarsa</strong> — selisih
           ${data.expiry.delta_seconds}s (batas ${data.expiry.limit_seconds}s).</div>`
      : `<div class="msg-ok">Alert masih berlaku (selisih ${data.expiry.delta_seconds}s
           dari batas ${data.expiry.limit_seconds}s).</div>`;
  } else {
    expiry = `<div class="msg-error">${esc(data.expiry.reason)}</div>`;
  }

  const tamperWarn = data.tampered
    ? `<div class="msg-error">Kondisi <strong>MANIPULASI</strong> — signature tidak diubah
         penyerang, tapi isi berubah. Akan terdeteksi saat verifikasi.</div>` : "";

  const field = (k, v) => `<div class="field-card"><div class="fk">${k}</div>
    <div class="fv">${esc(v)}</div></div>`;

  box.classList.remove("hidden");
  box.innerHTML = tamperWarn +
    block("1. CIPHERTEXT DITERIMA", `<div class="mono break" style="font-size:12px">
      ${esc(data.cipher.join(", "))}</div>`) +
    block("2. &amp; 3. DEKRIPSI — blok = cipher<sup>d</sup> mod n", `
      <div class="scroll-x"><table class="tbl">
        <thead><tr><th>Ciphertext</th><th>Blok Hasil</th><th>Untuk ASCII</th></tr></thead>
        <tbody>${rows}</tbody></table></div>`) +
    block("4. HASIL DEKRIPSI (blocksToText)", `<div class="mono break">${esc(data.plain)}</div>`) +
    block("5. FIELD PESAN", `<div class="field-grid">
      ${field("Nama", data.fields.nama)}${field("Latitude", data.fields.lat)}
      ${field("Longitude", data.fields.lon)}${field("Waktu", data.fields.waktu)}
      ${field("Pesan", data.fields.pesan)}</div>`) +
    block("6. CEK KEDALUARSA (5 menit)", expiry);
  return true;
}

/* ---------------- Verifikasi ---------------- */
$("#btn-verify").addEventListener("click", async () => {
  const box = $("#verify-result");
  const { status, data } = await api(`/api/inbox/${state.selectedId}/verify`, privateBody());
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal verifikasi."]);
    return;
  }

  const match = data.valid;
  const banner = match
    ? `<div class="verify-banner valid"><h3>✓ SOS VALID</h3>
        <div class="verify-list">
          <div>✓ Pengirim Terverifikasi</div>
          <div>✓ Lokasi Tidak Dimodifikasi</div>
          <div>✓ Pesan Tidak Dimodifikasi</div>
        </div></div>`
    : `<div class="verify-banner invalid"><h3>✗ SOS TIDAK VALID — SIGNATURE TIDAK VALID</h3>
        <div class="verify-list">
          <div>✗ PESAN TELAH DIMODIFIKASI ATAU PALSU</div>
          <div>✗ Lokasi/Data Telah Dimanipulasi</div>
          <div>✗ Kemungkinan Hoax</div>
        </div></div>`;

  box.classList.remove("hidden");
  box.innerHTML =
    banner +
    block("VERIFIED HASH = signature<sup>e</sup> mod n (public key pengirim)", `
      ${kv("signature", data.signature)}
      ${kv("public key pengirim e", data.sender_public.e)}
      ${kv("public key pengirim n", data.sender_public.n)}
      <div style="margin-top:10px;color:var(--muted);font-size:12px">
        Proses square-and-multiply:</div>
      ${powTable(data.pow_log)}`) +
    block("PERBANDINGAN HASH", `
      <div class="compare">
        <div class="cc ${match ? "match" : "mismatch"}">
          <div class="ck">verifiedHash (dari signature)</div>
          <div class="cv">${data.verified_hash}</div></div>
        <div class="cc ${match ? "match" : "mismatch"}">
          <div class="ck">hash ulang (dari hasil dekripsi)</div>
          <div class="cv">${data.recomputed_hash}</div></div>
      </div>
      <div style="text-align:center;margin-top:14px;font-size:14px">
        ${match
          ? `<span class="badge-ok">✓ IDENTIK (${data.verified_hash} = ${data.recomputed_hash})</span>`
          : `<span class="badge-bad">✗ BERBEDA (${data.verified_hash} ≠ ${data.recomputed_hash})</span>`}
      </div>
      <div class="msg-${match ? "ok" : "error"}" style="margin-top:12px">
        Status pesan #${data.id} tersimpan di database:
        <strong>${data.status.toUpperCase()}</strong>
        ${data.tampered ? " · ditandai TAMPERED" : ""}
      </div>`);

  setStepper(4);
  toast(match ? "SOS VALID ✓" : "SIGNATURE TIDAK VALID ✗", match ? "ok" : "err");
});

/* ---------------- init ---------------- */
window.addEventListener("DOMContentLoaded", () => {
  const stored = STORE.get("center");
  if (stored && stored.private) {
    state.me = stored;
    if (stored.name) $("#c-nama").value = stored.name;
    unlock("panel-4");
    $("#btn-inbox").disabled = false;
    toast(`Pusat "${stored.name}" aktif dari localStorage`, "ok");
  } else {
    $("#btn-inbox").disabled = true;
  }
  setStepper(1);
});

/* otomatis muat ulang inbox tiap kembali ke tab ini (mis. setelah kirim dari Pengirim) */
window.addEventListener("focus", () => {
  if (state.me && !$("#panel-4").classList.contains("locked")) loadInbox();
});
