import json
import os, sys

from fetch_deck_history import OUTPUT_DIRNAME, run as fetch_deck_history
from time_in_deck import run as time_in_deck


def run(deck_id):
    filename = fetch_deck_history(deck_id)
    with open(filename, "r") as f:
        deck_history = json.load(f)
    time_in_deck(deck_history, filename)


if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIRNAME):
        os.mkdir(OUTPUT_DIRNAME)
    deck_id = sys.argv[1]
    run(deck_id)
