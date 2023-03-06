import asyncio
import time

import pandas as pd
import scrython as scry
import streamlit as st
from streamlit_searchbox import st_searchbox

from utils import display

results = None
text_input = None


st.set_page_config(layout="wide")


def get_autocomplete(text: str):
    candidates = scry.cards.Autocomplete(q=text).data()
    print(f"{candidates=}")
    return candidates


def get_search_results():
    cards = scry.cards.Search(q=text_input, unique='prints').data()

    sets = set()
    uniques = []
    for card in cards:
        if card['set'] not in sets:
            pass
        # print(c['set'])
    return pd.DataFrame.from_dict(map(to_card_properties, uniques))


def get_property(card, prop, key=None):
    try:
        # get_prop_value = getattr(card, prop)
        # value = get_prop_value()
        value = card.get(prop)
        if key is not None:
            value = value.get(key, '')
        return value
    except KeyError:
        return None


def to_card_properties(card):
    return dict(
        id=get_property(card, 'id'),
        name=get_property(card, 'name'),
        set=get_property(card, 'set'),
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


st.subheader("Card Search")
text_input = st_searchbox(get_autocomplete, key="card_search")

if text_input:
    print(text_input)
    results = get_search_results()

st.subheader("Results")
if results is not None and not results.empty:
    display(results)
