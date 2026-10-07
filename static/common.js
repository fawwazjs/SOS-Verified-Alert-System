/* ==================================================================
   common.js - utilitas UI bersama (kedua halaman)
   Tidak ada kriptografi di browser: semua perhitungan di server (rsa.py).
   Private key hanya disimpan di localStorage, dikirim per request.
   ================================================================== */

const $ = (sel) => document.querySelector(sel);

/* ---------- localStorage ---------- */
const STORE = {
  get(role) {
    try { return JSON.parse(localStorage.getItem("sos." + role)) || null; }
    catch { return null; }
  },
  set(role, data) {
    // data: { userId, name, private: {d,n}, public: {e,n} }
    localStorage.setItem("sos." + role, JSON.stringify(data));
  },
  clear(role) { localStorage.removeItem("sos." + role); },
};

/* ---------- http ---------- */
async function api(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() =>
    ({ ok: false, errors: ["Respons server tidak valid."] }));
  return { status: res.status, data };
}

async function apiGet(url) {
  const res = await fetch(url);
  const data = await res.json().catch(() =>
    ({ ok: false, errors: ["Respons server tidak valid."] }));
  return { status: res.status, data };
}

/* ---------- html helpers ---------- */
function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function toast(msg, type = "") {
  const t = $("#toast");
  if (!t) return;
  t.textContent = msg;
  t.className = "toast " + type;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.add("hidden"), 3200);
}

function nowStamp() {
  const d = new Date(), p = (x) => String(x).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ` +
         `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

function setStepper(n) {
  document.querySelectorAll("#stepper .step").forEach((el) => {
    const s = Number(el.dataset.step);
    el.classList.toggle("active", s === n);
    el.classList.toggle("done", s < n);
  });
}

function unlock(panelId) {
  const el = $("#" + panelId);
  if (el) el.classList.remove("locked");
}

function block(title, innerHTML) {
  return `<div class="step-block">
    <div class="bhead">${title}</div>
    <div class="bbody">${innerHTML}</div>
  </div>`;
}

function kv(label, value) {
  return `<div class="kv">${esc(label)}: <b class="break">${esc(value)}</b></div>`;
}

function showErrors(container, errors) {
  container.innerHTML = `<div class="msg-error"><strong>Validasi gagal:</strong><br>` +
    (errors || []).map((e) => "&bull; " + esc(e)).join("<br>") + `</div>`;
  container.classList.remove("hidden");
}

function powTable(logPow) {
  let rows = "";
  (logPow || []).forEach((l) => {
    if (l.iterasi !== undefined) {
      rows += `<tr><td>${l.iterasi}</td><td>${l.bit}</td><td>${esc(l.aksi)}</td>
               <td class="num">${l.nilai}</td></tr>`;
    }
  });
  return `<div class="scroll-x"><table class="tbl">
    <thead><tr><th>Iter</th><th>Bit</th><th>Aksi</th><th>Nilai</th></tr></thead>
    <tbody>${rows}</tbody></table></div>`;
}

function chipsFromAscii(ascii, text, max = 40) {
  let out = "";
  ascii.slice(0, max).forEach((a, i) => {
    out += `<span class="chip">${esc(text[i])}=${a}</span>`;
  });
  if (ascii.length > max) out += `<span class="chip">... +${ascii.length - max} lainnya</span>`;
  return out;
}

/* ---------- render log pembangkitan kunci (dipakai kedua halaman) ---------- */
function renderKeyLogs(title, key) {
  let html = `<h4 class="section-title">${title}</h4>`;
  key.logs.forEach((stage) => {
    let body = "";
    (stage.langkah || []).forEach((l) => {
      if (l.iterasi !== undefined && l.r !== undefined) {
        body += kv(`iterasi ${l.iterasi}`, `r = ${l.r}, x = ${l.x}, y = ${l.y}`);
      } else {
        let n = 0;
        if (l.hasil) {
          const bad = /BUKAN|TIDAK ADA|!=/.test(String(l.hasil));
          body += `<div class="kv"><b class="${bad ? "badge-bad" : "badge-ok"} break">${esc(l.hasil)}</b></div>`;
          n++;
        }
        if (l.cek) { body += kv("cek", l.cek); n++; }
        if (l.rumus) {
          body += l.substitusi ? kv(l.rumus, l.substitusi)
                               : `<div class="kv"><b class="break">${esc(l.rumus)}</b></div>`;
          n++;
        }
        if (l.identitas) { body += kv("identitas Bezout", l.identitas); n++; }
        if (l.verifikasi) { body += kv("verifikasi", l.verifikasi); n++; }
        if (n === 0) body += Object.entries(l)
          .map(([k, v]) => kv(k, typeof v === "object" ? JSON.stringify(v) : v)).join("");
      }
    });
    html += block(stage.tahap, body || "<em>(tidak ada langkah)</em>");
  });

  html += block("HASIL KUNCI", `
    <div>Public Key (e, n) &nbsp;
      <span class="keypill pub">e = ${key.public.e}</span>
      <span class="keypill pub">n = ${key.public.n}</span></div>
    <div style="margin-top:8px">Private Key (d, n) &nbsp;
      <span class="keypill priv">d = ${key.private.d}</span>
      <span class="keypill priv">n = ${key.private.n}</span>
      <span class="hint">→ disimpan hanya di localStorage, tidak dikirim ke database</span></div>
    <div style="margin-top:8px;color:var(--muted);font-size:12.5px">
      phi(n) = ${key.phi} &nbsp;|&nbsp; verifikasi (e&times;d) mod phi =
      ${key.ed_mod_phi}
    </div>`);
  return html;
}
