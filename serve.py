#!/usr/bin/env python3
"""
Build Cannapedia and serve it locally for preview.

Usage:
    python3 serve.py            # build + serve on http://localhost:8000
    python3 serve.py --port 9000

This uses only Python's standard library (http.server), so there is
nothing to install to try the site out. Re-run this script (or
`python3 build.py` followed by a server restart) any time you edit
content in content/articles/ -- the generator is fast since the site
is small.
"""
import argparse
import functools
import http.server
import webbrowser
from pathlib import Path

import build as sitebuild

ROOT = Path(__file__).parent.resolve()
DIST_DIR = ROOT / "dist"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true",
                         help="Don't try to auto-open a browser tab.")
    args = parser.parse_args()

    sitebuild.build()

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(DIST_DIR)
    )
    url = f"http://localhost:{args.port}/"
    print(f"\nCannapedia is running at {url}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    with http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")


if __name__ == "__main__":
    main()
