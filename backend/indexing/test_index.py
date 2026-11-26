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
from forward_index import build_forward_index, save_forward_index, load_forward_index
from inverted_index import build_inverted_index, save_inverted_index, load_inverted_index
from build_index import load_games


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

#------------------ forward index ------------------

def test_forward_index_counts():
    lexicon, forward_index, _ = make_indexes(make_games())
    #game 1: "space" is once in the title and twice in the body
    assert forward_index[1][lexicon["space"]] == [1, 2]
    #game 2: "pokemon" is only in the title, "sofya" only in the body
    assert forward_index[2][lexicon["pokemon"]] == [1, 0]
    assert forward_index[2][lexicon["sofya"]] == [0, 1]
    #game 3: "quest" is twice in the title and once in the body
    assert forward_index[3][lexicon["quest"]] == [2, 1]


def test_forward_index_ids_exist_in_lexicon():
    lexicon, forward_index, _ = make_indexes(make_games())
    valid_ids = set(lexicon.values())
    for app_id, words in forward_index.items():
        for word_id in words:
            assert word_id in valid_ids


def test_forward_index_round_trip():
    lexicon, forward_index, _ = make_indexes(make_games())
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "forward_index.json")
        save_forward_index(forward_index, path)
        loaded = load_forward_index(path)
        assert loaded == forward_index
        #keys must be ints again after loading, json turns them into strings
        assert all(isinstance(k, int) for k in loaded)


def test_forward_index_missing_description():
    #a game with no description at all should not crash the build
    df = pd.DataFrame({"app_id": [10], "name": ["Lonely Game"], "short_description": ["Just short"], "description": [None]})
    lexicon, forward_index, _ = make_indexes(df)
    assert lexicon["lonely"] in forward_index[10]


#------------------ inverted index ------------------

def test_inverted_index_known_word():
    lexicon, _, inverted_index = make_indexes(make_games())
    #"game" by hand: game 1 title 1 body 1, game 2 body 1, game 3 title 1, game 4 body 1
    assert inverted_index[lexicon["game"]] == [[1, 1, 1], [2, 0, 1], [3, 1, 0], [4, 0, 1]]


def test_inverted_lists_sorted_and_unique():
    _, _, inverted_index = make_indexes(make_games())
    for word_id, postings in inverted_index.items():
        app_ids = [p[0] for p in postings]
        assert app_ids == sorted(app_ids)
        assert len(app_ids) == len(set(app_ids))


def test_inverted_matches_forward():
    _, forward_index, inverted_index = make_indexes(make_games())
    #every pair in the inverted index must have the same counts as the forward index
    for word_id, postings in inverted_index.items():
        for app_id, title_count, body_count in postings:
            assert forward_index[app_id][word_id] == [title_count, body_count]
    #and the total number of pairs must be the same in both
    forward_total = sum(len(words) for words in forward_index.values())
    inverted_total = sum(len(postings) for postings in inverted_index.values())
    assert forward_total == inverted_total


def test_inverted_index_round_trip():
    _, _, inverted_index = make_indexes(make_games())
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "inverted_index.json")
        save_inverted_index(inverted_index, path)
        loaded = load_inverted_index(path)
        assert loaded == inverted_index
        assert all(isinstance(k, int) for k in loaded)


#------------------ loading the games file ------------------

def test_load_games_cleans_ids():
    df = pd.DataFrame({
        "app_id": [1, 1, None, 3],
        "name": ["a", "b", "c", "d"],
        "short_description": ["x", "x", "x", "x"],
        "description": ["y", "y", "y", "y"],
    })
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "games.csv")
        df.to_csv(path, index=False)
        cleaned = load_games(path)
        #the duplicate id 1 and the missing id are gone
        assert list(cleaned["app_id"]) == [1, 3]


def test_load_games_missing_column():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "games.csv")
        pd.DataFrame({"app_id": [1]}).to_csv(path, index=False)
        try:
            load_games(path)
        except ValueError:
            return
        assert False, "expected a ValueError for missing columns"
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