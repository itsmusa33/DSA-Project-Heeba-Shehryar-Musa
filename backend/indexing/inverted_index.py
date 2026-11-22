#This is the inverted index file.
#This is the opposite of forward index. Here, with each word id we will associate the document ids where the word is found.
#Along with the word frequency in a particular document's title and body.

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
    
