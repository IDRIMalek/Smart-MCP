"""
📊 Smart MCP Pipeline — Tableau de Bord v2
ChromaDB patterns + Tests >200 + Mode Auto/Manuel amélioré
IP dynamique (détection auto de 192.168.1.100)
"""
import json, os, sys, threading, time, socket
from datetime import datetime
from pathlib import Path

import dash, plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, callback, ctx
from flask import Flask, request, jsonify

sys.path.insert(0, str(Path(__file__).parent.parent))
from brain.rag import RAGBrain, get_brain
from dashboard.test_runner import get_stats, run_batch, _save_results, _load_results, RESULTS_FILE

# ── Détection IP locale dynamique ──────────────────────
def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("192.168.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.100"

LOCAL_IP = _local_ip()
APP_TITLE = "🧪 Smart MCP Pipeline"
AUTO_REFRESH_MS = 3000

MACRO_COLORS = {
    "FORME": "#FF6B6B",
    "TABLEAU": "#4FC3F7",
    "KANBAN": "#81C784",
    "AGENDA": "#FFD54F",
    "GANTT": "#FF9800",
    "TEXTE": "#CE93D8",
}

# ── Connexion ChromaDB (chemin absolu — HOME peut être modifié par Hermes) ──
CHROMA_PATH = "/home/malek/.hermes/profiles/default2/home/.smart-mcp/brain"
try:
    brain = RAGBrain(persist_dir=CHROMA_PATH)
    patterns = brain.list_patterns()
    stats_chroma = brain.get_stats()
except Exception as e:
    print(f"[ChromaDB] Erreur: {e}")
    patterns = []
    stats_chroma = {"patterns_count": 0, "feedback_count": 0, "types": {}}

# ── Helpers ──────────────────────────────────────────

def _c(s):
    if s >= 1000: return f"{s/1000:.1f}s"
    return f"{s:.0f}ms"

def _run_tests_bg(macro_filter=""):
    def _run():
        try:
            run_batch(macro_filter=macro_filter)
        except Exception as e:
            print(f"[BG] {e}")
    t = threading.Thread(target=_run, daemon=True)
    t.start()

def _clear_results():
    if RESULTS_FILE.exists():
        RESULTS_FILE.unlink()

def _pattern_badge(tag: str) -> str:
    tag_colors = {
        "forme": "#FF6B6B", "shape": "#FF6B6B",
        "architecture": "#4FC3F7", "microservices": "#4FC3F7", "pipeline": "#4FC3F7",
        "couleur": "#81C784", "color": "#81C784", "palette": "#81C784",
        "sequence": "#FFD54F", "data": "#FF9800",
    }
    c = tag_colors.get(tag, "#888")
    return f'<span style="background:{c};color:#fff;padding:1px 6px;border-radius:8px;font-size:10px;margin:1px">{tag}</span>'


# ── API Flask ──────────────────────────────────────

server = Flask(__name__)

@server.route("/api/result", methods=["POST"])
def api_add_result():
    """Reçoit un résultat de test depuis Hermes WebUI (mode MANUEL)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Body JSON requis"}), 400
        data["source"] = "manual"
        data["timestamp"] = data.get("timestamp", datetime.now().isoformat())
        results = _load_results()
        results.append(data)
        _save_results(results)
        return jsonify({"success": True, "test_id": data.get("test_id", "?"), "total": len(results)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@server.route("/api/results", methods=["GET"])
def api_get_results():
    return jsonify({"results": _load_results()})

@server.route("/api/stats", methods=["GET"])
def api_get_stats():
    return jsonify(get_stats())

@server.route("/api/chromadb", methods=["GET"])
def api_chromadb():
    """Expose les patterns ChromaDB via API REST"""
    try:
        return jsonify({
            "patterns_count": len(patterns),
            "types": stats_chroma.get("types", {}),
            "patterns": patterns[:50]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Dash app ──────────────────────────────────────

app = dash.Dash(__name__, title=APP_TITLE, server=server)
app.layout = html.Div([

    # ── Header ──
    html.Div([
        html.H1(APP_TITLE, style={"margin": "0", "fontSize": "20px"}),
        html.Span(id="mode-badge", style={"marginLeft": "12px", "padding": "2px 10px",
                                           "borderRadius": "10px", "display": "inline-block",
                                           "fontSize": "12px", "fontWeight": "bold"}),
        html.Span(id="total-badge", style={"fontSize": "13px", "color": "#aaa", "marginLeft": "15px"}),
        html.Span(f"🌐 {LOCAL_IP}:8050", style={"fontSize": "11px", "color": "#4FC3F7",
                                                 "marginLeft": "auto", "fontFamily": "monospace"}),
        html.Span(id="last-update", style={"fontSize": "12px", "color": "#666", "marginLeft": "15px"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "12px 20px",
              "background": "#1a1a2e", "color": "white", "borderRadius": "8px 8px 0 0"}),

    # ── ChromaDB Patterns Section ──
    html.Div(id="chromadb-section", style={"padding": "12px 20px", "background": "#16213e",
                                            "borderBottom": "1px solid #282a36"}),

    # ── Controls bar ──
    html.Div([
        html.Div([
            html.Button("▶️ Tous", id="btn-run-all", n_clicks=0,
                       style={"background": "#4CAF50", "color": "white", "border": "none",
                              "padding": "6px 14px", "borderRadius": "4px", "cursor": "pointer",
                              "fontSize": "13px", "fontWeight": "bold"}),
            html.Button("🔄 FORME", id="btn-run-forme", n_clicks=0,
                       style={"background": MACRO_COLORS["FORME"], "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button("📊 TABLEAU", id="btn-run-tableau", n_clicks=0,
                       style={"background": MACRO_COLORS["TABLEAU"], "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button("📋 KANBAN", id="btn-run-kanban", n_clicks=0,
                       style={"background": MACRO_COLORS["KANBAN"], "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button("📅 AGENDA", id="btn-run-agenda", n_clicks=0,
                       style={"background": MACRO_COLORS["AGENDA"], "color": "#333", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button("📈 GANTT", id="btn-run-gantt", n_clicks=0,
                       style={"background": MACRO_COLORS["GANTT"], "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button("💬 TEXTE", id="btn-run-texte", n_clicks=0,
                       style={"background": MACRO_COLORS["TEXTE"], "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "4px", "alignItems": "center"}),
        html.Div([
            html.Button("⏸️ Pause", id="btn-pause", n_clicks=0,
                       style={"background": "#FF9800", "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button("🗑️ Reset", id="btn-reset", n_clicks=0,
                       style={"background": "#f44336", "color": "white", "border": "none",
                              "padding": "6px 10px", "borderRadius": "4px", "cursor": "pointer", "fontSize": "12px"}),
            html.Button(id="btn-mode", n_clicks=0,
                       style={"color": "white", "border": "none",
                              "padding": "6px 12px", "borderRadius": "4px", "cursor": "pointer",
                              "fontSize": "12px", "fontWeight": "bold"}),
        ], style={"display": "flex", "gap": "4px"}),
    ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
              "padding": "8px 20px", "background": "#16213e", "flexWrap": "wrap"}),

    # Run status
    html.Div(id="run-status", style={"padding": "4px 20px", "fontSize": "12px", "color": "#888",
                                      "background": "#16213e"}),

    # Charts
    html.Div([
        html.Div([
            html.H3("✅ Succès par macro", style={"margin": "0 0 8px 0", "fontSize": "14px", "color": "#eee"}),
            dcc.Graph(id="chart-success-rate", style={"height": "220px"}),
        ], style={"flex": "1", "padding": "12px", "background": "#1a1a2e", "borderRadius": "8px", "margin": "0 6px"}),
        html.Div([
            html.H3("📈 Tendances (derniers tests)", style={"margin": "0 0 8px 0", "fontSize": "14px", "color": "#eee"}),
            dcc.Graph(id="chart-trend", style={"height": "220px"}),
        ], style={"flex": "2", "padding": "12px", "background": "#1a1a2e", "borderRadius": "8px", "margin": "0 6px"}),
    ], style={"display": "flex", "padding": "6px 14px 8px 14px", "gap": "4px"}),

    # Mode Manuel : formulaire intégré (plus de curl)
    html.Div(id="manual-form", style={"display": "none", "padding": "12px 20px",
                                       "background": "#1a3a2a",
                                       "borderLeft": "4px solid #4CAF50"}),

    # Filters
    html.Div([
        html.Div([
            html.Span("🔍 Filtrer : ", style={"fontSize": "12px", "color": "#aaa", "marginRight": "10px"}),
            dcc.Dropdown(id="filter-source", options=[
                {"label": "📦 Toutes sources", "value": ""},
                {"label": "🤖 Auto", "value": "auto"},
                {"label": "🧑 Manuel", "value": "manual"},
            ], value="", clearable=False, style={"width": "140px", "fontSize": "12px", "display": "inline-block"}),
            dcc.Dropdown(id="filter-macro", options=[
                {"label": "📦 Toutes macros", "value": ""},
                {"label": "🔴 FORME", "value": "FORME"},
                {"label": "🔵 TABLEAU", "value": "TABLEAU"},
                {"label": "🟢 KANBAN", "value": "KANBAN"},
                {"label": "🟡 AGENDA", "value": "AGENDA"},
                {"label": "🟠 GANTT", "value": "GANTT"},
                {"label": "🟣 TEXTE", "value": "TEXTE"},
            ], value="", clearable=False, style={"width": "150px", "fontSize": "12px",
                                                  "display": "inline-block", "marginLeft": "6px"}),
            dcc.Dropdown(id="filter-status", options=[
                {"label": "📦 Tous status", "value": ""},
                {"label": "✅ Success", "value": "success"},
                {"label": "⚠️ Classifié OK", "value": "classified_ok"},
                {"label": "🟡 XML invalide", "value": "xml_invalid"},
                {"label": "❌ Échec", "value": "failed"},
            ], value="", clearable=False, style={"width": "160px", "fontSize": "12px",
                                                  "display": "inline-block", "marginLeft": "6px"}),
            dcc.Dropdown(id="filter-model", options=[], value="", clearable=False,
                        style={"width": "180px", "fontSize": "12px", "display": "inline-block", "marginLeft": "6px"}),
            html.Span(id="filter-count", style={"fontSize": "12px", "color": "#888", "marginLeft": "12px"}),
        ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "padding": "6px 0"}),
    ], style={"padding": "0 14px"}),

    # Results table
    html.Div([
        html.H3("📋 Résultats", style={"margin": "0 0 4px 0", "fontSize": "14px", "color": "#eee"}),
        html.Span("💡 Reset = vide les résultats (pas la ChromaDB). Source: auto = test auto, manu = test via Hermes",
                  style={"fontSize": "11px", "color": "#666", "fontStyle": "italic", "display": "block", "marginBottom": "6px"}),
        html.Div(id="results-table", style={"maxHeight": "400px", "overflowY": "auto", "marginTop": "4px"}),
    ], style={"padding": "8px 20px 16px 20px", "background": "#1a1a2e",
               "margin": "0 14px 14px 14px", "borderRadius": "8px"}),

    dcc.Interval(id="auto-refresh", interval=AUTO_REFRESH_MS, n_intervals=0),
    dcc.Store(id="paused", data=False),
    dcc.Store(id="manual-mode", data=False),
    dcc.ConfirmDialog(id="confirm-reset",
                      message="⚠️ Reset = vide uniquement results.json.\nLa ChromaDB (patterns XML) est INTACTE. Continuer ?"),
], style={"fontFamily": "-apple-system, BlinkMacSystemFont, sans-serif",
           "background": "#0f3460", "minHeight": "100vh", "color": "#ccc"})


# ── Callback ChromaDB ──────────────────────────────

@callback(
    Output("chromadb-section", "children"),
    Input("auto-refresh", "n_intervals"),
)
def render_chromadb(n):
    """Affiche les stats ChromaDB en haut du dashboard"""
    count = len(patterns)
    types = stats_chroma.get("types", {})
    forme = types.get("forme", 0)
    archi = types.get("architecture", 0)
    generic = types.get("generic", 0)

    # Tags cloud
    all_tags = set()
    for p in patterns[:20]:
        for t in p.get("tags", []):
            all_tags.add(t.strip())

    tag_badges = [html.Span(t, style={
        "background": "#4FC3F7" if t in ("architecture","microservices","pipeline","sequence","data","etl","3-tiers","ci/cd") else
                      "#FF6B6B" if t in ("forme","shape","carre","cercle","triangle","losange","cylindre") else
                      "#81C784" if t in ("couleur","color","palette") else "#888",
        "color": "white", "padding": "2px 8px", "borderRadius": "10px",
        "fontSize": "10px", "margin": "2px", "display": "inline-block"
    }) for t in sorted(all_tags)[:25]]

    return html.Div([
        html.Div([
            html.H3("🧠 ChromaDB — Patterns", style={"margin": "0 0 8px 0", "fontSize": "15px", "color": "#eee"}),
            # Stats cards
            html.Div([
                html.Div([
                    html.Span("📦", style={"fontSize": "24px"}),
                    html.Div([
                        html.Div(str(count), style={"fontSize": "28px", "fontWeight": "bold", "color": "#4FC3F7"}),
                        html.Div("Patterns", style={"fontSize": "11px", "color": "#888"}),
                    ], style={"marginLeft": "10px"}),
                ], style={"display": "flex", "alignItems": "center", "background": "#1a1a2e",
                          "padding": "8px 16px", "borderRadius": "8px", "flex": "1"}),
                html.Div([
                    html.Span("🔴", style={"fontSize": "24px"}),
                    html.Div([
                        html.Div(str(forme), style={"fontSize": "28px", "fontWeight": "bold", "color": "#FF6B6B"}),
                        html.Div("Formes", style={"fontSize": "11px", "color": "#888"}),
                    ], style={"marginLeft": "10px"}),
                ], style={"display": "flex", "alignItems": "center", "background": "#1a1a2e",
                          "padding": "8px 16px", "borderRadius": "8px", "flex": "1"}),
                html.Div([
                    html.Span("🔵", style={"fontSize": "24px"}),
                    html.Div([
                        html.Div(str(archi), style={"fontSize": "28px", "fontWeight": "bold", "color": "#4FC3F7"}),
                        html.Div("Architecture", style={"fontSize": "11px", "color": "#888"}),
                    ], style={"marginLeft": "10px"}),
                ], style={"display": "flex", "alignItems": "center", "background": "#1a1a2e",
                          "padding": "8px 16px", "borderRadius": "8px", "flex": "1"}),
                html.Div([
                    html.Span("🟢", style={"fontSize": "24px"}),
                    html.Div([
                        html.Div(str(generic), style={"fontSize": "28px", "fontWeight": "bold", "color": "#81C784"}),
                        html.Div("Génériques", style={"fontSize": "11px", "color": "#888"}),
                    ], style={"marginLeft": "10px"}),
                ], style={"display": "flex", "alignItems": "center", "background": "#1a1a2e",
                          "padding": "8px 16px", "borderRadius": "8px", "flex": "1"}),
            ], style={"display": "flex", "gap": "8px", "marginBottom": "8px"}),
            # Tags cloud
            html.Div([
                html.Span("🏷️ Tags : ", style={"fontSize": "11px", "color": "#aaa", "marginRight": "6px"}),
                *tag_badges,
            ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "center", "padding": "4px 0"}),
            # Pattern list (scrollable)
            html.Details([
                html.Summary("📋 Liste des 26 patterns (cliquer pour ouvrir)",
                            style={"fontSize": "12px", "color": "#aaa", "cursor": "pointer",
                                   "padding": "4px 0"}),
                html.Div([
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("#", style={"padding": "2px 6px", "fontSize": "10px", "color": "#555"}),
                            html.Th("Titre", style={"padding": "2px 6px", "fontSize": "10px", "color": "#aaa"}),
                            html.Th("Tags", style={"padding": "2px 6px", "fontSize": "10px", "color": "#aaa"}),
                            html.Th("Source", style={"padding": "2px 6px", "fontSize": "10px", "color": "#aaa"}),
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(str(i+1), style={"padding": "2px 6px", "fontSize": "10px", "color": "#555"}),
                                html.Td(p.get("title","")[:50], style={"padding": "2px 6px", "fontSize": "10px", "color": "#ccc"}),
                                html.Td(",".join(p.get("tags",[]))[:30], style={"padding": "2px 6px", "fontSize": "9px", "color": "#888"}),
                                html.Td(p.get("source","")[:10], style={"padding": "2px 6px", "fontSize": "10px", "color": "#666"}),
                            ], style={"borderBottom": "1px solid #282a36"})
                            for i, p in enumerate(patterns)
                        ])
                    ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "11px"})
                ], style={"maxHeight": "300px", "overflowY": "auto", "marginTop": "4px"}),
            ], style={"marginTop": "4px"}),
        ]),
    ])


# ── Callbacks ──────────────────────────────────────

@callback(
    [Output("paused", "data"), Output("btn-pause", "children")],
    Input("btn-pause", "n_clicks"), State("paused", "data"),
    prevent_initial_call=True,
)
def toggle_pause(n, p):
    return (not p, "▶️ Reprendre" if not p else "⏸️ Pause")


@callback(
    Output("confirm-reset", "displayed"),
    Input("btn-reset", "n_clicks"),
    prevent_initial_call=True,
)
def ask_reset(n):
    return True


@callback(
    [Output("manual-mode", "data"),
     Output("btn-mode", "children"),
     Output("btn-mode", "style"),
     Output("mode-badge", "children"),
     Output("mode-badge", "style"),
     Output("manual-form", "children"),
     Output("manual-form", "style")],
    Input("btn-mode", "n_clicks"),
    State("manual-mode", "data"),
    prevent_initial_call=True,
)
def toggle_mode(n, mode):
    """Bascule AUTO ↔ MANUEL avec formulaire intégré (plus de curl)"""
    new_mode = not mode
    if new_mode:
        badge = "🔴 MANUEL"
        badge_style = {"background": "#d9534f", "color": "white", "marginLeft": "12px",
                       "padding": "2px 10px", "borderRadius": "10px", "display": "inline-block",
                       "fontSize": "12px", "fontWeight": "bold"}
        btn_style = {"background": "#d9534f", "color": "white", "border": "none",
                     "padding": "6px 12px", "borderRadius": "4px", "cursor": "pointer",
                     "fontSize": "12px", "fontWeight": "bold"}
        # Formulaire intégré — plus besoin de curl
        form = html.Div([
            html.H4("📝 Enregistrer un test manuel", style={"margin": "0 0 6px 0", "fontSize": "13px", "color": "#eee"}),
            html.Div([
                html.Div([
                    html.Label("Test ID :", style={"fontSize": "11px", "color": "#aaa", "display": "block"}),
                    dcc.Input(id="man-test-id", type="text", placeholder="ex: man-042", value=f"man-{int(time.time())%100000}",
                             style={"width": "140px", "padding": "4px 6px", "fontSize": "11px", "background": "#111",
                                    "border": "1px solid #333", "color": "#4FC3F7", "borderRadius": "4px"}),
                ], style={"flex": "1"}),
                html.Div([
                    html.Label("Macro :", style={"fontSize": "11px", "color": "#aaa", "display": "block"}),
                    dcc.Dropdown(id="man-macro", options=[
                        {"label": "🔴 FORME", "value": "FORME"},
                        {"label": "🔵 TABLEAU", "value": "TABLEAU"},
                        {"label": "🟢 KANBAN", "value": "KANBAN"},
                        {"label": "🟡 AGENDA", "value": "AGENDA"},
                        {"label": "🟠 GANTT", "value": "GANTT"},
                        {"label": "🟣 TEXTE", "value": "TEXTE"},
                    ], value="FORME", clearable=False, style={"width": "130px", "fontSize": "11px"}),
                ], style={"flex": "1"}),
                html.Div([
                    html.Label("Statut :", style={"fontSize": "11px", "color": "#aaa", "display": "block"}),
                    dcc.Dropdown(id="man-status", options=[
                        {"label": "✅ Success", "value": "success"},
                        {"label": "⚠️ Classifié OK", "value": "classified_ok"},
                        {"label": "🟡 XML invalide", "value": "xml_invalid"},
                        {"label": "❌ Échec", "value": "failed"},
                    ], value="success", clearable=False, style={"width": "130px", "fontSize": "11px"}),
                ], style={"flex": "1"}),
                html.Div([
                    html.Label("Modèle :", style={"fontSize": "11px", "color": "#aaa", "display": "block"}),
                    dcc.Input(id="man-model", type="text", placeholder="modèle utilisé",
                             value="qwen3.5:9b-hermes",
                             style={"width": "150px", "padding": "4px 6px", "fontSize": "11px", "background": "#111",
                                    "border": "1px solid #333", "color": "#4FC3F7", "borderRadius": "4px"}),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "8px"}),
            html.Div([
                html.Label("Prompt (optionnel) :", style={"fontSize": "11px", "color": "#aaa", "display": "block"}),
                dcc.Input(id="man-prompt", type="text", placeholder="Décris brièvement le test",
                         style={"width": "100%", "maxWidth": "500px", "padding": "4px 6px", "fontSize": "11px",
                                "background": "#111", "border": "1px solid #333", "color": "#ccc", "borderRadius": "4px"}),
            ], style={"marginBottom": "8px"}),
            html.Div([
                html.Label("XML généré (optionnel) :", style={"fontSize": "11px", "color": "#aaa", "display": "block"}),
                dcc.Textarea(id="man-xml", placeholder="<mxCell ... (optionnel)",
                            style={"width": "100%", "height": "50px", "fontSize": "10px",
                                   "background": "#111", "border": "1px solid #333", "color": "#81C784",
                                   "borderRadius": "4px", "fontFamily": "monospace"}),
            ], style={"marginBottom": "8px"}),
            html.Div([
                html.Button("💾 Enregistrer le test", id="btn-man-save", n_clicks=0,
                           style={"background": "#4CAF50", "color": "white", "border": "none",
                                  "padding": "6px 16px", "borderRadius": "4px", "cursor": "pointer",
                                  "fontSize": "12px", "fontWeight": "bold"}),
                html.Span(id="man-save-status", style={"fontSize": "11px", "color": "#aaa", "marginLeft": "12px"}),
                html.Span("💡 Test enregistré directement dans results.json — visible dans le tableau ci-dessous",
                         style={"fontSize": "10px", "color": "#666", "marginLeft": "12px", "fontStyle": "italic"}),
            ]),
        ], style={"padding": "8px 0"})
    else:
        badge = "🟢 AUTO"
        badge_style = {"background": "#5cb85c", "color": "white", "marginLeft": "12px",
                       "padding": "2px 10px", "borderRadius": "10px", "display": "inline-block",
                       "fontSize": "12px", "fontWeight": "bold"}
        btn_style = {"background": "#5cb85c", "color": "white", "border": "none",
                     "padding": "6px 12px", "borderRadius": "4px", "cursor": "pointer",
                     "fontSize": "12px", "fontWeight": "bold"}
        form = ""
        badge_style_inner = {"display": "none"}
    return new_mode, badge, btn_style, badge, badge_style, form, {"display": "block" if new_mode else "none",
                                                                    "padding": "12px 20px",
                                                                    "background": "#1a3a2a",
                                                                    "borderLeft": "4px solid #4CAF50"} if new_mode else {"display": "none"}


@callback(
    Output("man-save-status", "children"),
    Input("btn-man-save", "n_clicks"),
    [State("man-test-id", "value"), State("man-macro", "value"),
     State("man-status", "value"), State("man-model", "value"),
     State("man-prompt", "value"), State("man-xml", "value")],
    prevent_initial_call=True,
)
def save_manual_test(n, test_id, macro, status, model, prompt, xml):
    """Sauvegarde un test manuel directement (pas besoin de curl)"""
    try:
        result = {
            "test_id": test_id or f"man-{int(time.time())%100000}",
            "expected_macro": macro or "FORME",
            "status": status or "success",
            "model_name": model or "unknown",
            "prompt": prompt or "",
            "xml_generated": bool(xml and xml.strip()),
            "xml_valid": bool(xml and "<mxCell" in xml),
            "source": "manual",
            "timestamp": datetime.now().isoformat(),
            "timing_ms": {"total": 0},
            "classification": {"macro_class": macro or "FORME", "confidence": 1.0},
            "xml_cell_count": xml.count("mxCell") if xml else 0,
        }
        results = _load_results()
        results.append(result)
        _save_results(results)
        return f"✅ Enregistré — {len(results)} tests au total"
    except Exception as e:
        return f"❌ Erreur: {e}"


@callback(
    [Output("chart-success-rate", "figure"),
     Output("chart-trend", "figure"),
     Output("results-table", "children"),
     Output("last-update", "children"),
     Output("total-badge", "children"),
     Output("filter-count", "children"),
     Output("filter-model", "options")],
    [Input("auto-refresh", "n_intervals"),
     Input("btn-run-all", "n_clicks"),
     Input("btn-run-forme", "n_clicks"),
     Input("btn-run-tableau", "n_clicks"),
     Input("btn-run-kanban", "n_clicks"),
     Input("btn-run-agenda", "n_clicks"),
     Input("btn-run-gantt", "n_clicks"),
     Input("btn-run-texte", "n_clicks"),
     Input("confirm-reset", "submit_n_clicks"),
     Input("filter-source", "value"),
     Input("filter-macro", "value"),
     Input("filter-status", "value"),
     Input("filter-model", "value")],
    [State("paused", "data"), State("manual-mode", "data")],
)
def update_dashboard(n_int, n_all, n_forme, n_tableau, n_kanban, n_agenda, n_gantt, n_texte,
                     reset_confirm, f_source, f_macro, f_status, f_model, paused, manual):
    now = datetime.now().strftime("%H:%M:%S")
    triggered = ctx.triggered_id if ctx.triggered else None

    if paused and triggered == "auto-refresh":
        return (dash.no_update,) * 7

    # En mode AUTO, lancer les batchs de test
    if not manual:
        if triggered == "btn-run-all": _run_tests_bg()
        elif triggered == "btn-run-forme": _run_tests_bg("FORME")
        elif triggered == "btn-run-tableau": _run_tests_bg("TABLEAU")
        elif triggered == "btn-run-kanban": _run_tests_bg("KANBAN")
        elif triggered == "btn-run-agenda": _run_tests_bg("AGENDA")
        elif triggered == "btn-run-gantt": _run_tests_bg("GANTT")
        elif triggered == "btn-run-texte": _run_tests_bg("TEXTE")

    if triggered == "confirm-reset":
        _clear_results()

    stats = get_stats()
    total = stats.get("total_tests", 0)
    success = stats.get("success_count", 0)
    rate = stats.get("success_rate", 0)
    badge = f"📊 {total} tests — {rate}% succès" if total else "Aucun test"

    # ── Graphique succès ──
    macro_names = list(MACRO_COLORS.keys())
    rates_d, colors_d = [], []
    for m in macro_names:
        if m in stats.get("by_macro", {}) and stats["by_macro"][m]["total"] > 0:
            r = round(stats["by_macro"][m]["success"] / stats["by_macro"][m]["total"] * 100, 1)
        else:
            r = 0
        rates_d.append(r)
        colors_d.append(MACRO_COLORS.get(m, "#888"))

    fig_success = go.Figure([go.Bar(x=macro_names, y=rates_d, marker_color=colors_d,
                                     text=[f"{v}%" if v else chr(8212) for v in rates_d],
                                     textposition="outside", textfont={"color": "#ccc", "size": 11})])
    fig_success.update_layout(
        plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
        font={"color": "#ccc"}, margin=dict(l=10, r=10, t=4, b=20),
        yaxis=dict(range=[0, 110], gridcolor="#333", title="%", tickfont=dict(size=10)),
        xaxis=dict(gridcolor="#333", tickfont=dict(size=10)),
        showlegend=False,
    )

    # ── Graphique tendances ──
    recent = stats.get("recent", [])
    fig_trend = go.Figure()
    if len(recent) >= 3:
        for macro, color in MACRO_COLORS.items():
            mr = [r for r in reversed(recent) if r.get("expected_macro") == macro]
            if len(mr) >= 2:
                fig_trend.add_trace(go.Scatter(
                    x=[r.get("test_id", f"#{i}") for i, r in enumerate(mr)],
                    y=[r.get("timing_ms", {}).get("total", 0) / 1000 for r in mr],
                    mode="lines+markers", name=macro,
                    line=dict(color=color, width=2),
                    marker=dict(size=7, color=color),
                ))
        fig_trend.update_layout(
            plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
            font={"color": "#ccc"}, margin=dict(l=20, r=10, t=4, b=20),
            yaxis=dict(gridcolor="#333", title="Temps (s)", tickfont=dict(size=10)),
            xaxis=dict(gridcolor="#333", tickangle=-30, tickfont=dict(size=9)),
            hovermode="x unified", showlegend=True,
            legend=dict(font=dict(size=9), orientation="h", y=1.1),
        )
    else:
        fig_trend.add_annotation(
            text="Genere des tests pour voir les tendances",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#666"))
        fig_trend.update_layout(plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                                font={"color": "#ccc"}, margin=dict(l=10, r=10, t=4, b=20))

    # ── Tableau ──
    raw_results = stats.get("recent", [])

    all_models = sorted(set(r.get("model_name", "unknown") for r in raw_results))
    model_options = [{"label": "📦 Tous modeles", "value": ""}]
    for m in all_models:
        model_options.append({"label": f"🤖 {m}", "value": m})

    if f_source:
        raw_results = [r for r in raw_results if r.get("source", "auto") == f_source]
    if f_macro:
        raw_results = [r for r in raw_results if r.get("expected_macro", "") == f_macro]
    if f_status:
        raw_results = [r for r in raw_results if r.get("status", "") == f_status]
    if f_model:
        raw_results = [r for r in raw_results if r.get("model_name", "") == f_model]

    rows = []
    for idx, r in enumerate(raw_results, 1):
        macro = r.get("expected_macro", "?")
        s = r.get("status", "?")
        timing = r.get("timing_ms", {}).get("total", 0)
        prompt = r.get("prompt", "?")[:60]
        xml_ok = "✅" if r.get("xml_valid") else ("❌" if r.get("xml_generated") else chr(8212))
        src = "🤖 auto" if r.get("source") != "manual" else "🧑 manu"
        icon = {"success": "✅", "classified_ok": "⚠️", "xml_invalid": "🟡"}.get(s, "❌")
        mc = MACRO_COLORS.get(macro, "#888")

        row = html.Tr([
            html.Td(str(idx), style={"padding": "3px 4px", "fontSize": "10px", "color": "#555", "textAlign": "right"}),
            html.Td(r.get("test_id", ""), style={"padding": "3px 6px", "fontSize": "11px", "color": "#888"}),
            html.Td(macro, style={"padding": "3px 6px", "fontSize": "11px", "color": mc, "fontWeight": "bold"}),
            html.Td(prompt, style={"padding": "3px 6px", "fontSize": "11px", "maxWidth": "200px",
                                    "overflow": "hidden", "textOverflow": "ellipsis"}),
            html.Td(r.get("model_name", "?"), style={"padding": "3px 6px", "fontSize": "10px", "color": "#777"}),
            html.Td(src, style={"padding": "3px 6px", "fontSize": "11px", "color": "#888", "textAlign": "center"}),
            html.Td(f"{icon} {s}", style={"padding": "3px 6px", "fontSize": "11px"}),
            html.Td(xml_ok, style={"padding": "3px 6px", "fontSize": "11px", "textAlign": "center"}),
            html.Td(_c(timing), style={"padding": "3px 6px", "fontSize": "11px", "textAlign": "right", "color": "#aaa"}),
        ], style={"borderBottom": "1px solid #282a36"})
        rows.append(row)

    filter_info = f"({len(raw_results)} resultat{'s' if len(raw_results) != 1 else ''})"
    if rows:
        table = html.Table([
            html.Thead(html.Tr([
                html.Th("#", style={"padding": "4px 4px", "fontSize": "10px", "color": "#555", "textAlign": "right"}),
                html.Th("ID", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa"}),
                html.Th("Macro", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa"}),
                html.Th("Prompt", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa"}),
                html.Th("Modele", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa"}),
                html.Th("Source", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa", "textAlign": "center"}),
                html.Th("Status", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa"}),
                html.Th("XML", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa", "textAlign": "center"}),
                html.Th("Temps", style={"padding": "4px 6px", "fontSize": "11px", "color": "#aaa", "textAlign": "right"}),
            ])),
            html.Tbody(rows),
        ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "11px"})
    else:
        table = html.Div("Aucun resultat avec ces filtres",
                        style={"color": "#666", "fontSize": "13px", "textAlign": "center", "padding": "20px"})

    return fig_success, fig_trend, table, f"↻ {now}", badge, filter_info, model_options


if __name__ == "__main__":
    print(f"📊 {APP_TITLE} v2")
    print(f"   🌐 http://{LOCAL_IP}:8050")
    print(f"   🧠 ChromaDB: {len(patterns)} patterns")
    print(f"   API POST /api/result  (mode manuel)")
    print(f"   API GET  /api/chromadb")
    app.run(debug=False, host="0.0.0.0", port=8050)