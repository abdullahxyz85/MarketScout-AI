from services.knowledge_graph import build_knowledge_graph


def _base_state(**overrides):
    state = {
        "idea": "AI meal planning app",
        "industry": "HealthTech",
        "competitors": None,
        "scientific": None,
        "patents": None,
        "funding": None,
        "trends": None,
        "research_gaps": None,
    }
    state.update(overrides)
    return state


def test_build_knowledge_graph_uses_links_key_not_edges():
    # Regression test: networkx>=3.6's node_link_data() defaults to an "edges"
    # key unless edges="links" is passed explicitly, which previously caused
    # a KeyError deep in the pipeline and silently failed every research job.
    graph = build_knowledge_graph(_base_state())
    assert "links" in graph
    assert "edges" not in graph


def test_build_knowledge_graph_always_includes_idea_node():
    graph = build_knowledge_graph(_base_state())
    ids = [n["id"] for n in graph["nodes"]]
    assert "idea" in ids
    assert graph["node_count"] == len(graph["nodes"])
    assert graph["edge_count"] == len(graph["links"])


def test_build_knowledge_graph_adds_industry_node_and_edge():
    graph = build_knowledge_graph(_base_state(industry="HealthTech"))
    ids = [n["id"] for n in graph["nodes"]]
    assert "industry" in ids
    relations = [l["relation"] for l in graph["links"]]
    assert "targets_industry" in relations


def test_build_knowledge_graph_adds_competitor_nodes():
    state = _base_state(competitors={
        "competitors": [
            {"name": "Noom", "threat_level": "high", "market_share": "15%"},
            {"name": "MyFitnessPal", "threat_level": "high", "market_share": "20%"},
        ]
    })
    graph = build_knowledge_graph(state)
    competitor_nodes = [n for n in graph["nodes"] if n["type"] == "competitor"]
    assert len(competitor_nodes) == 2


def test_build_knowledge_graph_skips_competitors_without_a_name():
    state = _base_state(competitors={"competitors": [{"threat_level": "high"}]})
    graph = build_knowledge_graph(state)
    competitor_nodes = [n for n in graph["nodes"] if n["type"] == "competitor"]
    assert competitor_nodes == []


def test_build_knowledge_graph_handles_missing_optional_fields():
    # Every field is None — should not raise, just produce a minimal graph.
    graph = build_knowledge_graph(_base_state(industry=""))
    assert graph["node_count"] == 1  # just the idea node
    assert graph["edge_count"] == 0
