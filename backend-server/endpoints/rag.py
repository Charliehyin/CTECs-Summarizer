from flask import Blueprint, request, jsonify
from config.config import load_config
from scripts.compute_embeddings import split_by_newline, retrieve_sbert
import pickle

rag_bp = Blueprint('rag', __name__)
config = load_config()

@rag_bp.route('/rag', methods=['POST'])
def rag():
    query = request.json.get('message')
    top_k = request.json.get('top_k', 10)
    if not query:
        return jsonify({"error": "Missing message in request"}), 400

    try:
        # with open("corpus.txt", "r", encoding="utf-8") as file:
        #     corpus = split_by_newline(file.read())

        with open("essay_corpus.txt", "r", encoding="utf-8") as file:
            essay_corpus = split_by_newline(file.read())

        with open("summary_corpus.txt", "r", encoding="utf-8") as file:
            summary_corpus = split_by_newline(file.read())

        corpus_embeddings = pickle.load(open("corpus_embeddings.pkl", "rb"))
        essay_corpus_embeddings = pickle.load(open("essay_corpus_embeddings.pkl", "rb"))
        summary_corpus_embeddings = pickle.load(open("summary_corpus_embeddings.pkl", "rb"))

        # Retrieve results
        # top_chunks = retrieve_sbert(query, corpus, corpus_embeddings, top_k=top_k)
        top_chunks_essay = retrieve_sbert(query, essay_corpus, essay_corpus_embeddings, top_k=top_k)
        top_chunks_summary = retrieve_sbert(query, summary_corpus, summary_corpus_embeddings, top_k=3)

        top_chunks = top_chunks_essay + top_chunks_summary

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
