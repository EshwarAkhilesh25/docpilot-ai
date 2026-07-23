"""Check index paths and permissions."""

import os
from pathlib import Path

# Check FAISS index path
faiss_path = Path("storage/faiss_index")
print(f"FAISS index path: {faiss_path.absolute()}")
print(f"FAISS path exists: {faiss_path.exists()}")
if faiss_path.exists():
    print(f"FAISS path is directory: {faiss_path.is_dir()}")
    print(f"FAISS path contents: {os.listdir(faiss_path)}")
else:
    print(f"FAISS parent exists: {faiss_path.parent.exists()}")
    print(
        f"FAISS parent contents: {os.listdir(faiss_path.parent) if faiss_path.parent.exists() else 'N/A'}"
    )

# Check BM25 index path
bm25_path = Path("storage/bm25_index")
print(f"\nBM25 index path: {bm25_path.absolute()}")
print(f"BM25 path exists: {bm25_path.exists()}")
if bm25_path.exists():
    print(f"BM25 path is directory: {bm25_path.is_dir()}")
    print(f"BM25 path contents: {os.listdir(bm25_path)}")
else:
    print(f"BM25 parent exists: {bm25_path.parent.exists()}")
    print(
        f"BM25 parent contents: {os.listdir(bm25_path.parent) if bm25_path.parent.exists() else 'N/A'}"
    )

# Check if we can write to these paths
print(f"\nCan write to storage: {os.access('storage', os.W_OK)}")
if faiss_path.parent.exists():
    print(f"Can write to FAISS parent: {os.access(faiss_path.parent, os.W_OK)}")
