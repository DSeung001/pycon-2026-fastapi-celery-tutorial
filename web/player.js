const statusEl = document.getElementById("status");
const startBtn = document.getElementById("start-btn");
const playerEl = document.getElementById("hls-player");

function setStatus(text) {
  statusEl.textContent = `상태: ${text}`;
}

function attachHls(url) {
  if (window.Hls && window.Hls.isSupported()) {
    const hls = new window.Hls();
    hls.loadSource(url);
    hls.attachMedia(playerEl);
    return;
  }
  playerEl.src = url;
}

async function pollJob(jobId) {
  for (;;) {
    const response = await fetch(`/jobs/${jobId}`);
    const data = await response.json();

    setStatus(`${data.status} (${jobId})`);

    if (data.status === "completed" && data.output_url) {
      attachHls(data.output_url);
      return;
    }
    if (data.status === "failed") {
      throw new Error(data.error || "encoding failed");
    }
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }
}

startBtn.addEventListener("click", async () => {
  try {
    setStatus("작업 요청 중");
    const response = await fetch("/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "input.mp4" }),
    });
    const data = await response.json();
    await pollJob(data.job_id);
    setStatus("완료");
  } catch (error) {
    setStatus(`실패: ${error.message}`);
  }
});

