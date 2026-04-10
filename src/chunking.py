from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        # raise NotImplementedError("Implement SentenceChunker.chunk")
        if not text:
            return []

        # split sentences (giữ dấu câu)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk = " ".join(s.strip() for s in group if s.strip())
            if chunk:
                chunks.append(chunk)
        return chunks

class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        # raise NotImplementedError("Implement RecursiveChunker.chunk")
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        # raise NotImplementedError("Implement RecursiveChunker._split")
        if len(current_text) <= self.chunk_size:
            return [current_text.strip()]

        if not remaining_separators:
            # fallback: hard split
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        sep = remaining_separators[0]

        if sep:
            parts = current_text.split(sep)
        else:
            # last fallback (character-level)
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        chunks = []
        buffer = ""

        for part in parts:
            if buffer:
                candidate = buffer + sep + part
            else:
                candidate = part

            if len(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                if buffer:
                    chunks.extend(self._split(buffer, remaining_separators[1:]))
                buffer = part

        if buffer:
            chunks.extend(self._split(buffer, remaining_separators[1:]))

        return [c.strip() for c in chunks if c.strip()]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    # raise NotImplementedError("Implement compute_similarity")
    if not vec_a or not vec_b:
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)

class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        # raise NotImplementedError("Implement ChunkingStrategyComparator.compare")
        
        fixed_chunks = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        sentence_chunks = SentenceChunker().chunk(text)
        recursive_chunks = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def build(chunks):
            lengths = [len(c) for c in chunks]
            return {
                "count": len(chunks),
                "avg_length": sum(lengths) / len(lengths) if lengths else 0,
                "chunks": chunks
            }

        return {
            "fixed_size": build(fixed_chunks),
            "by_sentences": build(sentence_chunks),
            "recursive": build(recursive_chunks),
        }
