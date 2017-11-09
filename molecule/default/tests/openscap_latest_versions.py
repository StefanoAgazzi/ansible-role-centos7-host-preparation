from copr import create_client2_from_params

cl = create_client2_from_params(root_url="http://copr.fedorainfracloud.org/")

projects = cl.projects.get_list(name="openscap-latest", limit=100)

for p in projects:
    print(p)
    builds = p.get_builds(limit=100)
    for b in builds:
        print(b)
        print ("\n")
        print(b.package_name + "        " + b.package_version)
