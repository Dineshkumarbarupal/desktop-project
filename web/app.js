const state = { windows: [], selectedHwnd: null, toastTimer: null };
const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
function notify(message, isError = false) {
  const toast = $("toast"); toast.textContent = message;
  toast.style.background = isError ? "#8f343f" : "#202a40";
  toast.classList.add("show"); clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}
function renderWindows() {
  const query = $("searchInput").value.trim().toLocaleLowerCase();
  const visible = state.windows.filter((item) => item.title.toLocaleLowerCase().includes(query));
  $("windowCount").textContent = String(state.windows.length);
  $("resultCount").textContent = visible.length + " window" + (visible.length === 1 ? "" : "s");
  $("listStatus").textContent = "Scanned " + new Date().toLocaleTimeString();
  if (!visible.length) {
    $("windowRows").innerHTML = '<tr><td colspan="3" class="empty">' + (query ? "No matching windows found." : "No titled windows found.") + '</td></tr>';
    return;
  }
  $("windowRows").innerHTML = visible.map((item) =>
    '<tr class="window-row ' + (item.hwnd === state.selectedHwnd ? "selected" : "") + '" data-hwnd="' + item.hwnd + '">' +
    '<td title="' + escapeHtml(item.title) + '">' + escapeHtml(item.title) + '</td><td class="handle">' + item.hwnd +
    '</td><td>' + item.width + ' × ' + item.height + '</td></tr>').join("");
  document.querySelectorAll(".window-row").forEach((row) => row.addEventListener("click", () => selectWindow(Number(row.dataset.hwnd))));
}
function selectWindow(hwnd) {
  state.selectedHwnd = hwnd;
  const picked = state.windows.find((item) => item.hwnd === hwnd);
  if (!picked) return;
  $("selectedName").textContent = picked.title;
  $("controlWindowTitle").textContent = picked.title;
  $("posX").value = picked.x; $("posY").value = picked.y;
  $("winWidth").value = picked.width; $("winHeight").value = picked.height;
  $("noSelection").classList.add("hidden"); $("controlContent").classList.remove("hidden");
  renderWindows();
}
async function refreshWindows() {
  $("listStatus").textContent = "Scanning…";
  try {
    const result = await eel.get_windows()();
    if (!result || !result.ok) throw new Error((result && result.error) || "Could not enumerate windows.");
    state.windows = result.windows || [];
    if (!state.windows.some((item) => item.hwnd === state.selectedHwnd)) {
      state.selectedHwnd = null; $("selectedName").textContent = "None";
      $("noSelection").classList.remove("hidden"); $("controlContent").classList.add("hidden");
    }
    renderWindows();
    if (!state.windows.length) notify("No visible titled windows were found.");
  } catch (error) { $("listStatus").textContent = "Scan failed"; notify(error.message || String(error), true); }
}
async function runAction(action) {
  if (state.selectedHwnd === null) return notify("Select a window first.", true);
  try {
    const result = await eel.control_window(state.selectedHwnd, action)();
    if (!result || !result.ok) throw new Error((result && result.error) || "Window action failed.");
    notify(result.message); setTimeout(refreshWindows, 350);
  } catch (error) { notify(error.message || String(error), true); }
}
async function applyBounds() {
  if (state.selectedHwnd === null) return notify("Select a window first.", true);
  const values = ["posX", "posY", "winWidth", "winHeight"].map((id) => Number($(id).value));
  if (values.some((value) => !Number.isFinite(value))) return notify("Enter valid numbers for position and size.", true);
  try {
    const result = await eel.move_resize_window(state.selectedHwnd, ...values)();
    if (!result || !result.ok) throw new Error((result && result.error) || "Could not move or resize the window.");
    notify(result.message); setTimeout(refreshWindows, 350);
  } catch (error) { notify(error.message || String(error), true); }
}
$("refreshBtn").addEventListener("click", refreshWindows);
$("searchInput").addEventListener("input", renderWindows);
document.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => runAction(button.dataset.action)));
$("applyBoundsBtn").addEventListener("click", applyBounds);
$("closeBtn").addEventListener("click", () => {
  if (confirm("Send a close request to this window? The application may prompt to save unsaved work.")) runAction("close");
});
if (typeof eel === "undefined") notify("Eel bridge not found. Start this app with python main.py.", true);
else refreshWindows();
