#This is the forward index file.
#The main idea of a forward index is a way to make a list of all the words stored in a document.
#Instead of storing actual words, we will store their words IDs which will be accessed through the lexicon.
#We will also store the word frequency, both in the title and body of document. (This will be used in ranking feature - possibly)
#Every word must already be in the lexicon, otherwise a KeyError is raised.

from tokenizer import tokenize
from collections import Counter
import os
import json

def count_tokens(title_tokens, body_tokens,lexicon):
    #Using counter to get word count of each word in title and body.
    title_words_count = Counter(title_tokens)
    body_words_count = Counter(body_tokens)

    #Creating an empty dictionary result that will store the frequency(count) of each word in title and body.
    #title and body counts have a structure like (word:count).Using set the count will be dropped.
    #Using OR we will have a list of all words in that document (duplicates won't be repeated).
    result = {}

    #Creating a list that will contain all words in the title and body using the OR operator, the counts will be dropped in set.
    all_words = set(title_words_count) | set(body_words_count)

    #Looping over each word and storing its frequency both in title and body in a dictionary.
    #Each document will have it's own dictionary of word ids associated with frequencies.
    for word in all_words:
        result[lexicon[word]] = [title_words_count[word], body_words_count[word]]
    return result

def index_document(title,body,lexicon):
    #Tokenizing the title and body separately and storing the words in a list.
    title_words = tokenize(title)
    body_words = tokenize(body)
     #Counting is done by count_tokens, so the same logic is used for documents that are already tokenized
    return count_tokens(title_words, body_words, lexicon)

#Builds the forward index from games that are already tokenized.
#game_tokens is a dictionary of app_id -> (title_tokens, body_tokens), so tokenize does not run a second time.
def build_forward_index_from_tokens(game_tokens, lexicon):
    forward_index = {}
    for app_id, (title_tokens, body_tokens) in game_tokens.items():
        forward_index[int(app_id)] = count_tokens(title_tokens, body_tokens, lexicon)
    return forward_index

def build_forward_index(df,lexicon): #df(dataframe) is the table of games.
    #Replacing missing short descriptions with an empty string so that joining it with the description does not produce NaN.
    #This creates a cleaned copy of the column, so df itself is not changed.
    short_descriptions = df["short_description"].fillna("")

    #Creating an empty dictionary forward index that will contain dictionaries of each document.
    forward_index = {}

    #Using zip to go through the columns side by side, so each pass of the loop gives values belonging to the same game.
    for app_id, name, short, desc in zip(df["app_id"], df["name"], short_descriptions, df["description"]):
        
        #Using the name of the game as the title
        title = name

        #The body is the short description and the description joined with a space, so the last word of one does not stick to the first word of the other.
        #This is the same text the lexicon was built from, so every word will be found in it.
        body = short + " " + desc

        #Storing the result returned by index_document in a temp variable.
        doc_word_counts = index_document(title,body,lexicon)

        #Using the app id as the key and storing info in the forward index.
        #Converting app_id from a numpy integer (pandas type) to a normal Python integer, so that json can always save it as a key on any machine or library version.
        forward_index[int(app_id)] = doc_word_counts

    return forward_index 

def save_forward_index(forward_index, path):
    #Getting only the folder part from the part for os.makedirs function to make the folder.
    folder = os.path.dirname(path)
    #Checking if the path contains the folder or not as the program will crash if no folder exists.
    if folder:
        os.makedirs(folder, exist_ok=True)
    #Opening the file for writing purposes and naming it f.
    with open(path, "w", encoding="utf-8") as f:
        #Writing the forward index as json text in file.
        json.dump(forward_index, f)

def load_forward_index(path):
    with open(path, "r", encoding="utf-8") as f:
        #Reads the json text and stores it a temp variable 'raw'.
        #All keys in raw are string at this point.
        raw = json.load(f)
    #Creating a forward index that'll store the converted version.
    forward_index = {}
    #Looping over raws to get each game's app id and it's inner dictionary.
    for app_id, words in raw.items():
        #Converting the inner keys (word ids - strings after json load) back to integers. The values [title_count, body_count] are numbers already, so they are kept as they are.
        converted = {int(word_id): counts for word_id, counts in words.items()}
        #Converts the outer key (string) to integer and stores the inner dictionary.
        forward_index[int(app_id)] = converted
    return forward_index