#This file makes a small sample of the games file,
#so the index code can be tested and submitted without the full 50,000 games
#to run it type python export_sample.py --input games.csv --out sample_games.csv --size 1000

import argparse

import pandas as pd

from build_index import load_games

#Fixed seed so everyone in the group gets the exact same sample
SEED = 42

#How many edge case rows to force in for each kind
EDGE_ROWS = 5


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="games.csv")
    parser.add_argument("--out", default="sample_games.csv")
    parser.add_argument("--size", type=int, default=1000)
    args = parser.parse_args()

    #load_games already drops missing and duplicate app ids
    df = load_games(args.input)
    print("Games in full file:", len(df))

    #Rows that the tokenizer should definitely be tested on
    #A random sample may not contain them, so we pick them by hand
    missing_short = df[df["short_description"].isna()].head(EDGE_ROWS)
    has_html = df[df["description"].fillna("").str.contains("<", regex=False)].head(EDGE_ROWS)
    non_ascii = df[~df["description"].fillna("").str.isascii()].head(EDGE_ROWS)

    #The random part of the sample. min() so a small input file does not crash sample()
    random_part = df.sample(n=min(args.size, len(df)), random_state=SEED)

    #Joining everything. A game picked twice (edge case and random) is only kept once
    sample = pd.concat([missing_short, has_html, non_ascii, random_part])
    sample = sample.drop_duplicates(subset="app_id").reset_index(drop=True)

    sample.to_csv(args.out, index=False)
    print("Edge cases: %d missing short, %d html, %d non-ascii" % (len(missing_short), len(has_html), len(non_ascii)))
    print("Sample saved:", len(sample), "games ->", args.out)


if __name__ == "__main__":
    main()