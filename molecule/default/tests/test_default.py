import logging
from os import path

from packaging.version import Version

from molecule.default.tests import openscap_copr_info_fetcher

logging.basicConfig(level=logging.DEBUG)
LOGGER: logging.Logger = logging.getLogger(__name__)


def test_hosts_file(host):
    host = host.file('/etc/hosts')

    assert host.exists
    assert host.user == 'root'
    assert host.group == 'root'


def test_packages_installation(host):
    LOGGER.info("check required packages are installed")

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
    LOGGER.info("check services are running and enabled at boot")

    installed_packages = {
        host.package('openscap').name:
        host.package('openscap'),
        host.package('openscap-daemon').name:
        host.package('openscap-daemon'),
        host.package('scap-security-guide').name:
        host.package('scap-security-guide')
    }

    # check that installed packages come from the copr repo
    # by checking they are the same version (or later)
    copr_packages = openscap_copr_info_fetcher.get_packages_info()

    for package in installed_packages.keys():
        assert Version(installed_packages[package].version) >= \
               Version(copr_packages[package].version)


def test_services_are_running_and_enabled(host):
    LOGGER.info("check services are running and enabled")

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
                LOGGER.debug("check_docker_cgroup: True")
                return True

    LOGGER.debug("check_docker_cgroup: False")
    return False


def check_docker_env_file_exists():
    docker_env_file_exists = path.exists('/.dockerenv')
    LOGGER.debug("check_docker_env_file_exists: %s", docker_env_file_exists)
    return docker_env_file_exists


def running_inside_docker_container():
    LOGGER.info("check if running inside docker")

    return check_docker_cgroup() or check_docker_env_file_exists()


def test_grub():
    LOGGER.info("check grub default boot the first item in menu")

    if not running_inside_docker_container():
        try:
            grub_config_file_content = open('/etc/default/grub', 'r').read()
            assert grub_config_file_content.find(
                'GRUB_DEFAULT=0') != -1 or grub_config_file_content.find(
                    'GRUB_DEFAULT="0"') != -1
        except FileNotFoundError:
            assert False
