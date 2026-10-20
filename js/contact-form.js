export function initContactForm() {
  const form = document.getElementById("contact-form");
  if (!form) return;

  const status = document.getElementById("form-status");

  // Demo feedback only. Connect a delivery service here before accepting messages.
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const email = form.elements.namedItem("email").value || "you";
    if (status) status.textContent = "Thanks — message queued. I'll reply to " + email + ".";
    form.reset();
  });
}
