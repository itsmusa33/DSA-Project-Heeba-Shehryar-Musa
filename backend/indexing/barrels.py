#This is the barrels file.
#Main idea is to divide our inverted index into a bunch of files, where each file will hold particular word ids.
#This is to optimize the searching process for a particular word.

#n_barrels is the number of barrels
#We will be using 32 as n_barrels for now
def spilt_into_barrels(inverted_index, n_barrels):
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

