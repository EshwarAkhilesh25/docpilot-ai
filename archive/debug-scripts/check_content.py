"""Check document content."""

import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, user="postgres", password="eshwar", database="docmind"
)
conn.autocommit = True
cur = conn.cursor()

# Check Blockchain document
doc_id = "5fa51bae-9e45-497a-9836-bdbd964a451b"
cur.execute("SELECT raw_text FROM document_contents WHERE document_id = %s", (doc_id,))
content = cur.fetchone()
if content:
    print(f"Content length: {len(content[0])}")
    print(f"Content preview: {content[0][:500]}")
else:
    print("No content found")

# Check chunks
cur.execute("SELECT text FROM document_chunks WHERE document_id = %s", (doc_id,))
chunks = cur.fetchall()
print(f"Chunk count: {len(chunks)}")
if chunks:
    print(f"First chunk preview: {chunks[0][0][:500]}")

cur.close()
conn.close()
