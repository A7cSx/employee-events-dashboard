from .sql_execution import QueryMixin


class QueryBase(QueryMixin):
    """
    Base class for building SQL queries against the employee_events database.

    Subclasses (Employee, Team) inherit the QueryMixin for database access
    and override methods specific to their entity type.

    Class attributes set by subclasses:
        name        - human-readable entity name ("employee" or "team")
        id_column   - primary key column name used in WHERE clauses
        table       - the main table name for this entity
    """

    name = ""
    id_column = ""
    table = ""

    # ------------------------------------------------------------------
    # Methods to be overridden by subclasses
    # ------------------------------------------------------------------

    def names(self) -> "pd.DataFrame":
        """
        Return a DataFrame of all entity IDs and display names.
        Used to populate dropdown menus in the dashboard.
        Must be implemented by each subclass.
        """
        raise NotImplementedError(
            f"Subclass '{type(self).__name__}' must implement names()"
        )

    def username(self, entity_id: int) -> str:
        """
        Return the display name for a single entity.
        Must be implemented by each subclass.
        """
        raise NotImplementedError(
            f"Subclass '{type(self).__name__}' must implement username()"
        )

    def event_counts(self, entity_id: int) -> "pd.DataFrame":
        """
        Return cumulative positive and negative event counts over time
        for the given entity. Must be implemented by each subclass.
        """
        raise NotImplementedError(
            f"Subclass '{type(self).__name__}' must implement event_counts()"
        )

    def model_data(self, entity_id: int) -> "pd.DataFrame":
        """
        Return aggregated feature data used as input to the ML model.
        Must be implemented by each subclass.
        """
        raise NotImplementedError(
            f"Subclass '{type(self).__name__}' must implement model_data()"
        )

    # ------------------------------------------------------------------
    # Shared queries (usable by both Employee and Team)
    # ------------------------------------------------------------------

    def notes(self, entity_id: int) -> "pd.DataFrame":
        """
        Return manager notes for the given entity, ordered newest first.
        Both employees and teams share the same notes table structure,
        so this query lives in the base class.
        """
        sql = f"""
            SELECT note_date, note
            FROM notes
            WHERE {self.id_column} = {entity_id}
            ORDER BY note_date DESC
        """
        return self.query_return_df(sql)
