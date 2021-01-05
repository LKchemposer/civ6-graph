# General Notes

The dependency graph for Civ VI is a Directed Acyclic Graph (DAG) with 627 nodes and 1125 edges.

A node is one of the following entities:

| Node Type | Attributes |
| - | - |
| Technology | Era, Cost, Eureka, Effects |
| Civic | Era, Inspiration, Effects |
| Resource | Resource Type, Yields, Effects |
| Building | Era, Cost, Effects, Specificity (if unique) |
| Policy | Era, Policy Type, Notes |
| Improvement | Placement, Effects, Plunder, Specificity (if unique) |
| Unit | Era, Unit Type, Cost, Stats, Notes, Specificity (if unique) |
| Wonder | Era, Cost, Effects, Placement |
| Project | Effects |
| District | Effects, Specificity (if unique) |
| Government | Era, Number of Slots, Slots, Effects, Legacy Bonus |
| Civilization | Specificity |
| Leader(s) | Specificity |
| City-state | Specificity |
| Diplomacy | |
| Casus Belli | |
| Atomic Weapon | |

An edge is one of the following connections:

| Edge Type | Application |
| - | - |
| Unlocks | among all entities |
| Boosts | other entities to Technology or Civic |
| Replaces | unique Building, District, or Unit to generic Building, District, or Unit |
| Reveals | Technology to Resource |
| Harvests | Technology to Resource |
| Obsoletes | Civic to Policy, Policy to Policy |
| Upgrades | between Units |
| Builds | specific to Builder to Improvement |

