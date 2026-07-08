from services.utils import (
    _repair_truncated_json,
    extract_source_urls,
    format_sources_for_prompt,
    parse_json_response,
    truncate_sources,
)


def test_parse_json_response_direct_json():
    assert parse_json_response('{"a": 1}') == {"a": 1}


def test_parse_json_response_markdown_code_block():
    text = 'Here is the result:\n```json\n{"a": 1, "b": 2}\n```\nHope that helps.'
    assert parse_json_response(text) == {"a": 1, "b": 2}


def test_parse_json_response_extracts_largest_object_from_surrounding_text():
    text = 'Sure! {"score": 42, "grade": "B"} — let me know if you need more.'
    assert parse_json_response(text) == {"score": 42, "grade": "B"}


def test_repair_truncated_json_closes_open_array_and_string():
    # Simulates an LLM response cut off mid-array by max_tokens: the string and
    # the array are both still open when generation stopped.
    truncated = '{"items": ["a", "b", "c'
    assert _repair_truncated_json(truncated) == {"items": ["a", "b", "c"]}


def test_repair_truncated_json_closes_nested_object():
    truncated = '{"outer": {"a": 1, "b": 2'
    assert _repair_truncated_json(truncated) == {"outer": {"a": 1, "b": 2}}


def test_repair_truncated_json_returns_none_when_unrecoverable():
    assert _repair_truncated_json("not json and no brackets") is None


def test_parse_json_response_empty_string_flags_parse_error():
    result = parse_json_response("")
    assert result["parse_error"] is True


def test_parse_json_response_unparseable_text_flags_parse_error():
    result = parse_json_response("this is not json at all")
    assert result["parse_error"] is True
    assert result["raw_response"] == "this is not json at all"


def test_truncate_sources_limits_content_length():
    sources = [{"url": "u", "title": "t", "content": "x" * 1000}]
    result = truncate_sources(sources, max_content=10)
    assert len(result[0]["content"]) == 10


def test_extract_source_urls_respects_limit():
    sources = [{"url": f"u{i}"} for i in range(10)]
    assert extract_source_urls(sources, limit=3) == ["u0", "u1", "u2"]


def test_extract_source_urls_skips_entries_without_url():
    sources = [{"url": "u1"}, {}, {"url": "u2"}]
    assert extract_source_urls(sources) == ["u1", "u2"]


def test_format_sources_for_prompt_empty_list():
    assert format_sources_for_prompt([]) == "No web data available."


def test_format_sources_for_prompt_includes_title_and_url():
    sources = [{"title": "Report A", "url": "http://x", "content": "details"}]
    formatted = format_sources_for_prompt(sources)
    assert "Report A" in formatted
    assert "http://x" in formatted
