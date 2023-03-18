import json
from typing import Optional, Self

import streamlit as st


class MetaDatabase(type):
    @property
    def database(cls):
        return cls.instance()._database


class Database(object, metaclass=MetaDatabase):
    _instance = None
    _database = {}
    _DB_KEY = 'DB'

    def __init__(self) -> None:
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls: Self, filename: Optional[str] = "mtg.db") -> Self:
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

        if cls._DB_KEY in st.session_state:
            cls._database = st.session_state[cls._DB_KEY]
        else:
            try:
                with open(filename, 'r') as file:
                    cls._database = json.load(file)
            except (FileNotFoundError, json.decoder.JSONDecodeError):
                pass

        return cls._instance

    @classmethod
    def exists(cls: Self, name: str, set_: Optional[str] = None) -> bool:
        return name in cls.database

    @classmethod
    def retrieve(cls: Self, name: str, set_: Optional[str] = None):
        return cls.database.get(name)

    @classmethod
    def insert(cls: Self, card) -> None:
        cls.database[card['name']] = card
        with open('mtg.db', 'w') as file:
            json.dump(cls.database, file)
