from .query_base import QueryBase


class Team(QueryBase):
    """
    Provides SQL queries scoped to an entire team.

    Inherits shared database access (QueryMixin) and common notes query
    (QueryBase.notes) and adds team-specific query methods.
    """

    name = "team"
    id_column = "team_id"
    table = "team"

    def names(self):
        """
        Return a DataFrame with team_id and team_name for every team.
        Used to populate the team dropdown in the dashboard.
        """
        sql = """
            SELECT team_id, team_name AS name
            FROM team
            ORDER BY team_name
        """
        return self.query_return_df(sql)

    def username(self, entity_id: int) -> str:
        """
        Return the name of a single team by ID.
        Returns an empty string if no match is found.
        """
        sql = f"""
            SELECT team_name
            FROM team
            WHERE team_id = {entity_id}
        """
        result = self.query_return_list_of_tuples(sql)
        return result[0][0] if result else ""

    def event_counts(self, entity_id: int):
        """
        Return a DataFrame with cumulative positive and negative event
        counts over time for all members of the specified team combined.

        Columns: event_date, positive_events, negative_events
        """
        sql = f"""
            SELECT
                event_date,
                SUM(positive_events) OVER (
                    ORDER BY event_date ROWS UNBOUNDED PRECEDING
                ) AS positive_events,
                SUM(negative_events) OVER (
                    ORDER BY event_date ROWS UNBOUNDED PRECEDING
                ) AS negative_events
            FROM employee_events
            WHERE team_id = {entity_id}
            ORDER BY event_date
        """
        return self.query_return_df(sql)

    def model_data(self, entity_id: int):
        """
        Return the per-employee average of positive and negative events
        for the team. Averaging (rather than summing) normalises for
        team size, keeping the ML model input comparable to single-employee data.

        Columns: positive_events, negative_events
        """
        sql = f"""
            SELECT
                CAST(SUM(positive_events) AS REAL) / COUNT(DISTINCT employee_id) AS positive_events,
                CAST(SUM(negative_events) AS REAL) / COUNT(DISTINCT employee_id) AS negative_events
            FROM employee_events
            WHERE team_id = {entity_id}
        """
        return self.query_return_df(sql)
