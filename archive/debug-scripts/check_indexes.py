"""Check vector and BM25 indexes."""

import pickle
import os

# Check FAISS index
faiss_path = "storage/faiss_index"
if os.path.exists(faiss_path):
    files = os.listdir(faiss_path)
    print(f"FAISS index files: {files}")
else:
    print("FAISS index directory does not exist")

# Check BM25 index
bm25_path = "storage/bm25_index/bm25_index.pkl"
if os.path.exists(bm25_path):
    with open(bm25_path, "rb") as f:
        bm25_index = pickle.load(f)
    print("BM25 index loaded successfully")
    print(f"BM25 index type: {type(bm25_index)}")
    if hasattr(bm25_index, "corpus_size"):
        print(f"BM25 corpus size: {bm25_index.corpus_size}")
else:
    print("BM25 index file does not exist")
