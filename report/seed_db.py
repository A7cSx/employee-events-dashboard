import sqlite3
from pathlib import Path

db = Path('python-package/employee_events/employee_events.db')
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute('DELETE FROM notes')
c.execute('DELETE FROM employee_events')
c.execute('DELETE FROM employee')
c.execute('DELETE FROM team')

c.execute("INSERT INTO team VALUES (1, 'Alpha Team', 'Morning', 'Sarah Johnson')")
c.execute("INSERT INTO team VALUES (2, 'Beta Team', 'Evening', 'Mark Williams')")

c.execute("INSERT INTO employee VALUES (1, 'Ahmed', 'Al-Rashid', 1)")
c.execute("INSERT INTO employee VALUES (2, 'Fatima', 'Al-Zahra', 1)")
c.execute("INSERT INTO employee VALUES (3, 'Omar', 'Hassan', 2)")
c.execute("INSERT INTO employee VALUES (4, 'Layla', 'Khalid', 2)")

c.execute("INSERT INTO employee_events VALUES ('2024-01-15', 1, 1, 3, 1)")
c.execute("INSERT INTO employee_events VALUES ('2024-02-10', 1, 1, 5, 0)")
c.execute("INSERT INTO employee_events VALUES ('2024-03-05', 1, 1, 2, 2)")
c.execute("INSERT INTO employee_events VALUES ('2024-01-20', 2, 1, 1, 3)")
c.execute("INSERT INTO employee_events VALUES ('2024-02-15', 2, 1, 2, 4)")
c.execute("INSERT INTO employee_events VALUES ('2024-01-12', 3, 2, 4, 0)")
c.execute("INSERT INTO employee_events VALUES ('2024-02-08', 3, 2, 6, 1)")
c.execute("INSERT INTO employee_events VALUES ('2024-01-25', 4, 2, 2, 3)")
c.execute("INSERT INTO employee_events VALUES ('2024-02-20', 4, 2, 3, 2)")

c.execute("INSERT INTO notes VALUES (1, 1, 'Excellent performance on Q1.', '2024-01-30')")
c.execute("INSERT INTO notes VALUES (2, 1, 'Needs coaching on customer handling.', '2024-02-20')")
c.execute("INSERT INTO notes VALUES (3, 2, 'Outstanding contributor.', '2024-02-12')")
c.execute("INSERT INTO notes VALUES (4, 2, 'Performance plan initiated.', '2024-03-20')")

conn.commit()
conn.close()
print('Done!')
