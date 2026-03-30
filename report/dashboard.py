import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fasthtml.common import (
    FastHTML, serve, Div, H1, H2, H3, P, Main, Header,
    Table, Thead, Tbody, Tr, Th, Td, Nav, A, Style,
    RedirectResponse, Select, Option, Form, Button, Label, Span
)
from employee_events import Employee, Team

CSS = """
body { font-family: Segoe UI, sans-serif; background: #f0f2f5; margin: 0; }
header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
header h1 { font-size: 1.3rem; margin: 0; }
nav a { color: #aaa; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
nav a:hover { color: white; }
main { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; display: flex; flex-direction: column; gap: 1.5rem; }
.card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.card h2 { margin: 0 0 1rem 0; font-size: 1.1rem; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.5rem; }
.form-row { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.form-row label { font-weight: 600; font-size: 0.9rem; }
select { padding: 0.4rem 0.8rem; border: 1px solid #ccc; border-radius: 6px; font-size: 0.9rem; }
button { padding: 0.4rem 1.2rem; background: #1a1a2e; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
button:hover { background: #16213e; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
thead tr { background: #1a1a2e; color: white; }
th { padding: 0.6rem 1rem; text-align: left; font-weight: 500; }
td { padding: 0.55rem 1rem; border-bottom: 1px solid #f0f0f0; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f8f9fa; }
.stats { display: flex; gap: 1rem; flex-wrap: wrap; }
.stat-box { flex: 1; min-width: 140px; background: #f8f9fa; border-radius: 8px; padding: 1rem; text-align: center; border-left: 4px solid #1a1a2e; }
.stat-box .value { font-size: 2rem; font-weight: 700; color: #1a1a2e; }
.stat-box .label { font-size: 0.8rem; color: #666; margin-top: 0.3rem; }
.positive { border-left-color: #27ae60 !important; }
.positive .value { color: #27ae60 !important; }
.negative { border-left-color: #e74c3c !important; }
.negative .value { color: #e74c3c !important; }
.risk-bar-container { background: #eee; border-radius: 20px; height: 30px; overflow: hidden; margin: 0.5rem 0; }
.risk-bar { height: 100%; border-radius: 20px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.9rem; transition: width 0.3s; }
.risk-low { background: #27ae60; }
.risk-medium { background: #f39c12; }
.risk-high { background: #e74c3c; }
.no-data { color: #888; font-style: italic; }
"""

app = FastHTML(hdrs=[Style(CSS)])
rt = app.route

employee_model = Employee()
team_model = Team()

def risk_score(model, entity_id):
    import math
    df = model.model_data(entity_id)
    if df.empty: return 0.0
    pos = df['positive_events'].iloc[0] or 0
    neg = df['negative_events'].iloc[0] or 0
    total = pos + neg if (pos + neg) > 0 else 1
    neg_ratio = neg / total
    return round(1 / (1 + math.exp(-5 * (neg_ratio - 0.4))), 3)

def risk_bar(score):
    pct = int(score * 100)
    cls = 'risk-low' if score < 0.33 else ('risk-medium' if score < 0.66 else 'risk-high')
    return Div(
        Div(f'{pct}%', cls=f'risk-bar {cls}', style=f'width:{pct}%'),
        cls='risk-bar-container'
    )

def events_table(df):
    if df.empty: return P('No event data available.', cls='no-data')
    rows = [Tr(Td(r['event_date']), Td(str(r['positive_events'])), Td(str(r['negative_events']))) for _, r in df.iterrows()]
    return Table(
        Thead(Tr(Th('Date'), Th('Cumulative Positive'), Th('Cumulative Negative'))),
        Tbody(*rows)
    )

def notes_table(df):
    if df.empty: return P('No notes on record.', cls='no-data')
    rows = [Tr(Td(r['note_date']), Td(r['note'])) for _, r in df.iterrows()]
    return Table(
        Thead(Tr(Th('Date'), Th('Note'))),
        Tbody(*rows)
    )

def summary_stats(df):
    if df.empty: return P('No data.', cls='no-data')
    pos = int(df['positive_events'].max() or 0)
    neg = int(df['negative_events'].max() or 0)
    return Div(
        Div(Div(str(pos), cls='value'), Div('Total Positive Events', cls='label'), cls='stat-box positive'),
        Div(Div(str(neg), cls='value'), Div('Total Negative Events', cls='label'), cls='stat-box negative'),
        cls='stats'
    )

def selector_form(model, current_id, route):
    df = model.names()
    id_col = model.id_column
    opts = [Option(r['name'], value=str(r[id_col]), selected=(str(r[id_col]) == str(current_id))) for _, r in df.iterrows()]
    return Div(
        Form(
            Div(
                Label('View: '),
                A('Employee', href='/employee/1', style='margin-right:1rem;'),
                A('Team', href='/team/1'),
                style='margin-right: 2rem;'
            ),
            Div(
                Label('Select: '),
                Select(*opts, name='entity_id'),
                Button('Go', type='submit'),
                style='display:flex; gap:0.5rem; align-items:center;'
            ),
            method='get', action=f'/{route}',
            style='display:flex; align-items:center; flex-wrap:wrap; gap:1rem;'
        ),
        cls='card'
    )

@rt('/')
def get():
    return RedirectResponse('/employee/1')

@rt('/employee')
def get(entity_id: int = 1):
    return RedirectResponse(f'/employee/{entity_id}')

@rt('/employee/{entity_id}')
def get(entity_id: int):
    name = employee_model.username(entity_id)
    df = employee_model.event_counts(entity_id)
    notes = employee_model.notes(entity_id)
    score = risk_score(employee_model, entity_id)
    return (
        Style(CSS),
        Header(H1(f'Employee Performance — {name}'), Nav(A('Employee', href='/employee/1'), A('Team', href='/team/1'))),
        Main(
            selector_form(employee_model, entity_id, 'employee'),
            Div(H2('Performance Summary'), summary_stats(df), cls='card'),
            Div(H2(f'Recruitment Risk Score: {int(score*100)}%'), risk_bar(score), cls='card'),
            Div(H2('Cumulative Event History'), events_table(df), cls='card'),
            Div(H2('Manager Notes'), notes_table(notes), cls='card'),
        )
    )

@rt('/team')
def get(entity_id: int = 1):
    return RedirectResponse(f'/team/{entity_id}')

@rt('/team/{entity_id}')
def get(entity_id: int):
    name = team_model.username(entity_id)
    df = team_model.event_counts(entity_id)
    notes = team_model.notes(entity_id)
    score = risk_score(team_model, entity_id)
    return (
        Style(CSS),
        Header(H1(f'Team Performance — {name}'), Nav(A('Employee', href='/employee/1'), A('Team', href='/team/1'))),
        Main(
            selector_form(team_model, entity_id, 'team'),
            Div(H2('Performance Summary'), summary_stats(df), cls='card'),
            Div(H2(f'Average Recruitment Risk Score: {int(score*100)}%'), risk_bar(score), cls='card'),
            Div(H2('Cumulative Event History'), events_table(df), cls='card'),
            Div(H2('Team Notes'), notes_table(notes), cls='card'),
        )
    )

serve()
