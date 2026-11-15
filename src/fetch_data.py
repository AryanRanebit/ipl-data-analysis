"""Download the raw IPL dataset from Cricsheet.

Source: https://cricsheet.org/downloads/ipl_json.zip (ODC-By licensed)
        https://cricsheet.org/register/people.csv

Re-running this script refreshes the raw data to the latest Cricsheet release.
The processed CSVs committed under data/processed/ are the frozen snapshot
that the analysis and tests run against; re-run build_dataset.py after
fetching to update them.
"""

import urllib.request
import zipfile
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
IPL_ZIP_URL = "https://cricsheet.org/downloads/ipl_json.zip"
PEOPLE_URL = "https://cricsheet.org/register/people.csv"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "ipl_json.zip"

    print(f"Downloading {IPL_ZIP_URL} ...")
    urllib.request.urlretrieve(IPL_ZIP_URL, zip_path)

    print(f"Downloading {PEOPLE_URL} ...")
    urllib.request.urlretrieve(PEOPLE_URL, RAW_DIR / "people.csv")

    out_dir = RAW_DIR / "ipl_json"
    out_dir.mkdir(exist_ok=True)
    print(f"Extracting to {out_dir} ...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)

    n_matches = len(list(out_dir.glob("*.json")))
    print(f"Done. {n_matches} match JSON files in {out_dir}")


if __name__ == "__main__":
    main()
