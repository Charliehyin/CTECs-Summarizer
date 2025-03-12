from flask import Blueprint, request, jsonify
import time
from utils.openai_client import client
from config.config import load_config
import re
from scripts.compute_embeddings import split_by_newline, compute_corpus_embeddings, retrieve_sbert
import pickle

rag_bp = Blueprint('rag', __name__)
config = load_config()

@rag_bp.route('/rag', methods=['POST'])
def rag():
    query = request.json.get('message')
    top_k = request.json.get('top_k', 5)
    if not query:
        return jsonify({"error": "Missing message in request"}), 400

    try:
        with open("corpus.txt", "r", encoding="utf-8") as file:
            corpus = split_by_newline(file.read())

        corpus_embeddings = pickle.load(open("corpus_embeddings.pkl", "rb"))
        # Retrieve results
        top_chunks = retrieve_sbert(query, corpus, corpus_embeddings, top_k=top_k)

        for rank, (index, score, text) in enumerate(top_chunks, start=1):
            print(f"Rank: {rank}, Chunk Index: {index}, Score: {score:.4f}")
            print(text)
            print()

        # Combine all top chunks into one string
        combined_text = ""
        for _, _, text in top_chunks:
            combined_text += text + "\n\n"
        
        # Update the top_chunks to include the combined text
        top_chunks_string = combined_text.strip()
        
        return jsonify({"response": top_chunks_string}), 200

    except Exception as e:
        print("Error processing request:", e)
        return jsonify({"error": "Internal server error."}), 500
