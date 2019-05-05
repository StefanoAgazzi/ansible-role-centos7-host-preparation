# TODO: use logging file handler, use json format
# TODO: add exception handler
from collections import namedtuple
from configparser import ConfigParser

import logging
from logging import Logger

import os
from os import path

import sqlite3
import bz2
import requests
import untangle

logging.basicConfig(level=logging.DEBUG)
LOGGER: Logger = logging.getLogger(__name__)

TEST_CONFIG = ConfigParser()


def build_package_info(name, version, release):
    package = namedtuple('package', 'name version release')
    return package(name, version, release)


def download_repo_file(repo_url, repo_file_name):
    LOGGER.info("Beginning repo file download")
    LOGGER.info("url: %s", repo_url)

    resp = requests.get(repo_url + repo_file_name)

    with open(repo_file_name, 'wb') as file:
        LOGGER.info('Saving repo file locally')
        file.write(resp.content)

    return repo_file_name


def download_and_uncompress_db_file():
    uncompressed_db_file_name = ""
    compressed_db_file_name = ""

    arch = TEST_CONFIG.get('openscap-copr-repo', 'arch')
    repomd_xml = TEST_CONFIG.get('openscap-copr-repo', 'repomd_xml')

    config = ConfigParser()
    config.read('openscapmaint-openscap-latest-epel-7.repo')
    base_url = config.get('openscapmaint-openscap-latest', 'baseurl')
    LOGGER.debug("base_url read from repo file: %s", base_url)
    arch_base_url = base_url.replace("$basearch", arch)
    LOGGER.debug(arch_base_url)
    logging.info('Parsing repomd.xml')
    doc = untangle.parse(arch_base_url + repomd_xml)
    for element in doc.repomd.data:
        if element['type'] == "primary_db":
            compressed_db_file_location = element.location['href']
            url = arch_base_url + "/" + compressed_db_file_location
            resp = requests.get(url)
            LOGGER.info('Saving primary db compressed file locally')
            compressed_db_file_name = compressed_db_file_location.replace(
                "/", "")
            with open(compressed_db_file_name, 'wb') as file:
                file.write(resp.content)

            zipfile = bz2.BZ2File(compressed_db_file_name)  # open the file
            LOGGER.info('Decompressing primary db')
            data = zipfile.read()  # get the decompressed data
            # the file_path ends with .bz2
            uncompressed_db_file_name = compressed_db_file_name[:-4]
            LOGGER.info('Saving primary db decompressed file locally')
            open(uncompressed_db_file_name,
                 'wb').write(data)  # write a uncompressed file

    return compressed_db_file_name, uncompressed_db_file_name


def get_packages_info():
    files_to_remove = []
    if path.exists('tests.config'):
        # when executing with molecule verify
        TEST_CONFIG.read('tests.config')
    else:
        # when executing with IDE
        TEST_CONFIG.read('../tests.config')

    repo_url = TEST_CONFIG.get('openscap-copr-repo', 'repo_file_path')
    repo_file_name = TEST_CONFIG.get('openscap-copr-repo', 'repo_file_name')

    downloaded_repo_file_name = download_repo_file(repo_url, repo_file_name)
    files_to_remove.append(downloaded_repo_file_name)

    compressed_db_file_name,\
        uncompressed_db_file_name = download_and_uncompress_db_file()

    files_to_remove.append(compressed_db_file_name)
    files_to_remove.append(uncompressed_db_file_name)

    LOGGER.info('Opening db connection')

    conn = sqlite3.connect(uncompressed_db_file_name)

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
    remove_downloaded_files(files_to_remove)

    return packages


def remove_downloaded_files(files_to_remove):
    LOGGER.info('Removing downloaded files')

    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)


get_packages_info()
