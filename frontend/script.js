async function scan() {
  let url = document.getElementById("url").value;

  if (!url) {
    alert("Enter URL first");
    return;
  }

  try {
    let res = await fetch("http://127.0.0.1:8000/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: url })
    });

    let data = await res.json();
    document.getElementById("imageScore").innerText = data.image_score;
    document.getElementById("textScore").innerText = data.text_score;
    document.getElementById("finalScore").innerText = data.final_score;

    let verdict = document.getElementById("verdict");
    verdict.innerText = data.verdict;

    verdict.className =
      data.verdict === "Real" ? "green" :
      data.verdict === "Suspicious" ? "yellow" : "red";

    loadHistory();

  } catch (err) {
    console.error(err);
    alert("Server not running");
  }
}

async function loadHistory() {
  let res = await fetch("http://127.0.0.1:8000/history");
  let data = await res.json();

  let table = document.getElementById("historyTable");
  table.innerHTML = "";

  data.forEach(row => {
    table.innerHTML += `
      <tr>
        <td>${row.id}</td>
        <td>${row.title}</td>
        <td>${row.image_score}</td>
        <td>${row.text_score}</td>
        <td>${row.final_score}</td>
        <td>${row.verdict}</td>
      </tr>
    `;
  });
}

window.onload = loadHistory;