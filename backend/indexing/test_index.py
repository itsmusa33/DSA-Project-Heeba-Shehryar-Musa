#This file tests the tokenizer, lexicon, forward index and inverted index
#It uses a tiny hand made table of games, 
#so every expected answer was worked out by hand and not copied from the code's own output

import os
import sys
import tempfile
from itertools import chain

import pandas as pd

#Making sure the imports work even if the tests are started from another folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tokenizer import tokenize
from lexicon import build_lexicon, save_lexicon, load_lexicon
from forward_index import build_forward_index
from inverted_index import build_inverted_index


#Four small games with known text
#Game 1 has html and a url, game 2 has an accent and a missing short description,
# game 4 has an apostrophe
def make_games():
    return pd.DataFrame({
        "app_id": [1, 2, 3, 4],
        "name": ["Space Game", "Pokémon Quest", "Quest Game Quest", "Café 2048"],
        "short_description": ["A fun game", None, "Space fun", "Dont stop"],
        "description": [
            "Fly in space. <b>Space</b> battles at https://example.com now",
            "Sofya's game of the day",
            "A fun quest",
            "<p>Don't stop playing</p> the game",
        ],
    })


#Builds all three indexes the same way build_index.py does
def make_indexes(df):
    texts = chain(df["name"].fillna(""), df["short_description"].fillna(""), df["description"].fillna(""))
    lexicon = build_lexicon(texts)
    forward_index = build_forward_index(df, lexicon)
    inverted_index = build_inverted_index(forward_index)
    return lexicon, forward_index, inverted_index


#tokenizer 

def test_tokenizer_strips_html_and_urls():
    assert tokenize("<b>Hello</b> world") == ["hello", "world"]
    assert tokenize("see https://example.com/x now") == ["see", "now"]
    assert tokenize("rock &amp; roll") == ["rock", "roll"]


def test_tokenizer_accents_and_apostrophes():
    assert tokenize("Pokémon") == ["pokemon"]
    assert tokenize("Sofya's game") == ["sofya", "game"]
    #curly apostrophe should turn into a normal one
    assert tokenize("Don\u2019t") == ["don't"]


def test_tokenizer_keeps_stopwords():
    #"and" must stay searchable, the project spec says not to remove stopwords
    assert tokenize("Data and Algorithms") == ["data", "and", "algorithms"]


def test_tokenizer_single_letters_and_junk():
    #single letters dropped, single digits kept
    assert tokenize("a I 7") == ["7"]
    #a 30 character word is junk and gets dropped
    assert tokenize("a" * 30) == []


def test_tokenizer_bad_input():
    assert tokenize(None) == []
    assert tokenize(float("nan")) == []
    assert tokenize("") == []


#lexicon

def test_lexicon_ids_have_no_gaps():
    lexicon, _, _ = make_indexes(make_games())
    #ids must be exactly 0 to N-1, each used once
    assert sorted(lexicon.values()) == list(range(len(lexicon)))


def test_lexicon_contents():
    lexicon, _, _ = make_indexes(make_games())
    assert "the" in lexicon    #stopwords are kept
    assert "pokemon" in lexicon    #accent removed
    assert "a" not in lexicon #single letters dropped


def test_lexicon_round_trip():
    lexicon, _, _ = make_indexes(make_games())
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "sub", "lexicon.json") #sub folder checks that save makes the folder
        save_lexicon(lexicon, path)
        assert load_lexicon(path) == lexicon

#Simple runner so the file also works without pytest
if __name__ == "__main__":
    failed = 0
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            try:
                func()
                print("PASS", name)
            except Exception as error:
                failed += 1
                print("FAIL", name, "->", repr(error))
    print("\n%d test(s) failed" % failed if failed else "\nAll tests passed")