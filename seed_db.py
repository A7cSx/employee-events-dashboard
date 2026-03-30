import sqlite3
from pathlib import Path

db = Path(r'C:\Users\Abdulrahman.alkhaldi\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\employee_events\employee_events.db')

conn = sqlite3.connect(db)
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS team (team_id INTEGER PRIMARY KEY, team_name TEXT, shift TEXT, manager_name TEXT);
CREATE TABLE IF NOT EXISTS employee (employee_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, team_id INTEGER);
CREATE TABLE IF NOT EXISTS employee_events (event_date TEXT, employee_id INTEGER, team_id INTEGER, positive_events INTEGER, negative_events INTEGER);
CREATE TABLE IF NOT EXISTS notes (employee_id INTEGER, team_id INTEGER, note TEXT, note_date TEXT, PRIMARY KEY (employee_id, team_id, note_date));
INSERT OR IGNORE INTO team VALUES (1, 'Alpha Team', 'Morning', 'Sarah Johnson');
INSERT OR IGNORE INTO team VALUES (2, 'Beta Team', 'Evening', 'Mark Williams');
INSERT OR IGNORE INTO employee VALUES (1, 'Ahmed', 'Al-Rashid', 1);
INSERT OR IGNORE INTO employee VALUES (2, 'Fatima', 'Al-Zahra', 1);
INSERT OR IGNORE INTO employee VALUES (3, 'Omar', 'Hassan', 2);
INSERT OR IGNORE INTO employee VALUES (4, 'Layla', 'Khalid', 2);
INSERT OR IGNORE INTO employee_events VALUES ('2024-01-15', 1, 1, 3, 1);
INSERT OR IGNORE INTO employee_events VALUES ('2024-02-10', 1, 1, 5, 0);
INSERT OR IGNORE INTO employee_events VALUES ('2024-03-05', 1, 1, 2, 2);
INSERT OR IGNORE INTO employee_events VALUES ('2024-01-20', 2, 1, 1, 3);
INSERT OR IGNORE INTO employee_events VALUES ('2024-02-15', 2, 1, 2, 4);
INSERT OR IGNORE INTO employee_events VALUES ('2024-01-12', 3, 2, 4, 0);
INSERT OR IGNORE INTO employee_events VALUES ('2024-02-08', 3, 2, 6, 1);
INSERT OR IGNORE INTO employee_events VALUES ('2024-01-25', 4, 2, 2, 3);
INSERT OR IGNORE INTO employee_events VALUES ('2024-02-20', 4, 2, 3, 2);
INSERT OR IGNORE INTO notes VALUES (1, 1, 'Excellent performance on Q1.', '2024-01-30');
INSERT OR IGNORE INTO notes VALUES (2, 1, 'Needs coaching on customer handling.', '2024-02-20');
INSERT OR IGNORE INTO notes VALUES (3, 2, 'Outstanding contributor.', '2024-02-12');
INSERT OR IGNORE INTO notes VALUES (4, 2, 'Performance plan initiated.', '2024-03-20');
""")

conn.commit()
conn.close()
print('Done!')
