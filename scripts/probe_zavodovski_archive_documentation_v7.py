"""Inspect public RAMADDA entry HTML for documentation URLs, never polygon bytes.

A missing CSV link is an ACCESS HOLD, not proof of absence.
"""
import argparse
import html.parser
import json
import re
import urllib.parse
import urllib.request

ROOT = "https://ramadda.data.bas.ac.uk"
ENTRY = ROOT + "/repository/entry/show?entryid=7220dc6b-2f52-4160-a6c0-e57c50963308"

class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        a = dict(attrs)
        if a.get("href"):
            self.links.append((a.get("href"), a.get("title", "")))

def documentation_links(page, base=ENTRY):
    parser = Links()
    parser.feed(page)
    found = []
    for href, title in parser.links:
        full = urllib.parse.urljoin(base, href)
        host = urllib.parse.urlparse(full).hostname
        if host != "ramadda.data.bas.ac.uk":
            continue
        if re.search(r"layer[_\\-]?descriptions(?:\\.csv)?", urllib.parse.unquote(full+" "+title), re.I):
            found.append(full)
    return sorted(set(found))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    a = p.parse_args()
    result = {"entry": ENTRY, "status": "HOLD", "csv_links": [],
              "original_polygon_rows_read": 0, "csv_contents_read": False}
    try:
        request = urllib.request.Request(ENTRY, headers={"User-Agent": "mina-source-metadata-audit/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            final = response.geturl()
            if urllib.parse.urlparse(final).hostname != "ramadda.data.bas.ac.uk":
                raise ValueError("Unexpected host redirect")
            content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("Page too large")
        result["http_html_bytes"] = len(content)
        result["csv_links"] = documentation_links(content.decode("utf-8", errors="replace"), final)
        result["status"] = "CSV_LINK_FOUND_NOT_DOWNLOADED" if result["csv_links"] else "HOLD_CSV_LINK_NOT_IN_HTML"
    except Exception as exc:
        result["status"] = "HOLD_SOURCE_ACCESS_ERROR"
        result["error_type"] = type(exc).__name__
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))
if __name__ == "__main__":
    main()
