# This is the tokenizer file
# We will take the input from our dataset and normalize it
# It will turn raw text into a list of clean words (tokens) for indexing and searching

import html
import re
import unicodedata

#Defining the max length of a token.
# Tokens longer than this are junk (glued sentences, crypto hashes, stretched words).
# 25 chosen from the data, only 127 of 139k words exceeded it, all junk. This was tried and tested first.
MAX_TOKEN_LENGTH = 25

# Replace lookalike characters: curly quotes -> straight, dashes and ellipsis -> space
# Text u2019 - u2026 are unicodes for special characters
CHAR_TABLE = str.maketrans({
    "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"',
    "\u2013": " ", "\u2014": " ", "\u2026": " ",
})

TAG_RE = re.compile(r"<[^>]+>")                  # HTML tags like <b>
URL_RE = re.compile(r"https?://\S+|www\.\S+")    # web addresses
TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)*")  # a word: letters/digits, apostrophes only inside


# Input: a piece of text (string).
# Output: an ordered list of lowercase tokens (repeats kept).
# Returns an empty list if the input is not a string.
def tokenize(text):
    if not isinstance(text, str):
        return []

    text = html.unescape(text)          # &amp; -> &, &#8217; -> curly quote
    text = TAG_RE.sub(" ", text)        # remove tags
    text = URL_RE.sub(" ", text)        # remove URLs
    text = text.translate(CHAR_TABLE)   # curly quotes, dashes, ellipsis
    text = text.lower()

    # Split accented letters into letter + accent mark, then drop every
    # non-ASCII character. "pokémon" -> "pokemon". Non-Latin scripts vanish.
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    tokens = []
    for word in TOKEN_RE.findall(text):
        if word.endswith("'s"):         # sofya's -> sofya
            word = word[:-2]
        if len(word) == 1 and not word.isdigit():   # drop single letters, keep single digits
            continue
        if len(word) > MAX_TOKEN_LENGTH:  # Skip junk like "0x848d..." or sentences with no spaces
            continue
        if word:
            tokens.append(word)
    return tokens