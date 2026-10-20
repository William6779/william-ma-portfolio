"""Check local page links, assets, CSS imports, and JavaScript imports.

Run from any directory: python scripts/check_site.py
Uses only the Python standard library; remote URLs are not fetched.
"""

from html.parser import HTMLParser
from os.path import abspath
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
HTML_ROOT = ROOT / "html"
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.references = []
        self.errors = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id")
        if element_id:
            if element_id in self.ids:
                self.errors.append(f"duplicate id: {element_id}")
            self.ids.add(element_id)
        for attribute in ("href", "src", "poster", "data-src"):
            if attrs.get(attribute):
                self.references.append(attrs[attribute])
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected closing tag: {tag}")
        else:
            self.stack.pop()


def check_reference(source, reference, pages):
    url = urlsplit(reference)
    if url.scheme or url.netloc:
        return None

    if url.path.startswith("/"):
        target = ROOT / unquote(url.path.lstrip("/"))
    elif url.path:
        target = source.parent / unquote(url.path)
    else:
        target = source
    # Keep the reference's spelling: resolve() may correct case on Windows.
    target = Path(abspath(target))
    if not target.resolve().is_relative_to(ROOT):
        return f"reference leaves the site directory: {reference}"
    if not target.is_file():
        return f"missing file: {reference}"

    # Verify spelling and case even on Windows, for case-sensitive hosting.
    relative = target.relative_to(ROOT)
    current = ROOT
    for part in relative.parts:
        if part not in {entry.name for entry in current.iterdir()}:
            return f"filename case mismatch: {reference}"
        current /= part

    fragment = unquote(url.fragment)
    if fragment and target in pages and fragment not in pages[target].ids:
        return f"missing anchor: {reference}"
    return None


def main():
    pages = {}
    references = {}
    errors = []
    sources = sorted(HTML_ROOT.rglob("*.html"))
    if not sources or not (HTML_ROOT / "index.html").is_file():
        errors.append("html/index.html: homepage is missing")
    for source in sources:
        parser = PageParser()
        parser.feed(source.read_text(encoding="utf-8"))
        parser.close()
        pages[source] = parser
        references[source] = parser.references
        errors.extend(f"{source.name}: {error}" for error in parser.errors)
        if parser.stack:
            errors.append(f"{source.name}: unclosed tags: {', '.join(parser.stack)}")

    for source in [ROOT / "styles.css", *sorted((ROOT / "css").glob("*.css"))]:
        references[source] = re.findall(
            r"url\(\s*['\"]?([^'\")]+)", source.read_text(encoding="utf-8")
        )
    for source in [ROOT / "script.js", *sorted((ROOT / "js").glob("*.js"))]:
        references[source] = re.findall(
            r"\bimport\s+(?:[^;]*?\s+from\s+)?['\"]([^'\"]+)",
            source.read_text(encoding="utf-8"),
        )

    for source, urls in references.items():
        for reference in urls:
            error = check_reference(source, reference, pages)
            if error:
                errors.append(f"{source.relative_to(ROOT)}: {error}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    count = sum(len(urls) for urls in references.values())
    print(f"Checked {len(pages)} pages and {count} references: no errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
