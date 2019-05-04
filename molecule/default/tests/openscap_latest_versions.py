# TODO: use tests.config
# TODO: use logging file handler, use json format
# TODO: add exception handler

import bz2

import logging
from logging import Logger

import sqlite3
from collections import namedtuple
from configparser import ConfigParser

import requests
import untangle

logging.basicConfig(level=logging.DEBUG)
LOGGER: Logger = logging.getLogger(__name__)


def build_package_info(name, version, release):
    package = namedtuple('package', 'name version release')
    return package(name, version, release)


def download_primary_repo_db():
    url = 'https://copr.fedorainfracloud.org/coprs/openscapmaint/openscap-latest/repo/' \
          'epel-7/openscapmaint-openscap-latest-epel-7.repo'

    LOGGER.info("Beginning repo file download")
    LOGGER.info("url: %s", url)

    resp = requests.get(url)

    with open('openscapmaint-openscap-latest-epel-7.repo', 'wb') as file:
        LOGGER.info('Saving repo file locally')
        file.write(resp.content)

    config = ConfigParser()
    config.read('openscapmaint-openscap-latest-epel-7.repo')
    base_url = config.get('openscapmaint-openscap-latest', 'baseurl')
    LOGGER.debug("base_url read from repo file: %s", base_url)

    arch_base_url = base_url.replace("$basearch", "x86_64")
    LOGGER.debug(arch_base_url)

    logging.info('Parsing repomd.xml')
    doc = untangle.parse(arch_base_url + "/repodata/repomd.xml")

    for element in doc.repomd.data:
        if element['type'] == "primary_db":
            url = arch_base_url + "/" + element.location['href']
            resp = requests.get(url)
            LOGGER.info('Saving primary db compressed file locally')
            with open('primary.sqlite.bz2', 'wb') as file:
                file.write(resp.content)

            file_path = 'primary.sqlite.bz2'
            zipfile = bz2.BZ2File(file_path)  # open the file
            LOGGER.info('Decompressing primary db')
            data = zipfile.read()  # get the decompressed data
            new_file_path = file_path[:
                                      -4]  # assuming the file_path ends with .bz2
            LOGGER.info('Saving primary db decompressed file locally')
            open(new_file_path, 'wb').write(data)  # write a uncompressed file


def get_packages_info_from_primary_repo_db():
    download_primary_repo_db()

    LOGGER.info('Opening db connection')
    conn = sqlite3.connect('primary.sqlite')

    cursor = conn.cursor()

    LOGGER.info('Querying db')
    rows = cursor.execute("""
    SELECT t.name, MAX(t.version), t."release"
    FROM packages t
    WHERE t.name = "scap-workbench"
        OR t.name = "scap-security-guide"
        OR t.name = "openscap-daemon"
        OR t.name = "openscap"
    GROUP BY t.name;
    """)

    LOGGER.debug("Packages Info:")
    packages = {}
    for row in rows:
        package_info = build_package_info(row[0], row[1], row[2])
        LOGGER.debug(package_info)
        packages[package_info.name] = package_info

    LOGGER.info('Closing db connection')

    conn.close()

    return packages
