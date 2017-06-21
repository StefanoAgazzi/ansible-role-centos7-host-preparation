import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_hosts_file(File):
    f = File('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


# def test_zabbix_package(Package):
#     vi = Package('vi')
#     assert vi.is_installed
#     assert vi.version.startswith("1:3.0")
