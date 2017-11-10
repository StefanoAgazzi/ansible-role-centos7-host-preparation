import sqlite3
import requests
import ConfigParser

print('Beginning file download with requests')

url = 'https://copr.fedorainfracloud.org/coprs/openscapmaint/openscap-latest/repo/' \
      'epel-7/openscapmaint-openscap-latest-epel-7.repo'
r = requests.get(url)

with open('primary.sqlite', 'wb') as f:
    f.write(r.content)

# Retrieve HTTP meta-data
print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)

config = ConfigParser.ConfigParser()
config.read('primary.sqlite')

base_url = config.get('openscapmaint-openscap-latest', 'baseurl')

arch_base_url = base_url.replace("$basearch", "x86_64")

print arch_base_url

conn = sqlite3.connect('primary.sqlite')

c = conn.cursor()

rows = c.execute("""
SELECT t.name, MAX(t.version), t."release"
FROM packages t
WHERE t.name = "scap-workbench"
    OR t.name = "scap-security-guide"
    OR t.name = "openscap-daemon"
    OR t.name = "openscap"
    OR t.name = "scap-workbench"
GROUP BY t.name;
""")

for row in rows:
    print row[0], row[1], row[2]

conn.close()
