const API = "http://127.0.0.1:8000";

const VERDICT_COLORS = {
  "Real": "#00ff9d",
  "Mostly Real": "#66ffcc",
  "Suspicious": "#ffd700",
  "Fake": "#ff4d4d",
};

// 🔹 Format numbers safely
function fmt(val, decimals = 2) {
  const n = parseFloat(val);
  return isNaN(n) ? "--" : n.toFixed(decimals);
}


// 🔹 Loading UI
function setLoading() {
  ["imageScore", "textScore", "finalScore", "verdict", "confidence"]
    .forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerText = "--";
    });

  document.getElementById("bar").style.width = "0%";
  document.getElementById("analysisText").innerText = "Analyzing...";
}


// 🔹 Populate UI (SAFE + DEBUG)
function populateResult(data) {
  console.log("📊 DATA RECEIVED:", data);

  if (!data) return;

  document.getElementById("imageScore").innerText = fmt(data.image_score);
  document.getElementById("textScore").innerText  = fmt(data.text_score);
  document.getElementById("finalScore").innerText = fmt(data.final_score);

  // Confidence
  const confidence = parseFloat(data.confidence) || 0;
  document.getElementById("confidence").innerText = confidence.toFixed(1) + "%";
  document.getElementById("bar").style.width = confidence + "%";

  // Verdict
  const verdictEl = document.getElementById("verdict");
  verdictEl.innerText = data.verdict || "--";
  verdictEl.style.color = VERDICT_COLORS[data.verdict] || "#fff";

  // Analysis
  document.getElementById("analysisText").innerText =
    data.analysis || data.fact_analysis || "No analysis available.";

  // Keywords
  document.getElementById("fakeCount").innerText    = data.fake_words || 0;
  document.getElementById("realCount").innerText    = data.real_words || 0;
  document.getElementById("trustedScore").innerText = data.trusted_score || 0;
}


// 🔥 FIXED SCAN FUNCTION (MAIN ISSUE FIXED HERE)
async function scan() {
  const url = document.getElementById("url").value.trim();

  if (!url || !url.startsWith("http")) {
    alert("Please enter a valid URL");
    return;
  }

  setLoading();

  try {
    const res = await fetch(`${API}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();
    console.log("✅ Scan result:", data);

    if (!data || data.verdict === "Error") {
      alert("Analysis failed");
      return;
    }

    // ⏳ SMALL DELAY → FIXES FAST UI ISSUE
    setTimeout(() => {
      populateResult(data);
    }, 200);

    // ⏳ LOAD HISTORY AFTER UI UPDATE
    setTimeout(() => {
      loadHistory();
    }, 500);

  } catch (err) {
    console.error("❌ Scan error:", err);
    alert("Backend not running");
  }
}


// 🔹 LOAD HISTORY
async function loadHistory() {
  try {
    const res = await fetch(`${API}/history`);
    const data = await res.json();

    console.log("📜 History:", data);

    const table = document.getElementById("historyTable");

    if (!data || data.length === 0) {
      table.innerHTML = `<tr>
        <td colspan="6" style="text-align:center;opacity:0.6;">
          No history yet
        </td>
      </tr>`;
      return;
    }

    table.innerHTML = data.map(row => {
      const color = VERDICT_COLORS[row.verdict] || "#fff";

      return `
        <tr>
          <td>${row.id}</td>
          <td>${row.title || "-"}</td>
          <td>${fmt(row.image_score)}</td>
          <td>${fmt(row.text_score)}</td>
          <td>${fmt(row.final_score)}</td>
          <td style="color:${color}; font-weight:bold;">
            ${row.verdict}
          </td>
        </tr>
      `;
    }).join("");

  } catch (err) {
    console.error("❌ History error:", err);
  }
}


// 🚀 AUTO LOAD
window.onload = loadHistory;