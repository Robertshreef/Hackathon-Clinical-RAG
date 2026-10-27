import re


def reorder_citations(llm_text: str, source_chunks: list):
    # Find unique citation indices in order of appearance
    raw_indices = re.findall(r"\[(\d+)\]", llm_text)
    seen = {}
    ordered_sources = []

    for idx_str in raw_indices:
        idx = int(idx_str)
        if idx not in seen and 0 <= idx < len(source_chunks):
            seen[idx] = len(seen) + 1  # Assign next sequential number (1, 2, ...)
            ordered_sources.append(source_chunks[idx])

    # Replace inline tags with the new sequential numbers
    def replace_tag(match):
        idx = int(match.group(1))
        return f"[{seen[idx]}]" if idx in seen else match.group(0)

    clean_text = re.sub(r"\[(\d+)\]", replace_tag, llm_text)

    return clean_text, ordered_sources
