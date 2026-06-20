# Draw.io MCP Integration — Skill

## Objectif
Connecter Smart MCP à draw.io via MCP (Model Context Protocol)

## Architecture
Smart MCP MCP Server (port automatique) → Hermes Gateway → Draw.io editor

## Endpoints MCP
- smart_diagram(prompt, context) — Génère un diagramme
- health() — Vérifie que le serveur tourne
- seed_brain() — Seed ChromaDB
- get_brain_stats() — Stats ChromaDB
- track_budget() — Suivi des tokens

## Diagrammes importants
- all-diagrams-merged.drawio — Mega-diagramme 10 pages (vue macro)
- smart-mcp-progress.drawio — Suivi de progression F1-F15, Zones A-E
- hermes-smart-mcp-architecture.drawio — Architecture Smart MCP
