#This is the barrels file.
#Main idea is to divide our inverted index into a bunch of files, where each file will hold particular word ids.
#This is to optimize the searching process for a particular word.

import os 
import json
#OrderedDict is the dict that remembers the order things were added or used.
from collections import OrderedDict

N_BARRELS = 32
#Maximum number of barrels kept in memory at once. One barrel is about 39 MB in RAM, so 8 barrels is about 320 MB.
MAX_CACHED_BARRELS = 8

#Remembering the barrel count of each barrel folder once it has been read from meta.json.
#Keys are folder paths and values are n_barrels.
#So the file is read only on the first lookup and not on every call.
_meta_cache = {}

#Keeping recently used barrels in memory so the same barrel is not parsed from disk again for every word.
#Keys are (folder, barrel_number) and values are the loaded barrels. OrderedDict remembers the order of use, oldest first.
_barrel_cache = OrderedDict()

#n_barrels is the number of barrels
#We will be using 32 as n_barrels for now
def split_into_barrels(inverted_index, n_barrels):
    #Making a list "barrels" and each position in the list will refer to a barrel.
    #Making n_barrels separate empty dictionaries, one for each barrel, before any word is placed.
    barrels = [{} for _ in range(n_barrels)]
    #Looping through inverted index to get word ids and associated entries.
    for word_id, entries in inverted_index.items():
        #Calculating which barrel a word would go into.
        #The remainder of word_id by our selected number of barrels "32" gives the barrel number.
        #Using modulo and not division (word_id // size) because ids are first-seen.
        #So common words have low ids and division put 78% of all postings in barrel 0. (TESTED)
        barrel_number = word_id % n_barrels
        #Putting the word and its list of games into that barrel.
        barrels[barrel_number][word_id] = entries
    #Returning after the loop has finished, so every word is placed.
    return barrels

def save_barrels(barrels,folder):
    #Creating the folder for the barrel files if it does not exist yet. 
    #exist_ok=True stops it from crashing if the folder is already there.
    os.makedirs(folder, exist_ok=True)

    for number, barrel in enumerate(barrels):
        #Building the file name from the barrel number, for example barrel_5.json.
        name = f"barrel_{number}.json"
        #Joining the folder and the file name into one path, using the right slash for the system.
        path = os.path.join(folder, name)
        #Opening the file for writing (it is created if it does not exist) and saving the barrel as json text.
        #The word ids (keys) become strings in the file, so they must be converted back to integers when loading.
        with open(path, "w", encoding="utf-8") as f:
            json.dump(barrel, f)

    #Saving the number of barrels in a small file called meta.json, next to the barrel files.
    #A word's barrel is word_id % n_barrels, so search must use the same count that was used to build.
    #Reading it from this file means the two can never disagree, even if N_BARRELS is changed later.
    meta_path = os.path.join(folder, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"n_barrels": len(barrels)}, f)

def load_barrel(folder,barrel_number):
    name = f"barrel_{barrel_number}.json"
    #Joining the folder and the file name into one path, using the right slash for the system.
    path = os.path.join(folder, name)
    with open(path, "r", encoding="utf-8") as f:
    #Reads the json text and stores it a temp variable 'raw'.
    #raw holds the barrel exactly as it was in the file, so all the word ids (keys) are still strings like "4812".
        raw = json.load(f)
    #Converting the word ids (keys) back to integers. 
    #The values are lists of integers already, so they are kept as they are.
    barrel = {int(word_id): entries for word_id, entries in raw.items()}
    return barrel

#Returns the number of barrels used to build the barrels in this folder.
#It reads meta.json only the first time; after that the stored number is reused.
def get_n_barrels(folder):
    #If this folder was already read, returning the remembered number without touching the disk.
    if folder in _meta_cache:
        return _meta_cache[folder]
    #First time for this folder: reading meta.json, for example {"n_barrels": 32}.
    meta_path = os.path.join(folder, "meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    #Storing the number so the next call finds it in the cache.
    _meta_cache[folder] = meta["n_barrels"]
    return _meta_cache[folder]

#Returns a barrel, loading it from disk only if it is not already in the cache.
def get_barrel(folder, barrel_number):
    #The key is a tuple of folder and barrel number, so barrels from different folders never get mixed up.
    key = (folder, barrel_number)
    #Cache hit if the barrel is already in memory.
    #move_to_end marks it as the most recently used, so it goes to the back of the line for eviction.
    if key in _barrel_cache:
        _barrel_cache.move_to_end(key)
        return _barrel_cache[key]
    #Case for cache miss
    #Loading the barrel from disk and storing it at the end, as the most recently used.
    barrel = load_barrel(folder,barrel_number)
    _barrel_cache[key] = barrel
    #If the cache is over its limit, removing the oldest entry. 
    #last=False removes from the front, which is the least recently used.
    if len(_barrel_cache) > MAX_CACHED_BARRELS:
        _barrel_cache.popitem(last=False)
    return barrel

def get_postings(word_id, folder):
    #Getting the barrel count (read from meta.json only once, then cached).
    n_barrels = get_n_barrels(folder)
    #Working out which barrel holds this word, using the same modulo rule that was used to split.
    barrel_number = word_id % n_barrels
    #Loading only that one barrel file, not the whole inverted index.
    barrel = get_barrel(folder, barrel_number)
    #get returns the value if the key exists, and an empty list if it does not.
    return barrel.get(word_id, [])
