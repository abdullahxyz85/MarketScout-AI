import pytest

from orchestrator.pipeline import (
    AGENT_SEQUENCE,
    _next_agent_name,
    _progress_after,
    _progress_before,
    _run_step,
    register_queue,
    cleanup_queue,
    get_queue,
)


def test_agent_sequence_has_fifteen_agents():
    assert len(AGENT_SEQUENCE) == 15


def test_idea_guard_is_first_agent():
    assert AGENT_SEQUENCE[0] == "Idea Guard"


def test_research_agent_is_second():
    assert AGENT_SEQUENCE[1] == "Research Agent"


def test_progress_before_first_step_is_zero():
    assert _progress_before(0) == 0


def test_progress_after_last_step_is_hundred():
    assert _progress_after(len(AGENT_SEQUENCE) - 1) == 100


def test_progress_is_monotonically_increasing():
    values = [_progress_before(i) for i in range(len(AGENT_SEQUENCE))] + [_progress_after(len(AGENT_SEQUENCE) - 1)]
    assert values == sorted(values)


def test_progress_after_matches_next_before():
    # The "after" value of step i must equal the "before" value of step i+1,
    # so the progress bar never jumps backward or skips between agents.
    for i in range(len(AGENT_SEQUENCE) - 1):
        assert _progress_after(i) == _progress_before(i + 1)


def test_next_agent_name_after_idea_guard_is_research_agent():
    assert _next_agent_name(0) == "Research Agent"


def test_next_agent_name_returns_following_agent():
    assert _next_agent_name(1) == AGENT_SEQUENCE[2]


def test_next_agent_name_returns_complete_on_last_step():
    assert _next_agent_name(len(AGENT_SEQUENCE) - 1) == "Complete"


@pytest.mark.asyncio
async def test_run_step_returns_result_and_progress_on_success():
    async def ok():
        return {"value": 42}

    errors = []
    result, progress = await _run_step("job-1", 0, errors, "TestAgent", ok())

    # _post_validate may add _validation_warnings / _hallucination_flags — check core value
    assert result.get("value") == 42
    assert progress == _progress_after(0)
    assert errors == []


@pytest.mark.asyncio
async def test_run_step_captures_exception_without_raising():
    async def boom():
        raise ValueError("kaboom")

    errors = []
    result, progress = await _run_step("job-2", 3, errors, "TestAgent", boom())

    assert result == {}
    assert progress == _progress_after(3)
    assert len(errors) == 1
    assert "TestAgent" in errors[0]
    assert "kaboom" in errors[0]


@pytest.mark.asyncio
async def test_run_step_pushes_running_and_completed_events_to_queue():
    job_id = "job-queue-test"
    queue = register_queue(job_id)
    try:
        async def ok():
            return {"ok": True}

        await _run_step(job_id, 1, [], "TestAgent", ok())

        running_event = queue.get_nowait()
        completed_event = queue.get_nowait()

        assert running_event["status"] == "running"
        assert running_event["current_agent"] == AGENT_SEQUENCE[1]
        assert completed_event["status"] == "completed"
        assert completed_event["progress"] == _progress_after(1)
    finally:
        cleanup_queue(job_id)
        assert get_queue(job_id) is None
