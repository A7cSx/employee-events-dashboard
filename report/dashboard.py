import sys, os, io, base64, math
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fasthtml.common import (
    FastHTML, serve, Div, H1, H2, P, Main, Header,
    Table, Thead, Tbody, Tr, Th, Td, Nav, A, Style,
    RedirectResponse, Select, Option, Form, Button, Label, Img
)
from employee_events import Employee, Team

CSS = """
body{font-family:Segoe UI,sans-serif;background:#f0f2f5;margin:0;}
header{background:#1a1a2e;color:white;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;}
header h1{font-size:1.3rem;margin:0;}
nav a{color:#aaa;text-decoration:none;margin-left:1.5rem;font-size:.9rem;}
nav a:hover{color:white;}
main{max-width:1000px;margin:2rem auto;padding:0 1rem;display:flex;flex-direction:column;gap:1.5rem;}
.card{background:white;border-radius:10px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08);}
.card h2{margin:0 0 1rem 0;font-size:1.1rem;color:#333;border-bottom:2px solid #f0f0f0;padding-bottom:.5rem;}
select{padding:.4rem .8rem;border:1px solid #ccc;border-radius:6px;font-size:.9rem;}
button{padding:.4rem 1.2rem;background:#1a1a2e;color:white;border:none;border-radius:6px;cursor:pointer;}
table{width:100%;border-collapse:collapse;font-size:.9rem;}
thead tr{background:#1a1a2e;color:white;}
th{padding:.6rem 1rem;text-align:left;}
td{padding:.55rem 1rem;border-bottom:1px solid #f0f0f0;}
tr:hover td{background:#f8f9fa;}
.stats{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;}
.stat-box{flex:1;min-width:140px;background:#f8f9fa;border-radius:8px;padding:1rem;text-align:center;border-left:4px solid #1a1a2e;}
.stat-box .value{font-size:2rem;font-weight:700;color:#1a1a2e;}
.stat-box .label{font-size:.8rem;color:#666;margin-top:.3rem;}
.positive{border-left-color:#27ae60!important;}.positive .value{color:#27ae60!important;}
.negative{border-left-color:#e74c3c!important;}.negative .value{color:#e74c3c!important;}
.risk-bar-wrap{background:#eee;border-radius:20px;height:30px;overflow:hidden;margin:.5rem 0;}
.risk-bar{height:100%;border-radius:20px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;}
.risk-low{background:#27ae60;}.risk-med{background:#f39c12;}.risk-high{background:#e74c3c;}
img{max-width:100%;border-radius:8px;}
.form-row{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;}
.no-data{color:#888;font-style:italic;}
"""

app = FastHTML(hdrs=[Style(CSS)])
rt = app.route
employee_model = Employee()
team_model = Team()

