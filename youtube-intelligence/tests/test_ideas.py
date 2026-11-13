import json

import pytest

from yti.ideas import build_idea_prompt, parse_ideas_response


def sample_payload():
    return [
        {
            "idea_id": f"idea-{i}",
            "title": f"Distinct idea {i}",
            "curiosity_question": f"What is the unique question number {i}?",
            "angle": f"Angle {i}",
            "lens": f"Lens {i}",
            "search_queries": [f"unique search {i}a", f"unique search {i}b"],
        }
        for i in range(10)
    ]


def test_prompt_uses_only_the_narrow_topic_and_requests_distinct_searchable_ideas():
    prompt = build_idea_prompt("Satellites")
    assert "INPUT TOPIC: Satellites" in prompt
    assert "Do not assume a target audience" in prompt
    assert "distinct lens" in prompt
    assert "Do not write scripts" in prompt


def test_prompt_rejects_blank_topic_and_invalid_count():
    with pytest.raises(ValueError):
        build_idea_prompt("  ")
    with pytest.raises(ValueError):
        build_idea_prompt("Satellites", idea_count=1)


def test_parse_accepts_ten_structured_ideas():
    ideas = parse_ideas_response(json.dumps(sample_payload()))
    assert len(ideas) == 10
    assert ideas[0].search_queries == ("unique search 0a", "unique search 0b")


def test_parse_rejects_wrong_count():
    with pytest.raises(ValueError, match="expected exactly 10"):
        parse_ideas_response(json.dumps(sample_payload()[:9]))


def test_parse_rejects_duplicate_lenses():
    payload = sample_payload()
    payload[1]["lens"] = payload[0]["lens"]
    with pytest.raises(ValueError, match="unique lens"):
        parse_ideas_response(json.dumps(payload))


def test_parse_rejects_duplicate_queries_across_ideas():
    payload = sample_payload()
    payload[1]["search_queries"][0] = payload[0]["search_queries"][0]
    with pytest.raises(ValueError, match="search_queries must be unique"):
        parse_ideas_response(json.dumps(payload))
