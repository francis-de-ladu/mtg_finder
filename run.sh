#!/bin/bash

headless="${1:-true}"

# streamlit run src/main.py --server.runOnSave true --server.headless $headless
python -m streamlit run src/main.py --server.runOnSave true --server.headless $headless
