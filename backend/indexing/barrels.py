#This is the barrels file.
#Main idea is to divide our inverted index into a bunch of files, where each file will hold particular word ids.
#This is to optimize the searching process for a particular word.

import os 
import json

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

