#This file is of the lexicon.
#Lexicon is a data structure in which each entry/ word in a document is assigned a unique id.
#We will then access the words using their ids in the data structures to come forward.

import json
import os
#Lexicon will first maje use of the tokenizer, each enrty/word will first be normalised by tokenizer and then added to lexicon.
from tokenizer import tokenize

#Building the lexicon, taking a list of texts as input.
def build_lexicon(texts):
    lexicon ={}
    #For each text, we are tokenizing its words and saving it in a list of words.
    for text in texts:
        words = tokenize(text)
        #Checking if the word is a part of lexicon.
        #If not, making it the key and associating the dictionary length as the id.
        #1st entry would have id 0, 2nd will have id 1 and so on.
        for word in words:
            if word not in lexicon.keys():
                lexicon[word] = len(lexicon)
    return lexicon

#Saving the lexicon in a file to store in permanently.
def save_lexicon(lexicon, path):
    #Getting only the folder part from the part for os.makedirs function to make the folder.
    folder = os.path.dirname(path)
    #Checking if the path contains the folder or not as the program will crash if no folder exists.
    if folder:
        os.makedirs(folder, exist_ok=True)
    #Opening the file for wrirting purposes and naming it f.
    with open(path, "w", encoding="utf-8") as f:
        #Writing the dictionary/lexicon as json text in file.
        json.dump(lexicon, f)
