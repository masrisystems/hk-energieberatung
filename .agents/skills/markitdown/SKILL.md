---
name: markitdown
description: Convert local documents and supported URLs to clean Markdown with Microsoft MarkItDown. Use when a user asks to convert, extract, inspect, summarize, or analyze PDFs, Office files, EPUBs, emails, HTML, notebooks, structured text, images, audio, archives, or a directory of those files.
---

# Microsoft MarkItDown

Convert supported non-Markdown sources before inspecting or analyzing their contents.

## Workflow

1. Locate the source file, URL, or directory.
2. Prefer the `markitdown` MCP tools when available:
   - `convert_to_markdown` for one local file.
   - `convert_url_to_markdown` for a URL.
   - `batch_convert_documents` for a directory.
3. If the MCP server is unavailable, use the global CLI:

   ```powershell
   markitdown "path/to/document.pdf"
   markitdown "path/to/document.pdf" -o "path/to/output.md"
   ```

4. Use the extracted Markdown to complete the user's request.

Write converted files only when the user asks for an output file or when a persistent intermediate artifact is necessary. Preserve the source file.

## Supported inputs

MarkItDown supports common PDFs, Word documents, PowerPoint presentations, Excel workbooks, EPUBs, Outlook messages, HTML, Jupyter notebooks, CSV/TSV, JSON/XML/RSS, images, audio, and ZIP archives. Conversion quality and optional OCR or transcription capabilities depend on the installed MarkItDown extras and local services.

## CLI batch example

```powershell
Get-ChildItem -Path "docs" -Include *.pdf,*.docx,*.xlsx -Recurse | ForEach-Object {
    $outputPath = [System.IO.Path]::ChangeExtension($_.FullName, ".md")
    markitdown $_.FullName -o $outputPath
}
```
