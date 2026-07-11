import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

import router as router_module
from main import app
from orchestrator.pipeline import register_queue
from schemas.models import ResearchRequest

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"


def test_start_research_rejects_short_idea():
    res = client.post("/research/start", json={"idea": "too short"})
    assert res.status_code == 422


def test_unknown_job_status_returns_404():
    res = client.get("/research/does-not-exist/status")
    assert res.status_code == 404


def test_unknown_job_stream_returns_404():
    res = client.get("/research/does-not-exist/stream")
    assert res.status_code == 404


@pytest.fixture
def fake_final_state():
    return {
        "job_id": "unused",
        "idea": "A fake AI idea for testing purposes",
        "industry": "SaaS",
        "healthcare_mode": False,
        "errors": [],
        "innovation_score": {"innovation_score": 77, "grade": "B"},
        "report": {"market_score": 80, "opportunity_score": 70, "competition_level": "medium"},
        "knowledge_graph": {"nodes": [], "links": [], "node_count": 0, "edge_count": 0},
    }


def test_start_research_completes_and_result_contains_full_payload(monkeypatch, fake_final_state):
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        return dict(fake_final_state, job_id=job_id)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    start_res = client.post(
        "/research/start",
        json={"idea": "A fake AI idea for testing purposes", "industry": "SaaS"},
    )
    assert start_res.status_code == 200
    job_id = start_res.json()["job_id"]

    status_res = client.get(f"/research/{job_id}/status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"

    result_res = client.get(f"/research/{job_id}/result")
    assert result_res.status_code == 200
    result = result_res.json()
    assert result["innovation_score"]["innovation_score"] == 77


def test_start_research_marks_job_failed_on_pipeline_exception(monkeypatch):
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        raise RuntimeError("simulated agent crash")

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    start_res = client.post(
        "/research/start",
        json={"idea": "A fake AI idea for testing purposes", "industry": "SaaS"},
    )
    job_id = start_res.json()["job_id"]

    status_res = client.get(f"/research/{job_id}/status")
    assert status_res.json()["status"] == "failed"

    result_res = client.get(f"/research/{job_id}/result")
    assert result_res.status_code == 500


@pytest.mark.asyncio
async def test_stream_delivers_full_result_when_client_connects_before_completion(monkeypatch, fake_final_state):
    # Regression test: the SSE stream must deliver exactly one done=true event,
    # and that event must carry the full result — not an earlier, incomplete
    # done=true event that would close the stream prematurely (see pipeline.py:
    # run_pipeline() must not push its own done=true event, only the router's
    # _pipeline_task should, after it has assembled the full payload).
    pipeline_may_finish = asyncio.Event()

    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        await pipeline_may_finish.wait()
        return dict(fake_final_state, job_id=job_id)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    job_id = str(uuid.uuid4())
    queue = register_queue(job_id)
    router_module._jobs[job_id] = {
        "status": router_module.JobStatus.RUNNING,
        "created_at": "now",
        "idea": "test",
        "industry": "SaaS",
        "result": None,
    }
    request = ResearchRequest(idea="A fake AI idea for testing purposes", industry="SaaS")

    task = asyncio.ensure_future(router_module._pipeline_task(job_id, request, queue))
    await asyncio.sleep(0)  # let the task start and block inside fake_run_pipeline
    pipeline_may_finish.set()
    await task

    event = queue.get_nowait()
    assert event["done"] is True
    assert event["result"]["innovation_score"]["innovation_score"] == 77
    assert queue.empty()  # exactly one terminal event — no premature done event beat it
