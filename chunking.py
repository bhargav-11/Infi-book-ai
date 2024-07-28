def chunk_by_sentences(
    elements,
    max_chunk_size=400,
    max_sentences=8,
    sentence_delimiters=['.','?','!']
):
    chunks = []
    current_chunk = []
    current_chunk_tokens = 0
    sentence_count = 0

    if len(elements) == 0:
        return chunks, None

    for element in elements:
        text = element["text"]
        metadata = {key: value for key, value in element.items() if key not in ["text", "metadata"]}
        sentence_tokens = sum(text.count(delimiter) for delimiter in sentence_delimiters)
        sentence_count += sentence_tokens

        current_chunk.append(
            {
                "text": text,
                "metadata": {**element.get("metadata", {}), **metadata},
            }
        )

        if sentence_count >= max_sentences or (
            max_chunk_size is not None and current_chunk_tokens + sentence_tokens >= max_chunk_size
        ):
            chunks.append(current_chunk)
            current_chunk = []
            sentence_count = 0
            current_chunk_tokens = 0

        current_chunk_tokens += sentence_tokens

    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks