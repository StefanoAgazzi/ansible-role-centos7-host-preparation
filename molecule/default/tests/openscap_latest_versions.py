import sqlite3

conn = sqlite3.connect('primary.sqlite')

c = conn.cursor()

c.execute("""
SELECT t.name, MAX(t.version), t."release"
FROM packages t
WHERE t.name = "scap-workbench"
    OR t.name = "scap-security-guide"
    OR t.name = "openscap-daemon"
    OR t.name = "openscap"
    OR t.name = "scap-workbench"
GROUP BY t.name;
""")

print c.fetchall()

conn.close()
