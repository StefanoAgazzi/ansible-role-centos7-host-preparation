[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0) [![Build Status](https://travis-ci.com/StefanoAgazzi/ansible-role-centos7-host-preparation.svg?branch=master)](https://travis-ci.com/StefanoAgazzi/ansible-role-centos7-host-preparation)

centos7-host-preparation
=========

This role is intended to setup a CentOS or (Enteprise Linux) base system, installing essential packages and services.

Especially it configures the following repositories:
-   the EPEL repository
([https://fedoraproject.org/wiki/EPEL](https://fedoraproject.org/wiki/EPEL))

-   the openscap-latest copr repository
([https://copr.fedorainfracloud.org/coprs/openscapmaint/openscap-latest](https://copr.fedorainfracloud.org/coprs/openscapmaint/openscap-latest))


A brief description of the role goes here.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: StefanoAgazzi.centos7-host-preparation, x: 42 }

License
-------

GPLv3

Author Information
------------------

Stefano Agazzi
StefanoAgazzi.github.io
