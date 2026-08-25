(() => {
  const TIMEZONE = "America/New_York";

  function tick() {
    const el = document.getElementById("local-time");
    if (!el) return;
    try {
      el.textContent = new Intl.DateTimeFormat("en-US", {
        hour: "numeric",
        minute: "2-digit",
        timeZone: TIMEZONE,
      }).format(new Date());
    } catch (e) {
      el.textContent = "";
    }
  }
  tick();
  setInterval(tick, 30000);

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
  );
  document.querySelectorAll(".rv").forEach((el) => io.observe(el));

  const form = document.getElementById("contact-form");
  const status = document.getElementById("form-status");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = form.email.value || "you";
      if (status) status.textContent = "Thanks — message queued. I'll reply to " + email + ".";
      form.reset();
    });
  }
})();
