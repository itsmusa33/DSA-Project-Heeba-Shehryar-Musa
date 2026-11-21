#This is the forward index file.
#The main idea of a forward index is a way to make a list of all the words stored in a document.
#Instead of storing actual words, we will store their words IDs which will be accessed through the lexicon.
#We will also store the word frequency, both in the title and body of document. (This will be used in ranking feature - possibily)
#Every word must already be in the lexicon, otherwise a KeyError is raised.

from tokenizer import tokenize
from collections import Counter

def index_document(title,body,lexicon):
    #Tokenizing the title and body separately and storing the words in a list.
    title_words = tokenize(title)
    body_words = tokenize(body)

    #Using counter to get word count of each word in title and body.
    title_words_count = Counter(title_words)
    body_words_count = Counter(body_words)

    #Creating an empty dictionary result that will store the frequency(count) of each word in title and body.
    #title and body counts have a strcuture like (word:count).Using set the count will be dropped.
    #Using OR we will have a list of all words in that document (duplicates won't be repeated).
    result = {}

    #Creating a list that will contain all words in the title and body using the OR operator, the counts will be dropped in set.
    all_words = set(title_words_count) | set(body_words_count)

    #Looping over each word and storing its frequency both in title and body in a dictionary.
    #Each document will have it's own dictionary of word ids associated with frequencies.
    for word in all_words:
        result[lexicon[word]] = [title_words_count[word], body_words_count[word]]
    return result


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
        forward_index[app_id] = doc_word_counts

    return forward_index 



