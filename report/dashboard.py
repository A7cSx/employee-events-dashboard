import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fasthtml.common import FastHTML, serve, Div, H1, H2, P, Main, Header, RedirectResponse
from employee_events import Employee, Team

app = FastHTML()
rt = app.route

employee_model = Employee()
team_model = Team()

@rt("/")
def get():
    return RedirectResponse("/employee/1")

@rt("/employee")
def get(entity_id: int = 1):
    return RedirectResponse(f"/employee/{entity_id}")

@rt("/employee/{entity_id}")
def get(entity_id: int):
    name = employee_model.username(entity_id)
    df = employee_model.event_counts(entity_id)
    notes = employee_model.notes(entity_id)
    return Header(H1(f"Employee Performance - {name}")), Main(H2("Event Counts"), P(str(df.to_dict())), H2("Notes"), P(str(notes.to_dict())))

@rt("/team/{entity_id}")
def get(entity_id: int):
    name = team_model.username(entity_id)
    df = team_model.event_counts(entity_id)
    return Header(H1(f"Team Performance - {name}")), Main(H2("Event Counts"), P(str(df.to_dict())))

serve()
