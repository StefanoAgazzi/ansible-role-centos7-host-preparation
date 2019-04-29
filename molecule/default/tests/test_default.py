import os
from os import path

import semantic_version
import testinfra.utils.ansible_runner

from molecule.default.tests import openscap_latest_versions

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_packages_installation(host):
    epel_release = host.package('epel-release')
    python = host.package('python')
    libselinux_python = host.package('libselinux-python')
    libsemanage_python = host.package('libsemanage-python')
    ntp = host.package('ntp')
    firewalld = host.package('firewalld')
    htop = host.package('htop')

    # just check some examples packages,
    # mostly installed from added repos
    assert epel_release.is_installed
    assert python.is_installed
    assert libselinux_python.is_installed
    assert libsemanage_python.is_installed
    assert htop.is_installed
    assert ntp.is_installed
    assert firewalld.is_installed


def test_openscap_packages_installations(host):
    installed_packages = {host.package('openscap').name:
                          host.package('openscap'),
                          host.package('openscap-daemon').name:
                          host.package('openscap-daemon'),
                          host.package('scap-security-guide').name:
                          host.package('scap-security-guide')}

    # check that installed packages come from the copr repo
    # by checking they are the same version (or later)
    copr_packages = openscap_latest_versions \
        .get_packages_info_from_primary_repo_db()

    for package in installed_packages.keys():
        assert semantic_version.Version(
            installed_packages[package].version) >= \
               semantic_version.Version(copr_packages[package].version)


def test_services_are_running_and_enabled(host):
    firewalld = host.service("firewalld")
    ntpd = host.service("ntpd")

    assert firewalld.is_running
    assert firewalld.is_enabled
    assert ntpd.is_running
    assert ntpd.is_enabled


def check_docker_cgroup():
    with open('/proc/self/cgroup', 'r') as procfile:
        for line in procfile:
            fields = line.strip().split('/')
            if 'docker' in fields:
                return True
    return False


def check_docker_env_file():
    return path.exists('/.dockerenv')


def running_inside_docker_container():
    return check_docker_cgroup() and check_docker_env_file()


def test_grub():
    if not running_inside_docker_container():
        assert open('/etc/default/grub', 'r').read() \
                   .find('GRUB_DEFAULT=0') != -1
