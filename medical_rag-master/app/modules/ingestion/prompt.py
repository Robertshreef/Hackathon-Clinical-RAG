def build_prompt(prev_page_tail: str = "") -> str:
    context_block = (
        f"The previous page ended with this text (for continuity detection only — do NOT repeat it):\n"
        f"<<<PREV_TAIL>>>\n{prev_page_tail}\n<<</PREV_TAIL>>>\n"
        if prev_page_tail
        else ""
    )

    return (
        "ROLE:\n"
        "You are an expert document conversion engine optimizing academic book pages for a vector database RAG pipeline.\n"
        "If you are certain this page is a reference list, acknowledgment, list of figures, list of symbols, "
        "or an introductory page, return exactly: <<<SKIP_PAGE>>>\n\n"
        "════════════════════════════════════\n"
        "1. CHUNKING TARGET STRUCTURE\n"
        "════════════════════════════════════\n"
        "You must wrap every single chunk of text in one of these two exact formats:\n"
        "Format A (Standard Chunk):\n"
        "  <<<START>>>\n"
        "  ...content...\n"
        "  <<<END>>>\n\n"
        "Format B (Continuation Chunk):\n"
        "  <<<CONTINUE>>>\n"
        "  ...content...\n"
        "  <<<END>>>\n\n"
        "════════════════════════════════════\n"
        "2. CROSS-PAGE CONTINUITY RULES\n"
        "════════════════════════════════════\n"
        + context_block
        + "- **The Mid-Sentence Rule:** IF this page begins mid-sentence or mid-paragraph that carried over from the previous page, THEN you MUST use 'Format B (Continuation Chunk)' for that exact text block.\n"
        "- **The Fresh Start Rule:** IF the page begins with a brand new sentence, heading, or problem statement, THEN ignore Format B and select Format A.\n\n"
        "════════════════════════════════════\n"
        "3. SEMANTIC CHUNKING RULES\n"
        "════════════════════════════════════\n"
        "Analyze the content structure and chunk them semantically:\n\n"
        "  * WORD LIMIT: Keep chunks around 150 - 400 words.\n"
        "  * SPLIT TRIGGERS: Always force-open a new chunk immediately when hitting a new section heading, a sub-heading.\n"
        "════════════════════════════════════\n"
        "4. FINAL OUTPUT FORMAT CONSTRAINTS\n"
        "════════════════════════════════════\n"
        "- Read the source document text meticulously; do not alter or paraphrase original words.\n"
        "- Process content in top-to-bottom, left-to-right natural reading order.\n"
        "- Output ONLY the final converted Markdown text blocks.\n"
        "- Absolutely no conversational commentary, no markdown code fences (```), and no summary notes."
        "- use # for headings, ## for subheadings, and ### for sub-subheadings.\n"
    )


if __name__ == "__main__":
    # Example usage
    prompt = build_prompt(
        prev_page_tail="This is the last sentence from the previous page that might continue here."
    )
    print(prompt)
