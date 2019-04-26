"""
Default scenario test
"""

import os

import testinfra.utils.ansible_runner

TESTINFRA_HOSTS = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    """

    :param host: host under test
    """

    host_file = host.file('/etc/hosts')

    assert host_file.exists
    assert host_file.user == 'root'
    assert host_file.group == 'root'
