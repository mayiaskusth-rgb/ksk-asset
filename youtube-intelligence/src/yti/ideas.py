"""LLM prompt and response validation for broad-topic research ideation.

This module deliberately does not call a model provider. It defines a
provider-neutral prompt and validates the structured response so the actual
LLM adapter can be added without coupling the research contracts to a vendor.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ResearchIdea:
    idea_id: str
    title: str
    curiosity_question: str
    angle: str
    lens: str
    search_queries: tuple[str, ...]

    def __post_init__(self) -> None:
        for field in ("idea_id", "title", "curiosity_question", "angle", "lens"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
        if not isinstance(self.search_queries, tuple) or not 2 <= len(self.search_queries) <= 3:
            raise ValueError("search_queries must contain 2 or 3 queries")
        if any(not isinstance(query, str) or not query.strip() for query in self.search_queries):
            raise ValueError("search_queries cannot contain empty values")


def build_idea_prompt(topic: str, idea_count: int = 10) -> str:
    """Build a narrow-brief prompt that asks for distinct, searchable ideas."""
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("topic must be a non-empty string")
    if isinstance(idea_count, bool) or not isinstance(idea_count, int) or not 2 <= idea_count <= 20:
        raise ValueError("idea_count must be an integer between 2 and 20")

    return f"""You are a YouTube research ideation assistant.

INPUT TOPIC: {topic.strip()}

Generate exactly {idea_count} distinct YouTube research ideas around this topic.

Rules:
- Treat the input as the entire brief. Do not assume a target audience, geography,
  language, format, narrative, or preferred editorial angle.
- Explore different underlying questions and subject areas, not cosmetic
  rewordings of one idea.
- Consider scientific, practical, historical, human, economic, technological,
  surprising, controversial-but-safe, and counterintuitive directions where
  relevant. Do not force every category.
- Each idea must be independently searchable on YouTube.
- Each idea must have a distinct lens. Do not repeat a lens or substantially
  overlap another idea's central question.
- Do not write scripts, story arcs, hooks, thumbnails, or finished titles.
- Do not claim that an idea is popular or successful. These are hypotheses to
  validate with YouTube evidence.
- Return only valid JSON: an array of objects with exactly these keys:
  idea_id, title, curiosity_question, angle, lens, search_queries.
- search_queries must contain 2 or 3 natural YouTube search queries per idea.
- Use concise, plain English. No markdown fences or surrounding commentary.
"""


def parse_ideas_response(raw: str, expected_count: int = 10) -> list[ResearchIdea]:
    """Parse and validate a model response; fail closed on malformed output."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("LLM response must be non-empty text")
    if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 1:
        raise ValueError("expected_count must be a positive integer")

    try:
        payload: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response must be a JSON array") from exc
    if not isinstance(payload, list):
        raise ValueError("LLM response must be a JSON array")
    if len(payload) != expected_count:
        raise ValueError(f"expected exactly {expected_count} ideas; received {len(payload)}")

    required = {
        "idea_id", "title", "curiosity_question", "angle", "lens", "search_queries"
    }
    ideas: list[ResearchIdea] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError(f"idea at index {index} must contain exactly {sorted(required)}")
        queries = item["search_queries"]
        if not isinstance(queries, list):
            raise ValueError(f"idea at index {index}: search_queries must be an array")
        ideas.append(
            ResearchIdea(
                idea_id=item["idea_id"],
                title=item["title"],
                curiosity_question=item["curiosity_question"],
                angle=item["angle"],
                lens=item["lens"],
                search_queries=tuple(queries),
            )
        )

    def normalized(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()

    for field in ("idea_id", "title", "curiosity_question", "lens"):
        values = [normalized(getattr(idea, field)) for idea in ideas]
        if len(values) != len(set(values)):
            raise ValueError(f"ideas must have unique {field} values")

    all_queries = [normalized(query) for idea in ideas for query in idea.search_queries]
    if len(all_queries) != len(set(all_queries)):
        raise ValueError("search_queries must be unique across ideas")

    return ideas
