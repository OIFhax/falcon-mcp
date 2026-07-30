"""
Contains ThreatGraph resources.
"""

THREATGRAPH_USAGE_GUIDE = """
# ThreatGraph Guide

ThreatGraph tools pivot between vertices, edges, and indicator sightings.

## Workflow tips

- Start with `falcon_get_threatgraph_edge_types` to discover valid edge names.
- Use `falcon_get_threatgraph_ran_on` when you have an indicator value and want to find sightings.
- Valid ran-on indicator types are `domain`, `ipv4`, `ipv6`, `md5`, `sha1`, and `sha256`.
- Map Falcon Intelligence type `ip_address` to ThreatGraph type `ipv4` or `ipv6` as appropriate.
- An empty ran-on result means no retained ThreatGraph vertex or sightings were found. Do not treat it as benign intelligence.
- Use summary and vertex tools when you already know the `vertex_type` and `ids` you want to inspect.
- Use edge retrieval after you have a valid vertex ID and edge type.
"""
