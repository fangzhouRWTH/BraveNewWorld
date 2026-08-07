const form = document.querySelector("#controls");
const canvas = document.querySelector("#plot");
const statusNode = document.querySelector("#status");
const metricsNode = document.querySelector("#metrics");
const exportButton = document.querySelector("#export");
const resetButton = document.querySelector("#reset");
let latestTrace = null;

function requestFromForm() {
  return Object.fromEntries(
    [...new FormData(form).entries()].map(([key, value]) => [key, Number(value)])
  );
}

function draw(trace) {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = Math.min(480, Math.max(280, width * 0.55));
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, width, height);

  const pad = { left: 52, right: 18, top: 22, bottom: 38 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const values = trace.points.flatMap(point => [point.input, point.output]);
  let yMin = Math.min(...values, 0);
  let yMax = Math.max(...values, 0);
  const margin = Math.max((yMax - yMin) * 0.12, 0.1);
  yMin -= margin;
  yMax += margin;
  const tMax = trace.points.at(-1).time_s;
  const x = value => pad.left + (value / tMax) * plotWidth;
  const y = value => pad.top + (1 - (value - yMin) / (yMax - yMin)) * plotHeight;

  ctx.strokeStyle = "#d9dfda";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad.left, pad.top);
  ctx.lineTo(pad.left, height - pad.bottom);
  ctx.lineTo(width - pad.right, height - pad.bottom);
  ctx.stroke();

  ctx.fillStyle = "#647069";
  ctx.font = "12px system-ui";
  ctx.fillText(yMax.toFixed(2), 5, pad.top + 4);
  ctx.fillText(yMin.toFixed(2), 5, height - pad.bottom + 4);
  ctx.fillText("0 s", pad.left, height - 12);
  ctx.fillText(`${tMax.toFixed(2)} s`, width - pad.right - 42, height - 12);

  function line(key, color) {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    trace.points.forEach((point, index) => {
      const method = index === 0 ? "moveTo" : "lineTo";
      ctx[method](x(point.time_s), y(point[key]));
    });
    ctx.stroke();
  }
  line("input", "#bb5a31");
  line("output", "#126b50");

  ctx.fillStyle = "#bb5a31";
  ctx.fillRect(pad.left + 8, pad.top + 2, 14, 3);
  ctx.fillStyle = "#17211d";
  ctx.fillText("输入 u", pad.left + 28, pad.top + 7);
  ctx.fillStyle = "#126b50";
  ctx.fillRect(pad.left + 94, pad.top + 2, 14, 3);
  ctx.fillStyle = "#17211d";
  ctx.fillText("输出 y", pad.left + 114, pad.top + 7);
}

function showMetrics(trace) {
  const items = [
    ["稳态目标", trace.metrics.steady_state_target.toFixed(6)],
    ["末端输出", trace.metrics.final_output.toFixed(6)],
    ["末端误差", trace.metrics.final_error.toExponential(3)],
    ["轨迹哈希", trace.trace_hash.slice(0, 12)],
  ];
  metricsNode.replaceChildren(...items.map(([label, value]) => {
    const wrapper = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");
    term.textContent = label;
    detail.textContent = value;
    wrapper.append(term, detail);
    return wrapper;
  }));
}

async function simulate(event) {
  event?.preventDefault();
  statusNode.classList.remove("error");
  statusNode.textContent = "正在运行确定性仿真…";
  exportButton.disabled = true;
  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestFromForm()),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "仿真请求失败");
    latestTrace = payload;
    draw(payload);
    showMetrics(payload);
    statusNode.textContent = `${payload.engine_version} · ${payload.points.length} 个真实采样点`;
    exportButton.disabled = false;
  } catch (error) {
    latestTrace = null;
    statusNode.classList.add("error");
    statusNode.textContent = error.message;
  }
}

form.addEventListener("submit", simulate);
resetButton.addEventListener("click", () => { form.reset(); simulate(); });
exportButton.addEventListener("click", () => {
  if (!latestTrace) return;
  const blob = new Blob([JSON.stringify(latestTrace, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${latestTrace.demo_id}-${latestTrace.trace_hash.slice(0, 12)}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
});
window.addEventListener("resize", () => { if (latestTrace) draw(latestTrace); });
simulate();
