from enum import IntEnum
from enum import unique


@unique
class Active(IntEnum):
    active = 0
    inactive = 1
    unknown = 2


CREATE_TABLE_SQLS = [
    """CREATE TABLE IF NOT EXISTS proxy (
id INTEGER PRIMARY KEY AUTOINCREMENT,
proxy TEXT NOT NULL UNIQUE,
active INT NOT NULL,
update_time DOUBLE NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS caller (
id INTEGER PRIMARY KEY AUTOINCREMENT,
caller TEXT NOT NULL UNIQUE)""",
    """CREATE TABLE IF NOT EXISTS status (
proxy_id INTEGER NOT NULL,
caller_id INTEGER NOT NULL,
available_time DOUBLE,
UNIQUE (proxy_id, caller_id),
FOREIGN KEY (proxy_id) REFERENCES proxy(id),
FOREIGN KEY (caller_id) REFERENCES caller(id))"""
]

INSERT_PROXY_SQL = """INSERT OR IGNORE INTO proxy (proxy, active, update_time) VALUES {}"""

INSERT_CALLER_SQL = """INSERT OR IGNORE INTO caller (caller) VALUES (?)"""

INSERT_STATUS_SQL = """INSERT OR IGNORE INTO status
(caller_id, proxy_id, available_time)
SELECT *, ? AS available_time FROM
(SELECT caller.id AS caller_id FROM caller WHERE caller = ?)
CROSS JOIN (SELECT proxy.id AS proxy_id FROM proxy WHERE proxy IN ({}));
"""

UPDATE_STATUS_SQL = """
UPDATE status SET available_time = ?
WHERE caller_id IN (SELECT caller.id AS caller_id FROM caller WHERE caller = ?)
AND proxy_id IN (SELECT proxy.id as proxy_id FROM proxy WHERE proxy in {})
"""

SELECT_PROXY_SQL = """
SELECT id, proxy FROM proxy
WHERE update_time < ? AND active = ?
ORDER BY update_time ASC LIMIT 16
"""

UPDATE_ACTIVE_SQL = """
UPDATE proxy SET active = ?, update_time = ? WHERE id IN ({})
"""

RANDOM_PICK_SQL = """
SELECT * FROM (
	SELECT proxy FROM proxy WHERE active = 0
	AND id NOT IN (
		SELECT proxy_id FROM status WHERE caller_id IN (
			SELECT id AS caller_id FROM caller WHERE caller = ?
		) AND available_time > ?
	)
)
ORDER BY RANDOM() LIMIT ?;
"""

QUERY_PROXY_STATUS_SQL = """
SELECT count(id), active FROM proxy GROUP BY active
"""

RESET_PROXY_SQLS = [
    """DELETE FROM status WHERE proxy_id IN (SELECT id FROM proxy WHERE active = ?);""",
    """DELETE FROM proxy WHERE active = ?;"""
]
