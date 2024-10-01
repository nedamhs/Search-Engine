import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
import json
from flask import Flask, render_template, request
import numpy as np
wnl = WordNetLemmatizer()

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    return render_template('search.html')  # You will create this HTML file

# Route for handling the search query
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']  # Get the query
    results = searchFunction(query)  # Call search function
    return render_template('results.html', query=query, results=results)

def load_index():
    with open('inverted_index.json', 'r') as f:
        inverted_index = json.load(f)
        return inverted_index

def get_urls():
    #with open('../webpages/WEBPAGES_RAW/bookkeeping.json', 'r') as f:
    with open('/Users/nedamohseni/PycharmProjects/UCI ICS Search Engine/bookkeeping.json', 'r') as f:
        path_to_url = json.load(f)
        return path_to_url
def searchFunction(query):
    results = []
    result_url = []
    i = 1
    words = query.split(" ")
    for word in words:
        word = wnl.lemmatize(word)
        if word not in inverted_index.keys():
             words.remove(word)

    if len(words) == 0:
        return results
    else:
        # Get the postings for the first word
        common_docs = set(inverted_index[words[0]].keys())


        # Intersect the postings with each subsequent word
        for word in words[1:]:
            posting = set(inverted_index[word].keys())
            common_docs &= posting  # Intersect to keep only common documents

        ranked_results = rank_documents(words, common_docs)

        for docId, score in ranked_results[:20]:
             url = path_to_url[docId]
             if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
             result_url.append(url)

        return result_url

# function to calculate cosine similarity of query vector & document vector
def cosine_similarity(query_vector, doc_vector):
    dot_product = np.dot(query_vector, doc_vector)
    norm_query = np.linalg.norm(query_vector)  # vector length
    norm_doc = np.linalg.norm(doc_vector)      # vector `length
    return dot_product / (norm_query * norm_doc) if norm_query and norm_doc else 0

def rank_documents(query_tokens, result_docs):
    query_vector = []
    doc_vectors = {}

    # Build the query vector and document vectors based on TF-IDF
    for token in query_tokens:
        if token in inverted_index:
            query_vector.append(1)  # Assuming term frequency for query vector
            docs = inverted_index[token]
            for docId in result_docs:  # Only consider documents from boolean retrieval
                if docId in docs:
                    if docId not in doc_vectors:
                        doc_vectors[docId] = []
                    doc_vectors[docId].append(docs[docId][1])  # Append TF-IDF
                else:
                    doc_vectors[docId].append(0)  # No match for this token
        else:
            query_vector.append(0)

    # Calculate cosine similarity for each document
    similarity_scores = {}
    for docId, doc_vector in doc_vectors.items():
        similarity_scores[docId] = cosine_similarity(query_vector, doc_vector)

    # Sort documents by their cosine similarity score
    ranked_docs = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    return ranked_docs

if __name__ == "__main__":
    with open('inverted_index.json', 'r') as f:
        inverted_index = json.load(f)

    #with open('../webpages/WEBPAGES_RAW/bookkeeping.json', 'r') as f:
    with open('/Users/nedamohseni/PycharmProjects/UCI ICS Search Engine/bookkeeping.json', 'r') as f:
        path_to_url = json.load(f)

    # inverted_index = load_index()
    # path_to_url = get_urls()

    app.run(debug=True)