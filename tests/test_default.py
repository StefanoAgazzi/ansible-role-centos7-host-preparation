import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_hosts_file(File):
    f = File('/etc/hosts')

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

    assert epel_release.is_installed
    assert python.is_installed
    assert libselinux_python.is_installed
    assert libsemanage_python.is_installed
    assert ntp.is_installed
    assert firewalld.is_installed


def test_services_running_and_enabled(Service):
    firewalld = Service("firewalld")
    ntpd = Service("ntpd")

    assert firewalld.is_running
    assert firewalld.is_enabled
    assert ntpd.is_running
    assert ntpd.is_enabled
