#this is the main file 
#It reads the games file, then builds and saves the lexicon, forward index and inverted index.
#to run it type python build_index.py --input sample_games.csv --out data 
#in the terminal

import argparse
import os
import time

import pandas as pd

from tokenizer import tokenize
from lexicon import build_lexicon_from_tokens, save_lexicon
from forward_index import build_forward_index_from_tokens, save_forward_index
from inverted_index import build_inverted_index, save_inverted_index

REQUIRED_COLUMNS = ["app_id", "name", "short_description", "description"]


#Reading a csv, parquet or json file into a dataframe, chosen by the file extension
def read_table(path):
    ext = path.lower().rsplit(".", 1)[-1]
    if ext == "csv":
        return pd.read_csv(path)
    if ext == "parquet":
        return pd.read_parquet(path)
    if ext == "json":
        return pd.read_json(path)
    raise ValueError("Unsupported file type: " + ext)


def load_games(path):
    df = read_table(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    #A game without an app_id cannot be indexed, duplicate ids would silently overwrite each other
    df = df.dropna(subset=["app_id"]).drop_duplicates(subset="app_id")
    #After dropna a column can turn into floats (10.0), so ids are forced back to whole numbers
    df["app_id"] = df["app_id"].astype("int64")
    return df.reset_index(drop=True)

#Tokenizing every game once. Returns a dictionary of app_id -> (title_tokens, body_tokens).
#The body is the short description and the description joined with a space.
def tokenize_games(df):
    short_descriptions = df["short_description"].fillna("")
    game_tokens = {}
    for app_id, name, short, desc in zip(df["app_id"], df["name"].fillna(""), short_descriptions, df["description"].fillna("")):
        game_tokens[int(app_id)] = (tokenize(name), tokenize(short + " " + desc))
    return game_tokens

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="sample_games.csv")
    parser.add_argument("--out", default="data")
    args = parser.parse_args()

    df = load_games(args.input)
    print("Games loaded:", len(df))

    #Tokenizing every game once; the lexicon and the forward index both use these token lists.
    start = time.time()
    game_tokens = tokenize_games(df)
    print("Tokenized: %d games (%.2fs)" % (len(game_tokens), time.time() - start))

    #Feeding title and body token lists of every game to the lexicon.
    start = time.time()
    token_lists = [tokens for pair in game_tokens.values() for tokens in pair]
    lexicon = build_lexicon_from_tokens(token_lists)
    print("Lexicon: %d words (%.2fs)" % (len(lexicon), time.time() - start))

    start = time.time()
    forward_index = build_forward_index_from_tokens(game_tokens, lexicon)
    print("Forward index: %d documents (%.2fs)" % (len(forward_index), time.time() - start))

    start = time.time()
    inverted_index = build_inverted_index(forward_index)
    print("Inverted index: %d words (%.2fs)" % (len(inverted_index), time.time() - start))

    save_lexicon(lexicon, os.path.join(args.out, "lexicon.json"))
    save_forward_index(forward_index, os.path.join(args.out, "forward_index.json"))
    save_inverted_index(inverted_index, os.path.join(args.out, "inverted_index.json"))
    print("Saved to", args.out + "/")


if __name__ == "__main__":
    main()
