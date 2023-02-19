import os
import re

import requests
from bs4 import BeautifulSoup
from lxml import etree

os.makedirs("assets", exist_ok=True)

resp = requests.get("https://mtg.fandom.com/wiki/Category:Mana_symbols")
soup = BeautifulSoup(resp.content, 'html.parser')
div = soup.find('div', {'id': 'mw-category-media'})


def strip_ns_attributes(tree):
    query = "descendant-or-self::*[namespace-uri()!='']"
    # for each element returned by the above xpath query...
    for element in tree.xpath(query):
        for attr in element.attrib:
            if 'inkscape' in attr or 'sodipodi' in attr:
                element.attrib.pop(attr)
    return tree


def strip_ns_prefix(tree):
    # xpath query for selecting all element nodes in namespace
    query = "descendant-or-self::*[namespace-uri()!='']"
    # for each element returned by the above xpath query...
    for element in tree.xpath(query):
        # replace element name with its local name
        element.tag = etree.QName(element).localname
    return tree


def strip_useless_elems_and_attrs(tree):
    for element in tree.xpath("descendant-or-self::*"):
        if element.tag in ('defs', 'metadata', 'namedview'):
            tree.remove(element)
            continue

        for attr in xml.attrib:
            if attr in ('id', 'version'):
                xml.attrib.pop(attr)

    return tree


for item in div.ul.find_all('li'):
    name = item.div.find('div', {'class': 'gallerytext'}).a.text
    url = item.div.find('div', {'class': 'thumb'}).div.a.get('href')
    svg = requests.get(url).content

    xml = etree.XML(svg)

    xml = strip_ns_attributes(xml)
    xml = strip_ns_prefix(xml)
    etree.cleanup_namespaces(xml)

    xml = strip_useless_elems_and_attrs(xml)
    xml.attrib['viewBox'] = "0 0 600 600"

    xml = etree.tostring(xml).decode()
    xml = re.sub(r"\sxmlns:[^\s]+", "", xml)

    if name == '2B.svg':
        xml = xml.replace('#cccccc', '#cbc2bf')

    filepath = f"assets/{name}"
    with open(filepath, 'w') as svg_file:
        svg_file.write(xml)
