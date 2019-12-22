#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=C0111,E0611

# (c) 2019, Takamitsu IIDA (@takamitsu-iida)

ANSIBLE_METADATA = {'metadata_version': '0.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: iida.telnet.command

short_description: Send commands to network device over telnet

version_added: 2.9

description:
  - Send commands to network device over telnet
  - Action plugin execute telnet on behalf of the module

author:
  - Takamitsu IIDA (@takamitsu-iida)

options:
  commands:
    description:
      - List of commands to be executed over the telnet session.
    required: True

  network_os:
    description:
      - network os type
    default: ios

  host:
    description:
      - The target host ip address(or DNS name)
    required: True

  port:
    description:
      - The remote port
    default: 23

  user:
    description:
      - The user for login

  password:
    description:
      - The password for login

  become:
    description:
      - Need privilege escalation or not
    default: False

  become_pass:
    description:
      - The password for privilege escalation

  connect_timeout:
    description:
      - timeout for telnet to be connected
    default: 10

  login_timeout:
    description:
      - timeout for login prompt
    default: 5

  command_timeout:
    description:
      - timeout for command prompt
    default: 5

  pause:
    description:
      - Seconds to pause between each command issued
    default: 1

  log:
    description:
      - Create a log.
        The log file is written to the C(log) folder in the playbook root directory or
        role root directory if playbook is part of an ansible role.
        If the directory does not exist, it is created.
    type: bool
    default: 'false'

  console:
    description:
      - target device is console server or not.
    type: bool
    default: 'false'

'''

EXAMPLES = '''
- name: send commands
  iida.telnet.command:
    commands:
      - show process cpu | inc CPU
      - show ip int brief
  register: r

- hosts:
  tr1 ansible_host=172.28.128.3

- group_vars:
  ansible_network_os: ios
  ansible_user: cisco
  ansible_ssh_pass: cisco
  ansible_become: yes
  ansible_become_method: enable
  ansible_become_pass: cisco
'''

RETURN = '''
stdout:
  description: The set of responses from the commands
  type: list
  returned: always
  sample: [ '...', '...' ]

stdout_lines:
  description: The value of stdout split into a list
  type: list
  returned: always
  sample: [ ['...', '...'], ['...'], ['...'] ]

log_path:
  description: The full path to the log file
  returned: when log is yes
  type: string
'''
