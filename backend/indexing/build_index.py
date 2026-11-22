#this is the main file 
#It reads the games file, then builds and saves the lexicon, forward index and inverted index.
#to run it type python build_index.py --input sample_games.csv --out data 
#in the terminal

import argparse
import os
import time
from itertools import chain

import pandas as pd

from lexicon import build_lexicon, save_lexicon
from forward_index import build_forward_index, save_forward_index
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="sample_games.csv")
    parser.add_argument("--out", default="data")
    args = parser.parse_args()

    df = load_games(args.input)
    print("Games loaded:", len(df))

    #The lexicon must see exactly the text the forward index will tokenize(title + short description + description)
    #fillna("") so that missing text does not reach the tokenizer as NaN
    start = time.time()
    texts = chain(df["name"].fillna(""), df["short_description"].fillna(""), df["description"].fillna(""))
    lexicon = build_lexicon(texts)
    print("Lexicon: %d words (%.2fs)" % (len(lexicon), time.time() - start))

    start = time.time()
    forward_index = build_forward_index(df, lexicon)
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
