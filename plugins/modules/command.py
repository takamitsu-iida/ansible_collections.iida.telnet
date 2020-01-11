#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, broad-except, anomalous-backslash-in-string


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
- name: execute command on cisco devices over telnet connection
  # hosts: behind_bastion
  hosts: r1
  gather_facts: false  # this must be false

  tasks:

    - name: send commands
      # behind bastion host requires delegation
      # delegate_to: pg04
      iida.telnet.command:
        debug: true
        log: true
        console: false
        commands:
          - command: clear counters gig 2
            prompt: "\[confirm\]"
            answer: y
          - show run int gig 2
          - show process cpu | inc CPU
      register: r

    - name: show stdout
      debug:
        msg: |
          {% for s in r.stdout %}
          -----
          {{ s }}

          {% endfor %}
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import string_types

# import from collection
from ansible_collections.iida.telnet.plugins.module_utils.telnet_util import TelnetClient


def to_lines(stdout):
  for item in stdout:
    if isinstance(item, string_types):
      item = str(item).split('\n')
    yield item


def main():
  """main entry point for module execution"""

  # read default value from TelnetClient class (module_utils/telnet_util.py)
  DEFAULT_BECOME = TelnetClient.DEFAULT_BECOME                    # False
  DEFAULT_CONNECT_TIMEOUT = TelnetClient.DEFAULT_CONNECT_TIMEOUT  # 10
  DEFAULT_LOGIN_TIMEOUT = TelnetClient.DEFAULT_LOGIN_TIMEOUT      # 5
  DEFAULT_COMMAND_TIMEOUT = TelnetClient.DEFAULT_COMMAND_TIMEOUT  # 5
  DEFAULT_PAUSE = TelnetClient.DEFAULT_PAUSE                      # 1
  DEFAULT_CONSOLE = TelnetClient.DEFAULT_CONSOLE                  # False

  argument_spec = dict(
    commands=dict(type='list', required=True),
    network_os=dict(default='ios', type='str'),
    host=dict(type='str', required=True),
    port=dict(default=23, type='int'),
    user=dict(default="", type='str'),
    password=dict(default="", type='str'),
    become=dict(default=DEFAULT_BECOME, type='bool'),
    become_pass=dict(default="", type='str'),
    connect_timeout=dict(default=DEFAULT_CONNECT_TIMEOUT, type='int'),
    login_timeout=dict(default=DEFAULT_LOGIN_TIMEOUT, type='int'),
    command_timeout=dict(default=DEFAULT_COMMAND_TIMEOUT, type='int'),
    pause=dict(default=DEFAULT_PAUSE, type='int'),
    console=dict(default=DEFAULT_CONSOLE, type='bool'),
    log=dict(default=False, type='bool'),
    debug=dict(default=False, type='bool')
  )

  # generate module instance
  module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

  tc = TelnetClient(module.params)
  result = tc.process_command()

  if result.get('failed'):
    module.fail_json(**result)

  module.exit_json(**result)


if __name__ == '__main__':
  main()
