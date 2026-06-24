# Draw.io MCP Integration — Skill

## Objectif
Connecter Smart MCP à draw.io via MCP (Model Context Protocol) pour génération de diagrammes en temps réel.

## Architecture
```
Hermes WebUI → Hermes Gateway → Smart MCP Server (port auto) → LLM local (Ollama :11434)
                                                                    → ChromaDB (26 patterns)
                                                                    → XML draw.io
                                                                         → Draw.io editor (app.diagrams.net)
```

## Serveurs MCP

| Serveur | Port | URL locale |
|---------|------|------------|
| Smart MCP Server | Auto | - |
| Draw.io MCP | 8080 | http://192.168.1.100:8080 |

## Diagrammes persistants

Tous les diagrammes sont dans `Smart-MCP/diagrams/` (trackés Git).

| Fichier | Pages | Description |
|---------|-------|-------------|
| `smart-mcp-full-persistent.drawio` | 13 | F1-F17 + Zones A-E (mega diagramme complet) |

| `hermes-smart-mcp-architecture.drawio` | 2 | Architecture Smart MCP + Pipeline |

### Liens permanents GitHub (disponibles après push)
- https://app.diagrams.net/#HIDRIMalek/Smart-MCP/main/diagrams/smart-mcp-full-persistent.drawio

## Endpoints Smart MCP
- `smart_diagram(prompt, context)` — Génère un diagramme XML draw.io
- `health()` — Vérifie que le serveur tourne
- `seed_brain()` — Seed ChromaDB
- `get_brain_stats()` — Stats ChromaDB (patterns, types, feedback)
- `track_budget()` — Suivi des tokens

## Dashboard

- **Tests** : http://192.168.1.100:8050 (mode auto + manuel)
- **Draw.io** : http://192.168.1.100:8080 (si serveur MCP actif)

## CI/CD

- GitHub Actions dans `.github/workflows/ci.yml`
- Tests sans LLM : 208-214 tests, seed ChromaDB dynamique
- Workflow : lint (ruff) → test (pytest ci_tests.py)
