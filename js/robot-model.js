const VIEWER_TAG = "model-viewer";
const DEFINITION_TIMEOUT_MS = 15000;

async function waitForViewer() {
  let timeout;

  try {
    await Promise.race([
      customElements.whenDefined(VIEWER_TAG),
      new Promise((_, reject) => {
        timeout = window.setTimeout(() => {
          reject(
            new Error("The 3D viewer did not load. Check your internet connection and try again."),
          );
        }, DEFINITION_TIMEOUT_MS);
      }),
    ]);
  } finally {
    window.clearTimeout(timeout);
  }

  // Restore full resolution when stationary, but allow slower GPUs to reduce
  // resolution further while the visitor moves the camera.
  customElements.get(VIEWER_TAG).minimumRenderScale = 0.25;
}

export function initRobotModel(name) {
  const button = document.getElementById(`load-${name}-model`);
  const viewer = document.getElementById(`${name}-model`);
  const status = document.getElementById(`${name}-model-status`);
  if (!button || !viewer || !status) return;
  const source = viewer.getAttribute("src");

  function showReady() {
    button.hidden = true;
    viewer.removeAttribute("aria-busy");
    status.textContent = "Model ready. Drag to rotate; scroll or pinch to zoom.";
  }

  // Register once so retries cannot accumulate load/error handlers.
  viewer.addEventListener("load", showReady);

  viewer.addEventListener("error", () => {
    viewer.removeAttribute("src");
    viewer.removeAttribute("aria-busy");
    button.hidden = false;
    button.disabled = false;
    button.textContent = "Try loading again";
    status.textContent = "The 3D model could not be loaded. Check your connection, then try again.";
  });

  async function loadModel() {
    button.hidden = true;
    button.disabled = true;
    viewer.setAttribute("aria-busy", "true");
    status.textContent = "Preparing the 3D viewer...";

    try {
      await waitForViewer();
      if (viewer.loaded) {
        showReady();
        return;
      }
      status.textContent = "Downloading and preparing the 3D model...";
      viewer.src = source;
    } catch (error) {
      viewer.removeAttribute("aria-busy");
      button.hidden = false;
      button.disabled = false;
      button.textContent = "Try loading again";
      status.textContent = error.message;
    }
  }

  button.addEventListener("click", loadModel);
  loadModel();
}
