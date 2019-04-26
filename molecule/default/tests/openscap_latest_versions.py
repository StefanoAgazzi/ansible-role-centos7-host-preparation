# TODO: use tests.config
# TODO: use logging file handler, use json format
# TODO: add exception handler

import bz2
import logging
import sqlite3
from configparser import ConfigParser

import requests
import untangle

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PackageInfo:
    def __init__(self, name, version, release):
        self.name = name
        self.version = version
        self.release = release

    def __str__(self):
        return "name: " + self.name + ", version: " + \
               self.version + ", release:" + self.release


def download_primary_repo_db():
    url = 'https://copr.fedorainfracloud.org/coprs/openscapmaint/openscap-latest/repo/' \
          'epel-7/openscapmaint-openscap-latest-epel-7.repo'

    logger.info('Beginning repo file download')
    logger.info('url:' + url)

    r = requests.get(url)

    with open('openscapmaint-openscap-latest-epel-7.repo', 'wb') as f:
        logger.info('Saving repo file locally')
        f.write(r.content)

    config = ConfigParser.ConfigParser()
    config.read('openscapmaint-openscap-latest-epel-7.repo')
    base_url = config.get('openscapmaint-openscap-latest', 'baseurl')
    logger.debug('base_url read from repo file:' + base_url)

    arch_base_url = base_url.replace("$basearch", "x86_64")
    logger.debug(arch_base_url)

    logging.info('Parsing repomd.xml')
    doc = untangle.parse(arch_base_url + "/repodata/repomd.xml")

    for element in doc.repomd.data:
        if element['type'] == "primary_db":
            url = arch_base_url + "/" + element.location['href']
            r = requests.get(url)
            logger.info('Saving primary db compressed file locally')
            with open('primary.sqlite.bz2', 'wb') as f:
                f.write(r.content)

            file_path = 'primary.sqlite.bz2'
            zipfile = bz2.BZ2File(file_path)  # open the file
            logger.info('Decompressing primary db')
            data = zipfile.read()  # get the decompressed data
            new_file_path = file_path[:-4]  # assuming the file_path ends with .bz2
            logger.info('Saving primary db decompressed file locally')
            open(new_file_path, 'wb').write(data)  # write a uncompressed file


def get_packages_info_from_primary_repo_db():
    download_primary_repo_db();

    logger.info('Opening db connection')
    conn = sqlite3.connect('primary.sqlite')

    c = conn.cursor()

    logger.info('Querying db')
    rows = c.execute("""
    SELECT t.name, MAX(t.version), t."release"
    FROM packages t
    WHERE t.name = "scap-workbench"
        OR t.name = "scap-security-guide"
        OR t.name = "openscap-daemon"
        OR t.name = "openscap"
    GROUP BY t.name;
    """)

    logger.debug("Packages Info:")
    packages = {}
    for row in rows:
        p = PackageInfo(row[0], row[1], row[2])
        logger.debug(p)
        packages[p.name] = p

    logger.info('Closing db connection')

    conn.close()

    return packages
