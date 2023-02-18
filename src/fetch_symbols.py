from bs4 import BeautifulSoup
import requests
import os
import pandas as pd
from cairosvg import svg2png

os.makedirs("assets", exist_ok=True)

resp = requests.get("https://mtg.fandom.com/wiki/Category:Mana_symbols")
soup = BeautifulSoup(resp.content, 'html.parser')
div = soup.find('div', {'id': 'mw-category-media'})

for item in div.ul.find_all('li'):
    name = item.div.find('div', {'class': 'gallerytext'}).a.text
    url = item.div.find('div', {'class': 'thumb'}).div.a.get('href')
    svg = requests.get(url).content
    # filename = name.replace('.svg', '.png')
    # svg2png(bytestring=svg, write_to=f"assets/{filename}")

    with open(f"assets/{name}", 'wb') as asset:
        asset.write(svg)


# resp = requests.get("https://scryfall.com/docs/api/colors")
# tables = pd.read_html(resp.content)

# for tab in tables:
# print(tab)
