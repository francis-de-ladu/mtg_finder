import asyncio
import time

import pandas as pd
import scrython as scry
import streamlit as st
from tqdm import tqdm
import re


def is_public_prop(prop):
    return not prop.startswith('_')


def get_property(card, prop, key=None):
    try:
        get_prop_value = getattr(card, prop)
        value = get_prop_value()
        if key is not None:
            value = value.get(key, '')
        return value
    except KeyError:
        return None


def to_card_properties(card):
    return dict(
        id=get_property(card, 'id'),
        name=get_property(card, 'name'),
        type_line=get_property(card, 'type_line'),
        mana_cost=get_property(card, 'mana_cost'),
        cmc=get_property(card, 'cmc'),
        power=get_property(card, 'power'),
        toughness=get_property(card, 'toughness'),
        text=get_property(card, 'oracle_text'),
        rarity=get_property(card, 'rarity'),
        legal=get_property(card, 'legalities', key='commander') == 'legal',
        lang=get_property(card, 'lang'),
        url=get_property(card, 'related_uris', key='gatherer'),
    )


def to_html(cards):
    print(cards)


def replace_symbols(text, svg_size=14):
    for match in re.findall(r"\{(\w+)\}", text):
        try:
            with open(f"assets/{match}.svg", 'r') as svg_file:
                svg = svg_file.read()

            svg = re.sub(r'(width|height)="\d+"',
                         f"\\1={svg_size}", svg, count=2)
            text = text.replace(f"{{{match}}}", svg)
        except FileNotFoundError:
            continue

    return text


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    st.set_page_config(layout="wide")

    candidates = pd.read_csv("data/perrie/cards.csv")

    cards = []
    for name in tqdm(candidates.card_name.tolist()[:10]):
        card = to_card_properties(scry.cards.Named(exact=name))
        cards.append(card)
        time.sleep(0.1)

    processed = pd.DataFrame.from_dict(cards)

    processed.to_csv("data/perrie/processed.csv")

    processed['mana_cost'] = processed['mana_cost'].apply(
        replace_symbols, svg_size=18)
    processed['text'] = processed['text'].apply(replace_symbols, svg_size=14)

    processed['power'] = processed['power'].apply(lambda x: x or '')
    processed['toughness'] = processed['toughness'].apply(lambda x: x or '')

    styled = processed.drop(['id', 'lang'], axis=1).style.format(
        formatter={'cmc': "{:.0f}"}
    )

    st.markdown(
        styled.to_html(),
        unsafe_allow_html=True
    )
    markdown = to_html(processed)

    with open("assets/2G.svg", 'r') as svg_file:
        svg = svg_file.read()

    st.title("supsupsup")
    html = f"""<div style="height:20px"><p>supsup <span>{svg}</span> supsup</p></div>"""
    st.write(html, unsafe_allow_html=True)

    st.title("supsupsupsup")


if __name__ == "__main__":
    main()
