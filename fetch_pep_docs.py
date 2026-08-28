"""
Fetches the real PEP 8 and PEP 257 text and saves them locally,
so GPP can ground its explanations in the actual style guide
instead of the model's memory of it.

Tries a few known URL patterns for each doc, since PEP hosting
formats have changed over time (.txt vs .rst, different repo paths).
"""

import requests
from pathlib import Path

DOCS_FOLDER = Path("pep_docs")
DOCS_FOLDER.mkdir(exist_ok=True)

# Each doc has a few candidate URLs to try, in order.
SOURCES = {
    "pep8.txt": [
        "https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst",
        "https://raw.githubusercontent.com/python/peps/master/pep-0008.txt",
    ],
    "pep257.txt": [
        "https://raw.githubusercontent.com/python/peps/main/peps/pep-0257.rst",
        "https://raw.githubusercontent.com/python/peps/master/pep-0257.txt",
    ],
}


def fetch_docs():
    for filename, urls in SOURCES.items():
        saved = False
        for url in urls:
            print(f"Trying {url} ...")
            response = requests.get(url)
            if response.status_code == 200:
                (DOCS_FOLDER / filename).write_text(
                    response.text, encoding="utf-8"
                )
                print(f"Saved to {DOCS_FOLDER / filename}")
                saved = True
                break
            else:
                print(f"  -> failed ({response.status_code}), trying next...")
        if not saved:
            print(f"WARNING: could not fetch {filename} from any source.")


if __name__ == "__main__":
    fetch_docs()