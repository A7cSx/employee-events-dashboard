from .query_base import QueryBase

class Team(QueryBase):
    name = 'team'
    id_column = 'team_id'
    table = 'team'

    def names(self):
        return self.query_return_df("SELECT team_id, team_name AS name FROM team ORDER BY team_name")

    def username(self, entity_id):
        result = self.query_return_list_of_tuples(f"SELECT team_name FROM team WHERE team_id = {entity_id}")
        return result[0][0] if result else ''

    def event_counts(self, entity_id):
        sql = f'''SELECT event_date,
            SUM(positive_events) OVER (ORDER BY event_date ROWS UNBOUNDED PRECEDING) AS positive_events,
            SUM(negative_events) OVER (ORDER BY event_date ROWS UNBOUNDED PRECEDING) AS negative_events
            FROM employee_events WHERE team_id = {entity_id} ORDER BY event_date'''
        return self.query_return_df(sql)

    def model_data(self, entity_id):
        return self.query_return_df(f"SELECT CAST(SUM(positive_events) AS REAL) / COUNT(DISTINCT employee_id) AS positive_events, CAST(SUM(negative_events) AS REAL) / COUNT(DISTINCT employee_id) AS negative_events FROM employee_events WHERE team_id = {entity_id}")
