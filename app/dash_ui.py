from __future__ import annotations
from dash import Dash, html, dcc, Input, Output, State
from .storage.memory_store import MemoryStore

def build_dash_app(store: MemoryStore):
    app = Dash(__name__)
    app.layout = html.Div([
        html.H2("Assistant Dashboard"),
        dcc.Tabs(id="tabs", value="notes", children=[
            dcc.Tab(label="Notes", value="notes"),
            dcc.Tab(label="Tasks", value="tasks"),
        ]),
        html.Div(id="tab-content"),
    ])

    @app.callback(Output("tab-content","children"), [Input("tabs","value")])
    def render_tab(tab):
        if tab == "notes":
            notes = store.list_notes()
            return html.Ul([html.Li(f"{n.title} — {', '.join(n.tags)}") for n in notes])
        else:
            tasks = store.list_tasks()
            return html.Ul([html.Li(f"{t.title} [{t.status}]") for t in tasks])
    return app
