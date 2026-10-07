/* ==================================================================
   attacker.js - Halaman Penyadap (Man-in-the-Middle)

   Peran pihak ketiga: menyadap paket (metadata terbuka), menyusun
   payload palsu, mengenkripsi ulang dengan PUBLIC key pusat darurat,
   lalu menempelkan signature LAMA hasil sadapan.

   Penyerang TIDAK punya private key apa pun:
   - tidak bisa baca isi (butuh private key pusat)
   - tidak bisa buat signature baru (butuh private key pengirim)
   ================================================================== */

const state = {
  packets: [],     // semua paket hasil sadapan
  selected: null,  // paket terpilih
};

/* ---------------- 1. Muat paket disadap ---------------- */
$("#btn-load").addEventListener("click", loadPackets);

async function loadPackets(silent = false) {
  const box = $("#packets-result");
  const { status, data } = await apiGet("/api/inbox");
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Gagal memuat paket."]);
    return;
  }
  $("#load-hint").textContent = `${data.messages.length} paket di jalan`;

  if (!data.messages.length) {
    box.classList.remove("hidden");
    box.innerHTML = block("PAKET DISADAP",
      `<em>Belum ada paket. Kirim dulu pesan dari tab <strong>Pengirim</strong>.</em>`);
    if (!silent) toast("Belum ada paket di jalan", "err");
    return;
  }

  state.packets = data.messages;
  const rows = data.messages.map((m) => {
    const sel = state.selected && state.selected.id === m.id ? ' class="row-click selected"' : ' class="row-click"';
    const st = m.status === "valid" ? `<span class="chip ok">VALID</span>`
      : m.status === "invalid" ? `<span class="chip bad">INVALID</span>`
      : `<span class="chip">pending</span>`;
    const tam = m.tampered ? ` <span class="chip bad">SUDAH DISERANG</span>` : "";
    return `<tr${sel} data-id="${m.id}">
      <td class="num">${m.id}</td>
      <td>${esc(m.sender_name)} → ${esc(m.center_name)}</td>
      <td class="num">${m.ciphertext.length} blok</td>
      <td>${st}${tam}</td>
      <td class="break" style="font-size:11px">${esc(String(m.signature).slice(0, 20))}…</td>
      <td>${esc((m.created_at || "").replace("T", " ").slice(0, 19))}</td>
    </tr>`;
  }).join("");

  box.classList.remove("hidden");
  box.innerHTML = block("PAKET DISADAP — klik untuk dibajak (klik baris: signature terlihat, isi tidak)", `
    <div class="scroll-x"><table class="tbl">
      <thead><tr><th>Id</th><th>Jalur</th><th>Ukuran</th><th>Status</th>
        <th>Signature (disadap)</th><th>Masuk</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`);

  box.querySelectorAll(".row-click").forEach((tr) =>
    tr.addEventListener("click", () => selectPacket(Number(tr.dataset.id))));
}

function selectPacket(id) {
  state.selected = state.packets.find((p) => p.id === id) || null;
  if (!state.selected) return;
  loadPackets(true);   // render ulang tanda terpilih
  unlock("panel-attack");
  $("#btn-attack").disabled = false;
  $("#btn-reset").disabled = false;
  setStepper(2);
  toast(`Paket #${id} dibajak — signature terekam, isi tertutup`, "err");
}

