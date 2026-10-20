import { initLocalTime } from "./js/clock.js";
import { initScrollReveal } from "./js/scroll-reveal.js";
import { initContactForm } from "./js/contact-form.js";
import { initLightbox } from "./js/lightbox.js";

// Each initializer skips pages that do not contain its feature.
initLocalTime();
initScrollReveal();
initContactForm();
initLightbox();
