"""
📊 Smart MCP Pipeline — Tableau de Bord
Simplifié, parlant, avec GANTT et support tests manuels.
Mode AUTO → lance des tests automatiques
Mode MANUEL → enregistre les tests venant de Hermes WebUI
"""
import json, os, sys, threading, time
from datetime import datetime
from pathlib import Path

import dash, plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, callback, ctx
from flask import Flask, request, jsonify

sys.path.insert(0, str(Path(__file__).parent))
from test_runner import get_stats, run_batch, _save_results, _load_results, RESULTS_FILE

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

# ── Helpers ──────────────────────────────────────────

def _c(s):
    if s >= 1000:
        return f"{s/1000:.1f}s"
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


# ── API Flask pour tests manuels ──────────────────────

server = Flask(__name__)

@server.route("/api/result", methods=["POST"])
def api_add_result():
    """Reçoit un résultat de test manuel depuis Hermes WebUI"""
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


# ── Dash app ──────────────────────────────────────────

app = dash.Dash(__name__, title=APP_TITLE, server=server)
app.layout = html.Div([

    # Header
    html.Div([
        html.H1(APP_TITLE, style={"margin": "0", "fontSize": "20px"}),
        html.Span(id="mode-badge", style={"marginLeft": "12px", "padding": "2px 10px",
                                           "borderRadius": "10px", "display": "inline-block",
                                           "fontSize": "12px", "fontWeight": "bold"}),
        html.Span(id="total-badge", style={"fontSize": "13px", "color": "#aaa", "marginLeft": "15px"}),
        html.Span(id="last-update", style={"fontSize": "12px", "color": "#666", "marginLeft": "auto"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "12px 20px",
              "background": "#1a1a2e", "color": "white", "borderRadius": "8px 8px 0 0"}),

    # Controls bar
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

    # Mode Manuel : instructions
    html.Div(id="manual-instructions", style={"display": "none", "padding": "8px 20px",
                                               "background": "#1a3a2a",
                                               "borderLeft": "4px solid #4CAF50",
                                               "fontSize": "12px", "color": "#aaa"}),

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


# ── Callbacks ────────────────────────────────────────

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
     Output("manual-instructions", "children"),
     Output("manual-instructions", "style")],
    Input("btn-mode", "n_clicks"),
    State("manual-mode", "data"),
    prevent_initial_call=True,
)
def toggle_mode(n, mode):
    new_mode = not mode
    if new_mode:
        badge_text = "🔴 MANUEL"
        badge_style = {"background": "#d9534f", "color": "white", "marginLeft": "12px",
                       "padding": "2px 10px", "borderRadius": "10px", "display": "inline-block",
                       "fontSize": "12px", "fontWeight": "bold"}
        btn_style = {"background": "#d9534f", "color": "white", "border": "none",
                     "padding": "6px 12px", "borderRadius": "4px", "cursor": "pointer",
                     "fontSize": "12px", "fontWeight": "bold"}
        instructions = html.Div([
            html.Strong("📋 Mode Manuel activé"),
            html.Br(), html.Br(),
            "Les tests automatiques sont désactivés. Pour enregistrer un test depuis Hermes WebUI :",
            html.Pre("""curl -X POST http://192.168.1.100:8050/api/result \\
  -H "Content-Type: application/json" \\
  -d '{
    "test_id": "man-01",
    "prompt": "dessine un carre rouge",
    "expected_macro": "FORME",
    "status": "success",
    "model_name": "qwen3.5:9b-hermes",
    "model_params": {"max_tokens": 16384, "temperature": 0.3},
    "classification": {"macro_class": "FORME", "confidence": 0.95},
    "xml_generated": true,
    "xml_valid": true,
    "xml_cell_count": 5,
    "timing_ms": {"total": 5000}
}'""", style={"background": "#111", "padding": "8px", "borderRadius": "4px",
                    "fontSize": "11px", "overflowX": "auto", "color": "#4FC3F7"}),
        ])
        show_instructions = {"display": "block", "padding": "8px 20px", "background": "#1a3a2a",
                             "borderLeft": "4px solid #4CAF50", "fontSize": "12px", "color": "#aaa"}
    else:
        badge_text = "🟢 AUTO"
        badge_style = {"background": "#5cb85c", "color": "white", "marginLeft": "12px",
                       "padding": "2px 10px", "borderRadius": "10px", "display": "inline-block",
                       "fontSize": "12px", "fontWeight": "bold"}
        btn_style = {"background": "#5cb85c", "color": "white", "border": "none",
                     "padding": "6px 12px", "borderRadius": "4px", "cursor": "pointer",
                     "fontSize": "12px", "fontWeight": "bold"}
        instructions = ""
        show_instructions = {"display": "none"}
    return new_mode, badge_text, btn_style, badge_text, badge_style, instructions, show_instructions


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

    # En mode MANUEL, ignorer les boutons de test auto
    if not manual:
        if triggered == "btn-run-all":
            _run_tests_bg()
        elif triggered == "btn-run-forme":
            _run_tests_bg("FORME")
        elif triggered == "btn-run-tableau":
            _run_tests_bg("TABLEAU")
        elif triggered == "btn-run-kanban":
            _run_tests_bg("KANBAN")
        elif triggered == "btn-run-agenda":
            _run_tests_bg("AGENDA")
        elif triggered == "btn-run-gantt":
            _run_tests_bg("GANTT")
        elif triggered == "btn-run-texte":
            _run_tests_bg("TEXTE")

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

    # Options du filtre modèle
    all_models = sorted(set(r.get("model_name", "unknown") for r in raw_results))
    model_options = [{"label": "📦 Tous modeles", "value": ""}]
    for m in all_models:
        model_options.append({"label": f"🤖 {m}", "value": m})

    # Appliquer les filtres
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
    print(f"📊 {APP_TITLE}")
    print(f"   http://127.0.0.1:8050")
    print(f"   API POST /api/result  (mode manuel)")
    print(f"   API GET  /api/results")
    print(f"   API GET  /api/stats")
    app.run(debug=False, host="0.0.0.0", port=8050)
