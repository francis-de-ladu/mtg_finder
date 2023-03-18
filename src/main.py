import asyncio
from concurrent.futures import process
import re
import time
from typing import Optional

import pandas as pd
import scrython as scry
import streamlit as st
from stqdm import stqdm

from utils import Database
from pathlib import Path

from collections import defaultdict


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
    print(card.set_code())
    print(card.set_name())
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


def load_svg(name: str, size: int = 14, kind="symbology") -> str:
    with open(f"assets/{kind}/{name}.svg", 'r') as svg_file:
        svg = svg_file.read()

    return svg.replace("<svg ", f"<svg width='{size}',  height='{size}'", 1)


def replace_symbols(text, svg_size=14):
    for match in re.findall(r"\{(\w+)\}", text):
        try:
            text = text.replace(f"{{{match}}}", load_svg(match, svg_size))
        except FileNotFoundError:
            print(f"FileNotFoundError Exception --> {match}.svg")
            continue

    return text


def get_cards_from_names(card_names: list[str], top_n: Optional[int] = None):
    if top_n is not None:
        card_names = card_names[:top_n]

    cards = []
    missing = []
    for name in card_names:
        card = Database.retrieve(name)
        if card is not None:
            cards.append(card)
        else:
            missing.append(name)

    if missing:
        for name in stqdm(missing):
            card = Database.retrieve(name)
            if card is None:
                card = to_card_properties(scry.cards.Named(exact=name))
                Database.insert(card)
                time.sleep(0.05)
            cards.append(card)

    return cards


def process_cards(cards: list) -> pd.DataFrame:
    processed = pd.DataFrame.from_dict(cards)

    processed['mana_cost'] = processed['mana_cost'].apply(
        replace_symbols, svg_size=16)
    processed['text'] = processed['text'].apply(replace_symbols, svg_size=14)
    processed['text'] = processed['text'].apply(
        lambda x: f'<span style="white-space: pre-line">{x}</span>')

    processed['cmc'] = processed['cmc'].apply(
        lambda x: int(x) or '').apply(str)
    processed['power'] = processed['power'].apply(lambda x: x or '')
    processed['toughness'] = processed['toughness'].apply(lambda x: x or '')

    processed['strength'] = processed[['power', 'toughness']].apply(
        lambda entry: entry['power'] + '/' + entry['toughness'] if entry['power'] else '',
        axis=1,
    )

    processed['url'] = processed['url'].apply(
        lambda x: f'<a href="{x}">Gatherer</a>')

    return processed


def get_decks():
    try:
        decks = st.session_state["decks"]
    except KeyError:
        decks = defaultdict(list)
        for file in Path("data").rglob("*.csv"):
            deck = file.parts[-2]
            decks[deck].append(file.stem)
        st.session_state["decks"] = decks
    finally:
        return decks


def refresh_card_list(top_n=None):
    time.sleep(.25)
    curr_deck, curr_list = st.session_state["curr_deck"], st.session_state["curr_list"]
    list_path = Path("data") / curr_deck / f"{curr_list}.csv"
    print(list_path)
    candidates = pd.read_csv(list_path)
    try:
        card_names = candidates.card_name.tolist()
    except AttributeError:
        card_names = candidates.name.tolist()

    cards = get_cards_from_names(card_names, top_n=top_n)
    return process_cards(cards)


def main(top_n=None):
    st.set_page_config(layout="wide")

    decks = get_decks()
    curr_deck = next(iter(decks))
    st.session_state["curr_deck"] = curr_deck
    st.session_state["curr_list"] = decks[curr_deck][0]

    processed = refresh_card_list()

    COLUMNS = ['name', 'type_line', 'mana_cost', 'strength', 'text', 'rarity', 'url']
    styled = processed[COLUMNS].style.format(
        # formatter={'cmc': "{:.0f}"}
    )

    deck_dd, list_dd = st.columns(2)
    with deck_dd:
        decks = defaultdict(list)
        for file in Path("data").rglob("*.csv"):
            deck = file.parts[-2]
            decks[deck].append(file.stem)

        st.session_state["curr_deck"] = st.selectbox(
            "Current deck", decks.keys(),
            on_change=refresh_card_list)

    with list_dd:
        st.session_state["curr_list"] = st.selectbox(
            "Card list", decks[curr_deck],
            on_change=refresh_card_list)

    st.text(f"This list contains {len(processed)} cards.")

    st.markdown(
        styled.to_html(),
        unsafe_allow_html=True
    )

    st.title("supsupsup")
    html = f"<p>supsup <span>{load_svg('T')}</span> supsup</p>"
    st.write(html, unsafe_allow_html=True)

    st.title("supsupsupsup")


if __name__ == "__main__":
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    main()
