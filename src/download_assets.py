import json
import time
from pathlib import Path

import requests
from tqdm import tqdm


def get_svg_uri(data: dict[str, str]) -> str:
    for key, value in data.items():
        if key.endswith("svg_uri"):
            return value.split('?')[0]


def fetch_assets(kind: str, base_url: str = "https://api.scryfall.com/") -> None:
    out_dir = Path("assets") / kind
    out_dir.mkdir(parents=True, exist_ok=True)

    resp = requests.get(base_url + kind)
    data = json.loads(resp.content.decode())['data']

    for item in tqdm(data, desc=f"Fetching {kind} symbols"):
        uri = get_svg_uri(item)
        resp = requests.get(uri)
        svg = resp.content.decode()

        filename = uri.split('/')[-1]
        with open(out_dir / filename, 'w') as file:
            file.write(svg)

        time.sleep(0.05)


if __name__ == '__main__':
    fetch_assets("symbology")
    fetch_assets("sets")
