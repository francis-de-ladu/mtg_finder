import re

import streamlit as st

SYMBOLOGY = 'symbology'
SETS = 'sets'


def display(df):
    df['mana_cost'] = df['mana_cost'].apply(replace_symbology, svg_size=18)
    df['text'] = df['text'].apply(replace_symbology, svg_size=14)

    df['cmc'] = df['cmc'].apply(
        lambda x: int(x) or '').apply(str)
    df['power'] = df['power'].apply(lambda x: x or '')
    df['toughness'] = df['toughness'].apply(lambda x: x or '')

    df['url'] = df['url'].apply(
        lambda x: f'<a href="{x}">Gatherer</a>')

    if 'set' in df.columns:
        df['set'] = df['set'].apply(replace_sets, svg_size=24)

    styled = df.drop(['id', 'lang'], axis=1).style.format(
        # formatter={'cmc': "{:.0f}"}
    )

    st.markdown(
        styled.to_html(),
        unsafe_allow_html=True
    )


def load_svg(kind: str, name: str, size: int = 14) -> str:
    with open(f"assets/{kind}/{name}.svg", 'r') as svg_file:
        svg = svg_file.read()

    return svg.replace("<svg ", f"<svg width='{size}',  height='{size}'", 1)


def replace_symbology(text: str, svg_size: int = 14):
    for match in re.findall(r"\{(\w+)\}", text):
        try:
            text = text.replace(f"{{{match}}}", load_svg(SYMBOLOGY, match, svg_size))
        except FileNotFoundError:
            print(f"FileNotFoundError Exception --> {match}.svg")
            continue


def replace_sets(text: str, svg_size: int):
    try:
        text = text.replace(f"{text}", load_svg(SETS, text, svg_size))
    except FileNotFoundError:
        print(f"FileNotFoundError Exception --> {text}.svg")

    return text
