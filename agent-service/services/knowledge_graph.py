from __future__ import annotations

from typing import Any, Dict

import networkx as nx

from schemas.state import ResearchState


def build_knowledge_graph(state: ResearchState) -> Dict[str, Any]:
    """
    Build an evidence knowledge graph linking ideas, competitors, technologies,
    scientific papers, patents, funding rounds, and trends from all agent outputs.
    The graph is serialized to JSON for frontend visualization (vis.js / cytoscape.js compatible).
    """
    G = nx.DiGraph()

    idea = state.get("idea", "Startup Idea")
    industry = state.get("industry", "")

    G.add_node("idea", label=idea[:60], type="idea", color="#6366f1", size=30)

    if industry:
        G.add_node("industry", label=industry, type="industry", color="#a855f7", size=20)
        G.add_edge("idea", "industry", relation="targets_industry")

    competitors_data = state.get("competitors") or {}
    for comp in competitors_data.get("competitors", []):
        name = comp.get("name", "")
        if not name:
            continue
        node_id = f"comp_{name[:20].replace(' ', '_')}"
        G.add_node(
            node_id,
            label=name,
            type="competitor",
            color="#ef4444",
            size=16,
            threat_level=comp.get("threat_level", ""),
            market_share=comp.get("market_share", ""),
        )
        G.add_edge("idea", node_id, relation="competes_with")

    scientific_data = state.get("scientific") or {}
    for i, paper in enumerate(scientific_data.get("relevant_papers", [])[:5]):
        title = paper.get("title", "")
        if not title:
            continue
        node_id = f"paper_{i}"
        G.add_node(
            node_id,
            label=title[:45],
            type="paper",
            color="#10b981",
            size=12,
            year=paper.get("year", ""),
        )
        G.add_edge("idea", node_id, relation="supported_by_research")

    patent_data = state.get("patents") or {}
    for i, patent in enumerate(patent_data.get("existing_patents", [])[:5]):
        title = patent.get("title", "")
        if not title:
            continue
        node_id = f"patent_{i}"
        G.add_node(
            node_id,
            label=title[:45],
            type="patent",
            color="#f59e0b",
            size=12,
            holder=patent.get("holder", ""),
        )
        G.add_edge("idea", node_id, relation="related_patent")

    funding_data = state.get("funding") or {}
    for i, round_ in enumerate(funding_data.get("recent_funding_rounds", [])[:5]):
        company = round_.get("company", "")
        if not company:
            continue
        node_id = f"funding_{i}"
        G.add_node(
            node_id,
            label=company[:40],
            type="funding",
            color="#06b6d4",
            size=14,
            amount=round_.get("amount", ""),
            stage=round_.get("stage", ""),
        )
        G.add_edge("idea", node_id, relation="funding_activity")

    trends_data = state.get("trends") or {}
    for i, trend in enumerate(trends_data.get("trends", [])[:5]):
        name = trend.get("name", "")
        if not name:
            continue
        node_id = f"trend_{i}"
        G.add_node(
            node_id,
            label=name[:40],
            type="trend",
            color="#8b5cf6",
            size=14,
            direction=trend.get("direction", ""),
            impact=trend.get("impact", ""),
        )
        G.add_edge("idea", node_id, relation="affected_by_trend")

    gaps_data = state.get("research_gaps") or {}
    for i, gap in enumerate(gaps_data.get("unexplored_opportunities", [])[:4]):
        if not gap:
            continue
        node_id = f"gap_{i}"
        G.add_node(node_id, label=str(gap)[:40], type="opportunity", color="#22c55e", size=12)
        G.add_edge("idea", node_id, relation="has_opportunity")

    graph_data = nx.node_link_data(G, edges="links")
    return {
        "nodes": graph_data["nodes"],
        "links": graph_data["links"],
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
    }
