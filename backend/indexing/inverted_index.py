#This is the inverted index file.
#This is the opposite of forward index. Here, with each word id we will associate the document ids where the word is found.
#Along with the word frequency in a particular document's title and body.

import os
import json

def build_inverted_index(forward_index):
    #Initializing an empty inverted index(dictionary).
    #Keys will be word ids and values will be each games app_id along with word occurence in title and body.
    inverted_index = {}

    #Looping through the games in sorted app id order, so every word's list is built already sorted by app id and no separate sort is needed afterwards.
    #Game words are a game's inner dictionary of the format ([word id[title:body]]) where title & body represent occurences.
    for app_id in sorted(forward_index):
        game_words = forward_index[app_id]

        #From each game's inner dictionary, getting the word ids and the word occurences.
        for game_word_id, counts in game_words.items():

            #Using a list of [app_id, title_count, body_count] entries for each word. 
            #As each (word, game) pair occurs only once and we loop over all games of a word at search time anyway.
            #Lists use less memory and give a smaller file than dictionaries, and the ids stay integers when loaded (no typecasting required).
            
            #If the word doesn't exist in inverted index, initializing an empty list for that word id.
            if game_word_id not in inverted_index:
                inverted_index[game_word_id] = []

            #For each word id, appendig the app id (game) and word occurences to its list.    
            inverted_index[game_word_id].append([app_id,counts[0],counts[1]])
    return inverted_index
    
def save_inverted_index(inverted_index, path):
    #Getting only the folder part from the part for os.makedirs function to make the folder.
    folder = os.path.dirname(path)
    #Checking if the path contains the folder or not as the program will crash if no folder exists.
    if folder:
        os.makedirs(folder, exist_ok=True)
    #Opening the file for wrirting purposes and naming it f.
    with open(path, "w", encoding="utf-8") as f:
        #Writing the inverted index as json text in file.
        json.dump(inverted_index, f)

def load_inverted_index(path):
    with open(path, "r", encoding="utf-8") as f:
        #Reads the json text and stores it a temp variable 'raw'.
        #raw will contain the inverted index exactly as it came out of the json file.
        #Only the outer keys (word IDs) are strings, like "0". The values are lists of integers, which JSON keeps as integers.
        raw = json.load(f)
    #Creating an inverted index that'll contain the converted version (typecasting word ids from string to int)
    inverted_index = {}
    #Looping over raw to get the word ids and values (associated info).
    for game_word_id, value in raw.items():
        inverted_index[int(game_word_id)] = value
    #Returning the inverted index with integer keys again.
    return inverted_index