/* ---------------- 2. Serang / Reset ---------------- */
$("#btn-attack").addEventListener("click", async () => {
  const box = $("#attack-result");
  if (!state.selected) { showErrors(box, ["Pilih paket dulu (klik baris)."]); return; }

  const payload = {
    nama: $("#a-nama").value.trim(),
    lat: $("#a-lat").value.trim(),
    lon: $("#a-lon").value.trim(),
    waktu: $("#a-waktu").value.trim() || nowStamp(),
    pesan: $("#a-pesan").value.trim(),
  };
  if (!payload.nama || !payload.pesan) {
    showErrors(box, ["Nama dan pesan palsu wajib diisi."]);
    return;
  }

  const { status, data } = await api(`/api/inbox/${state.selected.id}/tamper`,
    { mode: "payload-palsu", payload });
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Serangan gagal."]);
    toast("Serangan gagal", "err");
    return;
  }

  // sinkronkan state lokal
  state.selected.ciphertext = data.cipher;
  state.selected.tampered = true;
  state.selected.status = data.status;
  loadPackets(true);

  box.classList.remove("hidden");
  box.innerHTML =
    block("ISI PAKET TELAH DIGANTI", `
      ${kv("id paket", data.id)}
      ${kv("payload palsu terkirim", data.text)}
      ${kv("signature", state.selected.signature + " (signature LAMA, tidak diubah)")}
      <div class="mono break" style="margin-top:8px;color:var(--muted);font-size:12px">
        ciphertext baru: ${esc(data.cipher.join(", "))}</div>`) +
    block("KENAPA INI TETAP AKAN GAGAL?", `
      <div class="chips">
        <span class="chip ok">isi diganti (public key pusat)</span>
        <span class="chip bad">signature tetap lama (tak punya private key pengirim)</span>
      </div>
      <div style="margin-top:10px;font-size:13px;color:var(--muted)">
        Saat pusat darurat memverifikasi:
        <code>signature<sup>e</sup> mod n</code> menghasilkan hash dari isi <strong>ASLI</strong>,
        sedangkan hash ulang isi <strong>PALSU</strong> berbeda →
        <strong class="badge-bad">SIGNATURE TIDAK VALID</strong>.
      </div>`);

  unlock("panel-handoff");
  $("#handoff-result").classList.remove("hidden");
  $("#handoff-result").innerHTML = block("4. SELANJUTNYA: BUKA TAB PUSAT DARURAT", `
    <div class="msg-error">
      Paket <strong>#${data.id}</strong> sudah berisi payload palsu.
      Muat inbox → klik pesan → <strong>Verifikasi Signature</strong> →
      hasilnya diharapkan <strong>✗ SOS TIDAK VALID</strong>.
    </div>`);
  setStepper(3);
  toast(`Paket #${data.id} berhasil dibajak`, "err");
});

$("#btn-reset").addEventListener("click", async () => {
  const box = $("#attack-result");
  if (!state.selected) { showErrors(box, ["Pilih paket dulu (klik baris)."]); return; }

  const { status, data } = await api(`/api/inbox/${state.selected.id}/reset`);
  if (status !== 200 || !data.ok) {
    showErrors(box, data.errors || ["Reset gagal."]);
    return;
  }
  state.selected.ciphertext = data.cipher;
  state.selected.tampered = false;
  state.selected.status = data.status;
  loadPackets(true);

  box.classList.remove("hidden");
  box.innerHTML = block("PAKET DIKEMBALIKAN KE ASLI", `
    ${kv("id paket", data.id)}
    ${kv("tampered", String(data.tampered))}
    <div style="margin-top:8px;font-size:13px;color:var(--muted)">
      Ciphertext dipulihkan dari salinan <code>original_ciphertext</code> —
      verifikasi di pusat darurat kembali <strong class="badge-ok">SOS VALID</strong>.
    </div>`);

  $("#handoff-result").classList.remove("hidden");
  $("#handoff-result").innerHTML = block("4. SELANJUTNYA: BUKA TAB PUSAT DARURAT", `
    <div class="msg-ok">Paket asli dipulihkan — verifikasi ulang di pusat darurat
    akan kembali <strong>SOS VALID</strong>.</div>`);
  setStepper(3);
  toast("Paket dipulihkan", "ok");
});

/* ---------------- init ---------------- */
window.addEventListener("DOMContentLoaded", () => {
  // waktu dipertahankan sama dengan paket asli (penyerang sengaja menyamarkan)
  $("#a-waktu").value = "2026-10-07 13:20:15";
  setStepper(1);
});

/* refresh daftar tiap kembali ke tab ini */
window.addEventListener("focus", () => loadPackets(true));
