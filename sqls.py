from enum import IntEnum
from enum import unique


@unique
class Active(IntEnum):
    active = 0
    inactive = 1
    unknown = 2


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS proxy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy TEXT NOT NULL UNIQUE,
    active INT NOT NULL,
    update_time DOUBLE NOT NULL
)
"""

INSERT_PROXY_SQL = """
INSERT OR IGNORE INTO proxy (proxy, active, update_time)
VALUES {}
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
SELECT id, proxy FROM proxy WHERE active = 0 ORDER BY RANDOM() LIMIT ?;
"""
