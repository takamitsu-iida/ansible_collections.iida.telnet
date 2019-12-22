# Ansible Collection - iida.telnet

Ansible Collection for telnet.

## Requirements

- Ansible 2.9 or later

## Install/Uninstall

1. Clone this repository

```bash
git clone https://github.com/takamitsu-iida/ansible_collections.iida.telnet.git
```

1. Build collection

```bash
make build
```

1. Install collection to your personal environment

The collection will be installed to ~/.ansible/collections/ansible_collections/

```bash
make install
```

## Example

hosts

```ini
[telnet_routers]
r1 ansible_host=192.168.122.179
```

group_vars/telnet_routers.yml

```yml
---

ansible_connection: network_cli  # in case of ssh. telnet does not require this.
ansible_ssh_common_args: ""      # in case of ssh.

ansible_network_os: ios
ansible_user: cisco
ansible_password: cisco
ansible_become: yes
ansible_become_method: enable
ansible_become_pass: cisco
```

playbook

```yml
---

- name: execute command on cisco devices
  hosts: r1  # telnet_routers
  gather_facts: False

  tasks:

    - name: send commands
      iida.telnet.command:
        debug: true
        log: true
        console: false
        commands:
          - command: clear counters gig 2
            prompt: '\[confirm\]'
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

    - name: command histories (for debug purpose)
      debug:
        var: r.command_histories

    - name: prompt histories (for debug purpose)
      debug:
        var: r.prompt_histories
```

execution example

```bash
iida-macbook-pro:ansible_collections.iida.telnet iida$ ansible-playbook site.yml

PLAY [execute command on cisco devices] *************************************************************
Sunday 22 December 2019  19:21:10 +0900 (0:00:00.073)       0:00:00.073 *******
Sunday 22 December 2019  19:21:10 +0900 (0:00:00.072)       0:00:00.072 *******

TASK [send commands] ********************************************************************************
ok: [r1]
Sunday 22 December 2019  19:21:15 +0900 (0:00:05.241)       0:00:05.315 *******
Sunday 22 December 2019  19:21:15 +0900 (0:00:05.242)       0:00:05.315 *******

TASK [show stdout] **********************************************************************************
ok: [r1] => {}

MSG:

-----
y

-----
Building configuration...

Current configuration : 99 bytes
!
interface GigabitEthernet2
 ip address dhcp
 negotiation auto
 no mop enabled
 no mop sysid
end

-----
CPU utilization for five seconds: 0%/0%; one minute: 0%; five minutes: 0%



Sunday 22 December 2019  19:21:16 +0900 (0:00:01.070)       0:00:06.386 *******
Sunday 22 December 2019  19:21:16 +0900 (0:00:01.070)       0:00:06.385 *******

TASK [command histories (for debug purpose)] ********************************************************
ok: [r1] => {
    "r.command_histories": [
        "terminal length 0",
        "terminal width 512",
        "enable",
        "cisco",
        "clear counters gig 2",
        "y",
        "show run int gig 2",
        "show process cpu | inc CPU",
        "quit"
    ]
}
Sunday 22 December 2019  19:21:17 +0900 (0:00:01.064)       0:00:07.451 *******
Sunday 22 December 2019  19:21:17 +0900 (0:00:01.064)       0:00:07.450 *******

TASK [prompt histories (for debug purpose)] *********************************************************
ok: [r1] => {
    "r.prompt_histories": [
        "Username:",
        "Password:",
        "csr>",
        "Password:",
        "csr#",
        "[confirm]",
        "csr#"
    ]
}

PLAY RECAP ******************************************************************************************
r1                         : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

Sunday 22 December 2019  19:21:18 +0900 (0:00:01.029)       0:00:08.481 *******
===============================================================================
iida.telnet.command ----------------------------------------------------- 5.24s
debug ------------------------------------------------------------------- 3.17s
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
total ------------------------------------------------------------------- 8.41s
Sunday 22 December 2019  19:21:18 +0900 (0:00:01.030)       0:00:08.480 *******
===============================================================================
send commands -------------------------------------------------------------------------------- 5.24s
show stdout ---------------------------------------------------------------------------------- 1.07s
command histories (for debug purpose) -------------------------------------------------------- 1.07s
prompt histories (for debug purpose) --------------------------------------------------------- 1.03s
iida-macbook-pro:ansible_collections.iida.telnet iida$
```
