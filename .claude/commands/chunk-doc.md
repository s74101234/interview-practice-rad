Split cleaned pages from /tmp/skill_output.json into chunks.

## Steps
1. Read /tmp/skill_output.json (output from /clean-text)
2. For each page:
   - If content <= 600 chars: keep as single chunk
   - Otherwise: split on sentence boundaries (。！？.!?), reassemble into segments <= 600 chars with 1-sentence overlap
3. Each chunk gets an id: "<source>_p<page>_c<index>"
4. Overwrite /tmp/skill_output.json with chunks in format:
   [{"id": "...", "source": "...", "page": "...", "text": "...", "char_count": N}]
5. Print summary: total chunks produced