def make_chart(df):
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(df["event_date"], df["positive_events"], color="#27ae60", marker="o", linewidth=2, label="Positive")
    ax.plot(df["event_date"], df["negative_events"], color="#e74c3c", marker="o", linewidth=2, label="Negative")
    ax.set_title("Cumulative Performance Events Over Time", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Cumulative Count")
    ax.legend(); ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.xticks(rotation=30, ha="right"); plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def make_risk_chart(score, label):
    fig, ax = plt.subplots(figsize=(9, 1.8))
    color = "#27ae60" if score < 0.33 else ("#f39c12" if score < 0.66 else "#e74c3c")
    ax.barh(0, 1, color="#eeeeee", height=0.5)
    ax.barh(0, score, color=color, height=0.5)
    ax.text(score/2, 0, f"{int(score*100)}%", va="center", ha="center", color="white", fontweight="bold", fontsize=14)
    ax.set_xlim(0,1); ax.set_yticks([]); ax.set_xticks([0,.25,.5,.75,1])
    ax.set_xticklabels(["0%","25%","50%","75%","100%"])
    ax.set_title(f"Recruitment Risk — {label}", fontsize=12, fontweight="bold")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def get_risk(model, entity_id):
    df = model.model_data(entity_id)
    if df.empty: return 0.0
    pos = float(df["positive_events"].iloc[0] or 0)
    neg = float(df["negative_events"].iloc[0] or 0)
    total = pos + neg if (pos+neg) > 0 else 1
    return round(1/(1+math.exp(-5*(neg/total - 0.4))), 3)

def notes_table(df):
    if df.empty: return P("No notes on record.", cls="no-data")
    rows = [Tr(Td(r["note_date"]), Td(r["note"])) for _,r in df.iterrows()]
    return Table(Thead(Tr(Th("Date"),Th("Note"))), Tbody(*rows))

def events_table(df):
    if df.empty: return P("No event data.", cls="no-data")
    rows = [Tr(Td(r["event_date"]), Td(str(int(r["positive_events"]))), Td(str(int(r["negative_events"])))) for _,r in df.iterrows()]
    return Table(Thead(Tr(Th("Date"),Th("Cumulative Positive"),Th("Cumulative Negative"))), Tbody(*rows))

def selector(model, current_id, route):
    df = model.names(); id_col = model.id_column
    opts = [Option(r["name"], value=str(r[id_col]), selected=(str(r[id_col])==str(current_id))) for _,r in df.iterrows()]
    return Div(Form(
        Label("Switch view: "), A("Employee",href="/employee/1"), " | ", A("Team",href="/team/1"),
        Label(" — Select: ", style="margin-left:1.5rem;"),
        Select(*opts, name="entity_id"),
        Button("Go", type="submit"),
        method="get", action=f"/{route}", style="display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;"
    ), cls="card")

def stat_boxes(df):
    if df.empty: return P("No data.", cls="no-data")
    pos = int(df["positive_events"].max() or 0)
    neg = int(df["negative_events"].max() or 0)
    return Div(
        Div(Div(str(pos),cls="value"),Div("Total Positive Events",cls="label"),cls="stat-box positive"),
        Div(Div(str(neg),cls="value"),Div("Total Negative Events",cls="label"),cls="stat-box negative"),
        cls="stats"
    )

@rt("/")
def get(): return RedirectResponse("/employee/1")

@rt("/employee")
def get(entity_id: int = 1): return RedirectResponse(f"/employee/{entity_id}")

@rt("/employee/{entity_id}")
def get(entity_id: int):
    name = employee_model.username(entity_id)
    df = employee_model.event_counts(entity_id)
    notes = employee_model.notes(entity_id)
    score = get_risk(employee_model, entity_id)
    chart_b64 = make_chart(df)
    risk_b64 = make_risk_chart(score, name)
    return (
        Header(H1(f"Employee Performance — {name}"), Nav(A("Employee",href="/employee/1"),A("Team",href="/team/1"))),
        Main(
            selector(employee_model, entity_id, "employee"),
            Div(H2("Performance Summary"), stat_boxes(df), cls="card"),
            Div(H2("Recruitment Risk Score"), Img(src=f"data:image/png;base64,{risk_b64}") if risk_b64 else P("No data."), cls="card"),
            Div(H2("Cumulative Event History — Chart"), Img(src=f"data:image/png;base64,{chart_b64}") if chart_b64 else P("No data."), cls="card"),
            Div(H2("Event History — Table"), events_table(df), cls="card"),
            Div(H2("Manager Notes"), notes_table(notes), cls="card"),
        )
    )

@rt("/team")
def get(entity_id: int = 1): return RedirectResponse(f"/team/{entity_id}")

@rt("/team/{entity_id}")
def get(entity_id: int):
    name = team_model.username(entity_id)
    df = team_model.event_counts(entity_id)
    notes = team_model.notes(entity_id)
    score = get_risk(team_model, entity_id)
    chart_b64 = make_chart(df)
    risk_b64 = make_risk_chart(score, name)
    return (
        Header(H1(f"Team Performance — {name}"), Nav(A("Employee",href="/employee/1"),A("Team",href="/team/1"))),
        Main(
            selector(team_model, entity_id, "team"),
            Div(H2("Performance Summary"), stat_boxes(df), cls="card"),
            Div(H2("Average Recruitment Risk Score"), Img(src=f"data:image/png;base64,{risk_b64}") if risk_b64 else P("No data."), cls="card"),
            Div(H2("Cumulative Event History — Chart"), Img(src=f"data:image/png;base64,{chart_b64}") if chart_b64 else P("No data."), cls="card"),
            Div(H2("Event History — Table"), events_table(df), cls="card"),
            Div(H2("Team Notes"), notes_table(notes), cls="card"),
        )
    )

serve()
