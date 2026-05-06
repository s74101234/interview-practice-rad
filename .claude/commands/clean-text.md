Clean raw text from /tmp/skill_output.json produced by /parse-doc.

## Steps
1. Read /tmp/skill_output.json
2. For each page, apply:
   - Remove page number patterns (e.g. "- N -", "Page N of M")
   - Normalize multiple whitespace and blank lines
   - Discard pages with fewer than 20 characters after cleaning
3. Overwrite /tmp/skill_output.json with cleaned pages
4. Print summary: pages before and after filtering
