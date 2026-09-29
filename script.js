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

  const galleryImages = document.querySelectorAll(
    ".detail-gallery img, .gallery-card img, .mini-gallery-card img"
  );
  if (galleryImages.length) {
    const lightbox = document.createElement("div");
    lightbox.className = "lightbox";
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.setAttribute("aria-label", "Expanded image preview");
    lightbox.hidden = true;
    lightbox.innerHTML = `
      <div class="lightbox-backdrop" data-lightbox-close></div>
      <div class="lightbox-panel">
        <button class="lightbox-close" type="button" aria-label="Close expanded image" data-lightbox-close>Close <span aria-hidden="true">×</span></button>
        <img class="lightbox-image" alt="">
        <p class="lightbox-caption"></p>
      </div>
    `;
    document.body.appendChild(lightbox);

    const expandedImage = lightbox.querySelector(".lightbox-image");
    const caption = lightbox.querySelector(".lightbox-caption");
    const closeButton = lightbox.querySelector(".lightbox-close");
    let lastFocusedImage = null;

    function closeLightbox() {
      lightbox.hidden = true;
      document.body.classList.remove("lightbox-open");
      if (lastFocusedImage) lastFocusedImage.focus();
    }

    function openLightbox(image) {
      lastFocusedImage = image;
      expandedImage.src = image.currentSrc || image.src;
      expandedImage.alt = image.alt;
      caption.textContent = image.closest("figure")?.querySelector("figcaption")?.textContent || image.alt;
      lightbox.hidden = false;
      document.body.classList.add("lightbox-open");
      closeButton.focus();
    }

    galleryImages.forEach((image) => {
      image.tabIndex = 0;
      image.setAttribute("role", "button");
      image.setAttribute("aria-label", `View larger image: ${image.alt}`);
      image.addEventListener("click", () => openLightbox(image));
      image.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openLightbox(image);
        }
      });
    });

    lightbox.addEventListener("click", (event) => {
      if (event.target.hasAttribute("data-lightbox-close")) closeLightbox();
    });
    document.addEventListener("keydown", (event) => {
      if (!lightbox.hidden && event.key === "Escape") closeLightbox();
    });
  }
})();