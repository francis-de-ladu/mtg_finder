import asyncio
import time

import pandas as pd
import scrython as scry
import streamlit as st
from tqdm import tqdm


def is_public_prop(prop):
    return not prop.startswith('_')


def get_property(card, prop, key=None):
    try:
        value = getattr(card, prop)()
        if key is not None:
            value = value.get(key, None)

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
        commander=get_property(card, 'legalities', key='commander') == 'legal',
        lang=get_property(card, 'lang'),
        url=get_property(card, 'related_uris', key='gatherer'),
    )


def to_html(cards):
    print(cards)


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    candidates = pd.read_csv("data/perrie/cards.csv")

    cards = []
    for name in tqdm(candidates.card_name.tolist()[:5]):
        # print(f"\n{name}:\n")
        card = to_card_properties(scry.cards.Named(exact=name))
        # for prop in filter(is_public_prop, dir(card)):
        #     try:
        #         print(f"{prop}: {getattr(card, prop)()}")
        #     except:
        #         continue
        # print(card)
        cards.append(card)
        time.sleep(0.1)

    processed = pd.DataFrame.from_dict(cards)

    processed.to_csv("data/perrie/processed.csv")

    st.dataframe(processed)
    markdown = to_html(processed)

    with open("assets/2G.svg", 'r') as svg_file:
        svg = svg_file.read()

    svg = svg.replace('<svg', '<svg style="height:18; width:18;"')

    st.title("supsupsup")
    html = f"""<div style="height:20px"><p>supsup <span>{svg}</span> supsup</p></div>"""
    st.write(html, unsafe_allow_html=True)

    st.title("supsupsupsup")


if __name__ == "__main__":
    main()
