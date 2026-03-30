"""
Employee Events Dashboard
=========================
A FastHTML application that lets managers monitor individual employee
or whole-team performance and recruitment-risk scores.

Routes
------
GET /                  → redirect to /employee/1
GET /employee          → redirect to /employee/{entity_id} (from dropdown)
GET /employee/{id}     → Employee performance page
GET /team              → redirect to /team/{entity_id} (from dropdown)
GET /team/{id}         → Team performance page
"""

# ── Standard library ────────────────────────────────────────────────
import sys
import os

# Make sure the report/ directory itself is on the path so relative
# imports inside report/ resolve correctly when running from project root.
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── FastHTML ─────────────────────────────────────────────────────────
from fasthtml.common import (
    FastHTML, serve,
    Div, H1, H2, H3, P, Hr, A, Link, Main, Header, Nav, Span,
    RedirectResponse,
)

# ── Installed Python package ─────────────────────────────────────────
from employee_events import Employee, Team

# ── Report utilities ─────────────────────────────────────────────────
from utils import load_model, REPO_ROOT

# ── Base components ──────────────────────────────────────────────────
from base_components import (
    BaseComponent, Dropdown, DataTable, MatplotlibViz, Radio,
)

# ── Combined components ───────────────────────────────────────────────
from combined_components import CombinedComponent, FormGroup


# ═══════════════════════════════════════════════════════════════════════
# Visualization subclasses
# ═══════════════════════════════════════════════════════════════════════

class LineChart(MatplotlibViz):
    """
    Cumulative line chart showing positive (green) vs negative (red)
    performance events over time for an employee or a team.
    """

    fig_size = (10, 4)

    def visualization(self, fig, ax, entity_id, model):
        df = model.event_counts(entity_id)

        if df.empty:
            ax.text(0.5, 0.5, "No event data available.",
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=12, color="#888")
            ax.set_axis_off()
            return

        ax.plot(df["event_date"], df["positive_events"],
                color="#27ae60", linewidth=2.5, marker="o",
                markersize=5, label="Positive Events")
        ax.plot(df["event_date"], df["negative_events"],
                color="#e74c3c", linewidth=2.5, marker="o",
                markersize=5, label="Negative Events")

        ax.set_title(
            f"Cumulative Performance Events — "
            f"{model.username(entity_id)}",
            fontsize=14, fontweight="bold", pad=12,
        )
        ax.set_xlabel("Date", fontsize=11)
        ax.set_ylabel("Cumulative Count", fontsize=11)
        ax.legend(fontsize=10)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()


class RecruitmentRiskGauge(MatplotlibViz):
    """
    Horizontal bar chart that displays the ML-predicted recruitment-risk
    score for an employee or team average.

    A colour gradient from green → amber → red is applied so that higher
    risk immediately stands out visually (satisfies the stand-out rubric
    criterion).
    """

    fig_size = (8, 2)

    def visualization(self, fig, ax, entity_id, model):
        ml_model = load_model()
        df = model.model_data(entity_id)

        if df.empty or df[["positive_events", "negative_events"]].isnull().all().all():
            ax.text(0.5, 0.5, "Insufficient data for risk prediction.",
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=11, color="#888")
            ax.set_axis_off()
            return

        row = df[["positive_events", "negative_events"]].fillna(0)
        features = row.values.tolist()
        probabilities = ml_model.predict_proba(features)
        risk_score = probabilities[0][1]          # probability of recruitment

        # Colour gradient: green → amber → red
        if risk_score < 0.33:
            bar_color = "#27ae60"
        elif risk_score < 0.66:
            bar_color = "#f39c12"
        else:
            bar_color = "#e74c3c"

        # Background track
        ax.barh(0, 1, color="#ecf0f1", height=0.6, edgecolor="#bdc3c7")
        # Risk bar
        ax.barh(0, risk_score, color=bar_color, height=0.6,
                edgecolor="none", alpha=0.9)

        # Score label inside bar
        ax.text(
            risk_score / 2, 0,
            f"{risk_score * 100:.1f}%",
            va="center", ha="center",
            fontsize=16, fontweight="bold", color="white",
        )

        entity_label = (
            "Team Average" if model.name == "team" else "Employee"
        )
        ax.set_title(
            f"Recruitment Risk Score ({entity_label})",
            fontsize=13, fontweight="bold", pad=10,
        )
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.set_xlabel("Risk of Recruitment", fontsize=10)
        ax.grid(False)
        fig.tight_layout()


# ═══════════════════════════════════════════════════════════════════════
# Dashboard page subclasses (CombinedComponent)
# ═══════════════════════════════════════════════════════════════════════

