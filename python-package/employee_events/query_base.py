from .sql_execution import QueryMixin

class QueryBase(QueryMixin):
    name = ''
    id_column = ''
    table = ''

    def notes(self, entity_id):
        sql = f'SELECT note_date, note FROM notes WHERE {self.id_column} = {entity_id} ORDER BY note_date DESC'
        return self.query_return_df(sql)
