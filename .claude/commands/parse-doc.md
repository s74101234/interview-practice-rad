Parse a PDF or PPTX file and output raw text per page/slide.

## Usage
/parse-doc <file_path>

## Steps
1. Determine file type from extension (.pdf or .pptx)
2. For PDF: use pymupdf4llm.to_markdown(file_path, page_chunks=True) to extract text per page
3. For PPTX: use python-pptx to iterate slides and extract title + body text
4. Save output as JSON to /tmp/skill_output.json in format:
   [{"source": "<filename>", "page": "<page_number>", "content": "<text>"}]
5. Print summary: number of pages/slides extracted
