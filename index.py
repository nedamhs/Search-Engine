import json
import math
import os
from collections import defaultdict, OrderedDict
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem import SnowballStemmer

# List of stop words according to https://www.ranks.nl/stopwords
stop_words = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each",
    "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
    "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in",
    "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most",
    "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
]

# Function to parse HTML files using beautiful soup
def parse_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        # fixed_html_content = soup.prettify().lower()
        return soup

def tokenize(text):
    tokens = []
    unique_tags = set()

    # a regex pattern to tokenize words and handle punctuations separately
    pattern = re.compile(r"(?<!\S)[A-Za-z]+(?!\S)|(?<!\S)[A-Za-z]+(?=:(?!\S))")

    # Traverse through all tags and text in the parsed HTML
    for element in text.descendants:
        if element.name:  # If the element is a tag
            tag = element.name
        elif element.string:  # If the element is text
            tag = element.parent.name
            words = pattern.findall(element.string)
            for word in words:
                tokens.append((word, tag))
                unique_tags.add(tag)

    # converting tokens to lower case
    for i in range(len(tokens)):
            word, tag = tokens[i]
            tokens[i] = (word.lower(), tag)

    return tokens

def preprocess_tokens(tokens):
    # remove stop words from token list
    for word,tag in tokens[:]:
            if word in stop_words:
              #print((word,tag))
              tokens.remove((word,tag))

    # Lemmatize the word component of each tuple
    lemmatizer = WordNetLemmatizer()
    for i in range(len(tokens[:])):
            word, tag = tokens[i]
            lemmatized_word = lemmatizer.lemmatize(word)
            # if word != lemmatized_word:
            #     print(word, "---> ", lemmatized_word)
            tokens[i] = (lemmatized_word, tag)

    #stemming
    # stemmer = PorterStemmer()
    # stemmer = SnowballStemmer(language='english')
    # for i in range(len(tokens[:])):
    #         word, tag = tokens[i]
    #         stemmed_word = stemmer.stem(word)
    #         if word != stemmed_word:
    #            print(word, "---> ", stemmed_word)
    #         tokens[i] = (stemmed_word, tag)

    return tokens

def create_inverted_index(tokens,  file_string):
    for word, tag in tokens:
        # token encountered for the first time
        if word not in inverted_index.keys():
            # initializes an empty dictionary as its value of the outer dictionary
            inverted_index[word] = {}
            # the dictionary will store "file_str  as keys"  and their corresponding "[tags] & frequency counts as values".
            inverted_index[word][file_string] = [[tag], 1]
        # token is already a key in outer dic
        else:
            # file string encountered for first time for the corresponding word
            if file_string not in inverted_index[word]:
                # adds file string to inner dic and set its tag and count to 1
                inverted_index[word][file_string] = [[tag], 1]
            #file string already a key in inner dic
            else:
                # increments the count by 1
                inverted_index[word][file_string][1] += 1
                # if tag is encountered for the first time within the doc
                if tag not in inverted_index[word][file_string][0]:
                   inverted_index[word][file_string][0].append(tag)

# Path to the root directory containing folders (WEBPAGES_RAW)
root_directory = '/Users/nedamohseni/PycharmProjects/UCI ICS Search Engine/WEBPAGES_RAW'

tokens = []
inverted_index = defaultdict(list)
total_token_count = 0

# source for iterating through files in a directory.
#https://www.geeksforgeeks.org/how-to-iterate-over-files-in-directory-using-python/
doc_count = 1;
# Iterate through each folder ( folder 0 through 74)
#for folder_num in range(0, 75):
for folder_num in range(0, 2):
    folder_path = os.path.join(root_directory, f'{folder_num}')
    for file_num in os.listdir(folder_path):  # Iterate through each file in the folder
        file_path = os.path.join(folder_path, file_num)
        if os.path.isfile(file_path): # Check if it's a file
            print(doc_count, " Parsing:", file_path)

            text = parse_html_file(file_path)
            tokens = tokenize(text)
            tokens = preprocess_tokens(tokens)

            file_string = str(folder_num) + "/" + str(file_num)
            create_inverted_index(tokens, file_string)
            doc_count = doc_count + 1
            total_token_count += len(tokens)
            if doc_count == 2:
                break
    #break

# sort by words with the least amount of words (ascending)
#inverted_index = OrderedDict(sorted(inverted_index.items(), key=lambda x: len(x[0])))

# calc tf-idf
for token in inverted_index.keys():
         for docID, values in inverted_index[token].items():
             #inverted_index[k][x] = (1 + math.log(y)) * math.log((doc_count / len(inverted_index[k])))
             tf_idf = (1 + math.log(values[1])) * math.log((doc_count / len(inverted_index[token])))
             #tf_idf = values[1] * math.log((doc_count / len(inverted_index[token])))
             inverted_index[token][docID].append(tf_idf)

# sort reverse by high tf-idf
#for token in inverted_index.keys():
#        #inverted_index[k] = OrderedDict(sorted(inverted_index[k].items(), key=lambda x: x[1], reverse=True))
#         inverted_index[token] = OrderedDict(sorted(inverted_index[token].items(), key=lambda x: x[1], reverse=True))

with open('inverted_index.json', 'w') as f:
        json.dump(inverted_index, f)


print("tokens:", len(tokens))
print("tot tokens:", total_token_count)
print("keys:", len(inverted_index.keys()))
#print(inverted_index)
# print(inverted_index['membrane'])



