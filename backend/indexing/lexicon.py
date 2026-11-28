#This file is of the lexicon.
#Lexicon is a data structure in which each entry/ word in a document is assigned a unique id.
#We will then access the words using their ids in the data structures to come forward.

import json
import os
#Lexicon will first make use of the tokenizer, each entry/word will first be normalised by tokenizer and then added to lexicon.
from tokenizer import tokenize

#Takes a list of token lists (each inner list is what tokenize returns for one text) and builds the lexicon from them.
#Used when the texts have already been tokenized, so tokenize does not run a second time.
def build_lexicon_from_tokens(token_lists):
    lexicon = {}
    #Going through the token list of each text one by one.
    for words in token_lists:
        #If the word is new, its id is the current size of the lexicon: 1st word gets 0, 2nd gets 1 and so on.
        #Ids are never renumbered, so new words can be added later without changing old ids.
        for word in words:
            if word not in lexicon:
                lexicon[word] = len(lexicon)
    return lexicon


#Building the lexicon, taking a list of texts as input.
#Each text is tokenized first, then the token lists are passed to build_lexicon_from_tokens.
def build_lexicon(texts):
    token_lists = [tokenize(text) for text in texts]
    return build_lexicon_from_tokens(token_lists)

def save_lexicon(lexicon, path):
    #Getting only the folder part from the part for os.makedirs function to make the folder.
    folder = os.path.dirname(path)
    #Checking if the path contains the folder or not as the program will crash if no folder exists.
    if folder:
        os.makedirs(folder, exist_ok=True)
    #Opening the file for writing purposes and naming it f.
    with open(path, "w", encoding="utf-8") as f:
        #Writing the dictionary/lexicon as json text in file.
        json.dump(lexicon, f)

#Loading the lexicon for reading purposes.
def load_lexicon(path):
    with open(path, "r", encoding="utf-8") as f:
        #Reads the json text and rebuilds the dictionary(lexicon).
        return json.load(f)
