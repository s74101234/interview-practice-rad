Embed chunks from /tmp/skill_output.json and store in Qdrant.

## Usage
/build-kb [collection=<name>]   (default collection: knowledge_base)

## Steps
1. Read /tmp/skill_output.json (output from /chunk-doc)
2. Load GEMINI_API_KEY from .env
3. Call Gemini text-embedding-004 API to embed each chunk text in batches of 16
4. Connect to Qdrant at localhost:6333
5. Create collection if it doesn't exist (vector size 768, COSINE distance)
6. Upsert all points with payload: {id, source, page, text, char_count}
7. Print summary: chunks embedded and stored, collection name