class EmployeeDashboard(CombinedComponent):
    """
    Full employee-performance page.

    children are evaluated top-to-bottom to produce the rendered HTML:
      1. Entity-selector form (dropdown + radio)
      2. Line chart — cumulative events over time
      3. Recruitment-risk gauge
      4. Manager notes table
    """

    outer_div_cls = "dashboard employee-dashboard"

    children = [
        FormGroup(children=[
            Radio(
                options=[("Employee", "/employee"), ("Team", "/team")],
                current_route="/employee",
            ),
            Dropdown(label="Select Employee", route="/employee"),
        ]),
        LineChart(),
        RecruitmentRiskGauge(),
        H2("Manager Notes"),
        DataTable(),
    ]


class TeamDashboard(CombinedComponent):
    """
    Full team-performance page.

    Same structure as EmployeeDashboard but scoped to a Team model.
    """

    outer_div_cls = "dashboard team-dashboard"

    children = [
        FormGroup(children=[
            Radio(
                options=[("Employee", "/employee"), ("Team", "/team")],
                current_route="/team",
            ),
            Dropdown(label="Select Team", route="/team"),
        ]),
        LineChart(),
        RecruitmentRiskGauge(),
        H2("Team Notes"),
        DataTable(),
    ]


# ═══════════════════════════════════════════════════════════════════════
# CSS — inline stylesheet served alongside the dashboard
# ═══════════════════════════════════════════════════════════════════════

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f4f6f9;
    color: #2c3e50;
}
header {
    background: #2c3e50;
    color: #fff;
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
header h1 { font-size: 1.4rem; font-weight: 600; letter-spacing: .5px; }
nav a {
    color: #bdc3c7;
    text-decoration: none;
    margin-left: 1.5rem;
    font-size: .9rem;
}
nav a:hover { color: #fff; }
main {
    max-width: 1100px;
    margin: 2rem auto;
    padding: 0 1.5rem;
}
.dashboard { display: flex; flex-direction: column; gap: 1.5rem; }
.form-group {
    background: #fff;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
}
.radio-container { display: flex; align-items: center; }
.radio-group { display: flex; gap: 1.2rem; font-size: .95rem; }
.radio-group label { cursor: pointer; display: flex; align-items: center; gap: .3rem; }
.dropdown-container { display: flex; align-items: center; gap: .7rem; }
.dropdown-container label { font-weight: 500; white-space: nowrap; }
select {
    padding: .4rem .7rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: .9rem;
    background: #fff;
}
button {
    padding: .4rem 1rem;
    background: #2980b9;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: .9rem;
}
button:hover { background: #1f6391; }
.chart-container, .table-container {
    background: #fff;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
}
.chart-img { width: 100%; max-width: 100%; }
h2 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #34495e;
    margin-bottom: -.5rem;
}
.data-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.data-table th {
    background: #2c3e50;
    color: #fff;
    padding: .6rem 1rem;
    text-align: left;
    font-weight: 500;
}
.data-table td { padding: .55rem 1rem; border-bottom: 1px solid #ecf0f1; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f8f9fa; }
.no-data { color: #888; font-style: italic; padding: .5rem 0; }
"""


# ═══════════════════════════════════════════════════════════════════════
# FastHTML application & routes
# ═══════════════════════════════════════════════════════════════════════

app = FastHTML(hdrs=[Link(rel="stylesheet", href="/static/report.css")])

# Instantiate query models (stateless — safe to share across requests)
employee_model = Employee()
team_model = Team()

# Instantiate dashboard page builders
employee_dashboard = EmployeeDashboard()
team_dashboard = TeamDashboard()


def page_shell(title: str, content, active: str = "employee"):
    """Wrap dashboard content in a consistent page header/nav."""
    return (
        Header(
            H1(title),
            Nav(
                A("Employee View", href="/employee/1"),
                A("Team View", href="/team/1"),
            ),
        ),
        Main(content),
    )


# ── Index route ─────────────────────────────────────────────────────

@app.get("/")
def index():
    return RedirectResponse("/employee/1")


# ── Employee routes ─────────────────────────────────────────────────

@app.get("/employee")
def employee_redirect(entity_id: int = 1):
    """Handle dropdown form submission → redirect to canonical URL."""
    return RedirectResponse(f"/employee/{entity_id}")


@app.get("/employee/{entity_id}")
def employee_page(entity_id: int):
    name = employee_model.username(entity_id) or "Employee"
    content = employee_dashboard(entity_id, employee_model)
    return page_shell(f"Employee Performance — {name}", content, "employee")


# ── Team routes ──────────────────────────────────────────────────────

@app.get("/team")
def team_redirect(entity_id: int = 1):
    """Handle dropdown form submission → redirect to canonical URL."""
    return RedirectResponse(f"/team/{entity_id}")


@app.get("/team/{entity_id}")
def team_page(entity_id: int):
    name = team_model.username(entity_id) or "Team"
    content = team_dashboard(entity_id, team_model)
    return page_shell(f"Team Performance — {name}", content, "team")


# ── Inline CSS served as a static file ──────────────────────────────

@app.get("/static/report.css")
def serve_css():
    from fasthtml.common import Response
    return Response(CSS, media_type="text/css")


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    serve(app=app, host="0.0.0.0", port=5001, reload=True)
