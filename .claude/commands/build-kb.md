Embed chunks from /tmp/skill_output.json and store in Qdrant.

## Usage
/build-kb [collection=<name>]   (default collection: knowledge_base)

## Steps
1. Read /tmp/skill_output.json (output from /chunk-doc)
2. Load GEMINI_API_KEY from .env
3. Call Gemini gemini-embedding-001 API to embed each chunk text in batches of 100 (vector size: 3072, taskType: RETRIEVAL_DOCUMENT)
4. Connect to Qdrant in local path mode (path: backend/data/qdrant)
5. Create collection if it doesn't exist (vector size 3072, COSINE distance)
6. Upsert all points with payload: {id, source, page, text, char_count}
7. Print summary: chunks embedded and stored, collection name
