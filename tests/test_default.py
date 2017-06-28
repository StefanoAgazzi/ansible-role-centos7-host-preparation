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
    # by chechking is the same version of the copr repos version
    assert openscap.version.startswith("1.2.14")
    assert openscap_daemon.version.startswith("0.1.6")
    assert scap_security_guide.version.startswith("0.1.33")


def test_services_are_running_and_enabled(Service):
    firewalld = Service("firewalld")
    ntpd = Service("ntpd")

    assert firewalld.is_running
    assert firewalld.is_enabled
    assert ntpd.is_running
    assert ntpd.is_enabled
