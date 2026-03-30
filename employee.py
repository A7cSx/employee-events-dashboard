from .query_base import QueryBase


class Employee(QueryBase):
    """
    Provides SQL queries scoped to a single employee.

    Inherits shared database access (QueryMixin) and common queries
    (QueryBase.notes) and adds employee-specific query methods.
    """

    name = "employee"
    id_column = "employee_id"
    table = "employee"

    def names(self):
        """
        Return a DataFrame with employee_id and full name for every employee.
        Used to populate the employee dropdown in the dashboard.
        """
        sql = """
            SELECT
                employee_id,
                first_name || ' ' || last_name AS name
            FROM employee
            ORDER BY last_name, first_name
        """
        return self.query_return_df(sql)

    def username(self, entity_id: int) -> str:
        """
        Return the full name of a single employee by ID.
        Returns an empty string if no match is found.
        """
        sql = f"""
            SELECT first_name || ' ' || last_name AS name
            FROM employee
            WHERE employee_id = {entity_id}
        """
        result = self.query_return_list_of_tuples(sql)
        return result[0][0] if result else ""

    def event_counts(self, entity_id: int):
        """
        Return a DataFrame with cumulative positive and negative event
        counts over time for the specified employee.

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
            WHERE employee_id = {entity_id}
            ORDER BY event_date
        """
        return self.query_return_df(sql)

    def model_data(self, entity_id: int):
        """
        Return total positive and negative event counts for a single employee.
        This two-column DataFrame is fed directly into the ML model.

        Columns: positive_events, negative_events
        """
        sql = f"""
            SELECT
                SUM(positive_events) AS positive_events,
                SUM(negative_events) AS negative_events
            FROM employee_events
            WHERE employee_id = {entity_id}
        """
        return self.query_return_df(sql)
