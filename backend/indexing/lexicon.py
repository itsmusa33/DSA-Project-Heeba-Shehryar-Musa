#This file is of the lexicon.
#Lexicon is a data structure in which each entry/ word in a document is assigned a unique id.
#We will then access the words using their ids in the data structures to come forward.

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
