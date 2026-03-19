"""
Contains ThreatGraph resources.
"""

THREATGRAPH_USAGE_GUIDE = """
# ThreatGraph Guide

ThreatGraph tools pivot between vertices, edges, and indicator sightings.

## Workflow tips

- Start with `falcon_get_threatgraph_edge_types` to discover valid edge names.
- Use `falcon_get_threatgraph_ran_on` when you have an indicator value and want to find sightings.
- Use summary and vertex tools when you already know the `vertex_type` and `ids` you want to inspect.
- Use edge retrieval after you have a valid vertex ID and edge type.
"""
