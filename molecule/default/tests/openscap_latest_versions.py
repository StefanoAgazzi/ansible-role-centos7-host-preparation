import ConfigParser
import requests
import sqlite3
import bz2

import untangle

print('Beginning file download with requests')

url = 'https://copr.fedorainfracloud.org/coprs/openscapmaint/openscap-latest/repo/' \
      'epel-7/openscapmaint-openscap-latest-epel-7.repo'
r = requests.get(url)

with open('openscapmaint-openscap-latest-epel-7.repo', 'wb') as f:
    f.write(r.content)

# Retrieve HTTP meta-data
print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)

config = ConfigParser.ConfigParser()
config.read('openscapmaint-openscap-latest-epel-7.repo')

base_url = config.get('openscapmaint-openscap-latest', 'baseurl')

arch_base_url = base_url.replace("$basearch", "x86_64")

print(arch_base_url)

doc = untangle.parse(arch_base_url + "/repodata/repomd.xml")

for element in doc.repomd.data:
    if element['type'] == "primary_db":
        url = arch_base_url + "/" + element.location['href']
        r = requests.get(url)

        with open('primary.sqlite.bz2', 'wb') as f:
            f.write(r.content)

        file_path = 'primary.sqlite.bz2'
        zipfile = bz2.BZ2File(file_path)  # open the file
        data = zipfile.read()  # get the decompressed data
        new_file_path = file_path[:-4]  # assuming the filepath ends with .bz2
        open(new_file_path, 'wb').write(data)  # write a uncompressed file

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
    print (row[0] + " " + row[1] + " " + row[2])

conn.close()
