from .query_base import QueryBase

class Employee(QueryBase):
    name = 'employee'
    id_column = 'employee_id'
    table = 'employee'

    def names(self):
        return self.query_return_df("SELECT employee_id, first_name || ' ' || last_name AS name FROM employee ORDER BY last_name")

    def username(self, entity_id):
        result = self.query_return_list_of_tuples(f"SELECT first_name || ' ' || last_name FROM employee WHERE employee_id = {entity_id}")
        return result[0][0] if result else ''

    def event_counts(self, entity_id):
        sql = f'''SELECT event_date,
            SUM(positive_events) OVER (ORDER BY event_date ROWS UNBOUNDED PRECEDING) AS positive_events,
            SUM(negative_events) OVER (ORDER BY event_date ROWS UNBOUNDED PRECEDING) AS negative_events
            FROM employee_events WHERE employee_id = {entity_id} ORDER BY event_date'''
        return self.query_return_df(sql)

    def model_data(self, entity_id):
        return self.query_return_df(f"SELECT SUM(positive_events) AS positive_events, SUM(negative_events) AS negative_events FROM employee_events WHERE employee_id = {entity_id}")
