export function initLocalTime() {
  const timeZone = "America/New_York";
  const localTime = document.getElementById("local-time");
  if (!localTime) return;

  function tick() {
    try {
      localTime.textContent = new Intl.DateTimeFormat("en-US", {
        hour: "numeric",
        minute: "2-digit",
        timeZone,
      }).format(new Date());
    } catch {
      localTime.textContent = "";
    }
  }
  tick();
  setInterval(tick, 30000);
}
