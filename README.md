# Portfolio Website for William Ma

Static HTML, CSS, and JavaScript. No build step or package installation is required.

## Local development

From the project folder, start the local server:

```powershell
python -m http.server 8000
```

Then open http://localhost:8000/html/ in your browser.

All HTML pages live in `html/`, including the homepage at `html/index.html`.
Keep serving the project folder so the shared CSS, JavaScript, and assets remain
accessible. The site root `/` has no index page; a hosting redirect from `/` to
`/html/` is needed if you want visitors to land on the homepage from the root URL.

Use the local server rather than opening HTML files directly: the JavaScript entry
point uses native browser modules.

## Where to make changes

| Change                                                  | File                                                    |
| ------------------------------------------------------- | ------------------------------------------------------- |
| Home page content and project timeline                  | `html/index.html`                                       |
| Engineering project content                             | `html/project-*.html`                                   |
| Artwork, photography, and collection links              | `html/art.html`, `html/photo.html`, `html/gallery.html` |
| Resume page and PDF                                     | `html/resume.html`, `assets/William_Ma_Resume.pdf`      |
| Colors, type, spacing, and global defaults              | `css/base.css`                                          |
| Buttons, form fields, and shared image wrappers         | `css/components.css`                                    |
| Site header, navigation, and page wrapper               | `css/layout.css`                                        |
| Home page layout                                        | `css/home.css`                                          |
| Shared project layouts and image galleries              | `css/projects.css`                                      |
| Swerve layout and diagrams                              | `css/swerve.css`                                        |
| Resume and image preview dialog styles                  | `css/resume.css`, `css/lightbox.css`                    |
| Clock, form feedback, scroll reveal, and image previews | Corresponding files in `js/`                            |
| Swerve viewer setup and loading                         | `js/swerve-viewer-config.js`, `js/swerve-model.js`      |

`styles.css` imports the stylesheets in cascade order and loads the font once.
Responsive rules live with their component or page styles. Keep new styles in the
appropriate file and use named classes instead of inline styles.

`script.js` initializes shared behaviors. Each initializer returns immediately on
pages without that feature. The Swerve page loads its viewer scripts separately;
the configuration script must run before the external model-viewer module.

To add a project, copy the closest `html/project-*.html` layout into `html/`, update
its content and image descriptions, and add a link in the home page timeline.
Links between pages use filenames such as `project-swerve.html`; shared resources
use paths such as `../styles.css`, `../script.js`, and `../assets/Engineering/...`.
Pages keep their
navigation in HTML; update each relevant header when adding a navigation item.

The contact form currently provides demo feedback only; it does not send or queue
messages. Connect a delivery service in `js/contact-form.js` to enable real submissions.

## Formatting and checks

`.editorconfig` sets UTF-8, LF line endings, and indentation. `.prettierrc.json`
defines formatting for Prettier-compatible editors; `.prettierignore` excludes
assets and the third-party decoder. Use your editor's Format Document command.

Run the dependency-free structural and local-reference check:

```powershell
python scripts/check_site.py
```

This checks HTML tag nesting, duplicate IDs, local files and anchors, CSS imports,
and JavaScript imports. It also checks filename case for deployment to
case-sensitive hosts. It does not fetch external services or render the pages.
After changing interactions, check image previews with the mouse and keyboard,
the contact form feedback, and the Swerve load/retry controls in a browser. After
changing layout, check both desktop and mobile widths.

## Swerve 3D preview

The page loads `assets/Swerve_Assembly.web.glb` only after the visitor clicks
**Load interactive model**. Keep `Swerve_Assembly.gltf` as the original CAD export;
the `.gltf.gz` file is not used by the viewer.

The viewer applies `orientation="0deg 90deg 0deg"` to align the CAD export's
negative Z up direction with the viewer's positive Y up direction. Keep this
rotation on the viewer so dragging orbits around the robot's upright axis.

Regenerate the web asset with [gltfpack 1.3](https://meshoptimizer.org/gltf/):

```powershell
gltfpack -i assets/Swerve_Assembly.gltf -o assets/Swerve_Assembly.web.glb -si 0.15 -se 0.001 -sp -mm -cc
```

This merges static geometry by material, simplifies it toward 15% of the original
triangle count with a 0.1% relative simplification error limit, quantizes vertex
data, removes CAD metadata, and applies `EXT_meshopt_compression`. The result is
a display model, so use the original export for precise engineering inspection.
After regenerating, visually check curved surfaces and small parts in the viewer.

| Metric                                       | Original export | Web preview |
| -------------------------------------------- | --------------: | ----------: |
| File size (decimal MB)                       |          142.42 |        5.41 |
| Estimated draw calls                         |          84,927 |          61 |
| Rendered triangles, including repeated parts |       5,851,437 |     912,825 |

Draw calls and triangle counts come from gltfpack's scene report; they are not
browser frame-rate measurements. The viewer uses a low-power GPU preference,
disables automatic camera prompts and tap-to-recenter raycasting, and allows
adaptive resolution down to 25% while moving. It renders on demand and skips
offscreen models through model-viewer's built-in behavior.

`assets/vendor/meshoptimizer/meshopt_decoder.js` is the classic browser decoder
from meshoptimizer v0.22, which supports the `EXT_meshopt_compression` format
emitted by `-cc`. It is served locally with its MIT license. Keep this decoder
configured before model-viewer initializes; it is required to load the GLB.
