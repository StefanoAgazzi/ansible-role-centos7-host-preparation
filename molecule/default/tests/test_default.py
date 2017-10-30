import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_packages_installation(Package):
    epel_release = Package('epel-release')
    python = Package('python')
    libselinux_python = Package('libselinux-python')
    libsemanage_python = Package('libsemanage-python')
    ntp = Package('ntp')
    firewalld = Package('firewalld')
    openscap = Package('openscap')
    openscap_daemon = Package('openscap-daemon')
    scap_security_guide = Package('scap-security-guide')
    kernel_ml = Package('kernel-ml')
    htop = Package('htop')

    # just check some examples packakges,
    # mostly installed from added repos
    assert epel_release.is_installed
    assert python.is_installed
    assert libselinux_python.is_installed
    assert libsemanage_python.is_installed
    assert htop.is_installed
    assert kernel_ml.is_installed
    assert ntp.is_installed
    assert firewalld.is_installed

    # TODO: check version dinamically using copr api

    # check installed packages come from the copr repo
    # by checking is the same version of the copr repos version
    assert openscap.version.startswith("1.2.15")
    assert openscap_daemon.version.startswith("0.1.7")
    assert scap_security_guide.version.startswith("0.1.35")


def test_services_are_running_and_enabled(Service):
    firewalld = Service("firewalld")
    ntpd = Service("ntpd")

    assert firewalld.is_running
    assert firewalld.is_enabled
    assert ntpd.is_running
    assert ntpd.is_enabled

# disable when running inside docker

# def test_grub(File):
#     grub = File("/etc/default/grub")
#
#     assert grub.contains("GRUB_DEFAULT=saved")
