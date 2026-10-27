// Turns literal "[1]" citation markers in the model's answer into markdown
// links pointing at "#cite-1", so react-markdown renders them as normal
// link nodes that we then intercept and style as clickable citation tabs.
// Also un-escapes citations markdown might otherwise treat as a reference
// definition (rare, but [1]: is valid markdown link-reference syntax).
export function prepareCitationMarkdown(text = "") {
  return text.replace(/\[(\d+)\](?!\()/g, (_, n) => `[${n}](#cite-${n})`);
}

export function isCitationHref(href = "") {
  return href.startsWith("#cite-");
}

export function citationIndexFromHref(href = "") {
  return href.replace("#cite-", "");
}
