# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

# (c) 2019, Takamitsu IIDA (@takamitsu-iida)

# telnetlib doc
# https://docs.python.jp/3/library/telnetlib.html

import re
from time import sleep

from ansible.module_utils._text import to_text, to_bytes
from ansible.module_utils.network.common.utils import to_list

# Python3 telnetlib.py needs to be modified so that we can receive a lot of messages
# from network device like show tech-support.
from ansible_collections.iida.telnet.plugins.module_utils.telnetlib import Telnet

class TelnetClient(object):

  # DEFAULTS
  DEFAULT_BECOME = False
  DEFAULT_CONNECT_TIMEOUT = 10
  DEFAULT_LOGIN_TIMEOUT = 5
  DEFAULT_COMMAND_TIMEOUT = 5
  DEFAULT_PAUSE = 1
  DEFAULT_CONSOLE = False

  def __init__(self, params):
    """constructor for TelnetClient class

    expected key of params
      - check_mode
      - commands
      - network_os
      - host
      - port
      - user
      - password
      - become
      - become_pass
      - connect_timeout
      - login_timeout
      - command_timeout
      - pause
      - console

    Arguments:
        params {dict} -- param dictionary
    """
    self.params = params

    # is check_mode or not, False if not specified
    self._check_mode = params.get('check_mode', False)

    self._commands = params.get('commands')
    self._network_os = params.get('network_os')
    self._host = params.get('host')
    self._port = params.get('port', 23)
    self._user = params.get('user')
    self._password = params.get('password')
    self._become = params.get('become', self.DEFAULT_BECOME)
    self._become_pass = params.get('become_pass')
    self._connect_timeout = params.get('connect_timeout', self.DEFAULT_CONNECT_TIMEOUT)
    self._login_timeout = params.get('login_timeout', self.DEFAULT_LOGIN_TIMEOUT)
    self._command_timeout = params.get('command_timeout', self.DEFAULT_COMMAND_TIMEOUT)
    self._pause = params.get('pause', self.DEFAULT_PAUSE)
    self._console = params.get('console', self.DEFAULT_CONSOLE)

    # output buffer
    self._raw_outputs = list()

    # command history buffer
    self.command_histories = list()

    # current prompt
    self.prompt = ""

    # prompt history buffer
    self.prompt_histories = list()

    # list of command prompt regex
    self.command_prompts = list()
    self.command_prompts.append(re.compile(br"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?$"))

    # list of login prompt regex
    self.login_prompts = list()
    self.login_prompts.append(re.compile(br"[Ll]ogin: ?|[Uu]sername: ?"))

    # list of password prompt regex
    self.password_prompts = list()
    self.password_prompts.append(re.compile(br"[\r\n](?:Local_)?[Pp]assword: ?$"))

    # Telnet class object
    self.connection = None

  #
  # GETTER/SETTER
  #
  def check_mode(self, *_):
    """get/set _check_mode"""
    if not _:
      return self._check_mode
    self._check_mode = _[0]
    return self

  def commands(self, *_):
    """get/set _commands"""
    if not _:
      return self._commands
    self._commands = _[0]
    return self

  def network_os(self, *_):
    """get/set _network_os"""
    if not _:
      return self._network_os
    self._network_os = _[0]
    return self

  def host(self, *_):
    """get/set _host"""
    if not _:
      return self._host
    self._host = _[0]
    return self

  def port(self, *_):
    """get/set _port"""
    if not _:
      return self._port
    self._port = _[0]
    return self

  def user(self, *_):
    """get/set _user"""
    if not _:
      return self._user
    self._user = _[0]
    return self

  def password(self, *_):
    """get/set _password"""
    if not _:
      return self._password
    self._password = _[0]
    return self

  def become(self, *_):
    """get/set _become"""
    if not _:
      return self._become
    self._become = _[0]
    return self

  def become_pass(self, *_):
    """get/set _become_pass"""
    if not _:
      return self._become_pass
    self._become_pass = _[0]
    return self

  def connect_timeout(self, *_):
    """get/set _connect_timeout"""
    if not _:
      return self._connect_timeout
    self._connect_timeout = _[0]
    return self

  def login_timeout(self, *_):
    """get/set _login_timeout"""
    if not _:
      return self._login_timeout
    self._login_timeout = _[0]
    return self

  def command_timeout(self, *_):
    """get/set _command_timeout"""
    if not _:
      return self._command_timeout
    self._command_timeout = _[0]
    return self

  def pause(self, *_):
    """get/set _pause"""
    if not _:
      return self._pause
    self._pause = _[0]
    return self

  def console(self, *_):
    """get/set _console"""
    if not _:
      return self._console
    self._console = _[0]
    return self

  def raw_outputs(self, *_):
    """get/set _raw_outputs"""
    if not _:
      return self._raw_outputs
    self._raw_outputs = _[0]
    return self

  # END OF GETTER/SETTER

  def add_raw_outputs(self, output):
    """add output to raw_outputs"""
    self.raw_outputs().append(to_text(output, errors='surrogate_or_strict'))


  def add_command_histories(self, cmd):
    """add command to command_histories"""
    self.command_histories.append(cmd)


  def add_prompt_histories(self, prompt):
    """add prompt to prompt_histories"""
    if self.prompt == prompt:
      return
    self.prompt_histories.append(prompt)
    self.prompt = prompt


  def get_connection(self):
    """Connect to the target host

    Returns:
        [telnetlib.Telnet] -- telnetlib.Telnet class object or None
    """
    if self.connection is not None:
      return self.connection

    host = self.host()
    port = self.port()
    connect_timeout = self.connect_timeout()

    # try to connect target host using telnetlib.Telnet
    tn = None
    try:
      # tn = telnetlib.Telnet(host, port=port, timeout=connect_timeout)
      tn = Telnet(host, port=port, timeout=connect_timeout)
      self.connection = tn
    except OSError:
      return None

    # tn.set_debuglevel(10)
    return tn


  def close_connection(self):
    if self.connection:
      self.connection.close()
      self.connection = None


  def login(self):
    """Login to the target host"""
    tn = self.get_connection()
    if tn is None:
      return

    user = self.user()
    password = self.password()

    command_prompts = self.command_prompts
    login_prompts = self.login_prompts
    password_prompts = self.password_prompts

    login_timeout = self.login_timeout()

    try:
      if self.console():
        sleep(2)
        tn.write(b'\n')

      if self.user():
        index, match, out = tn.expect(login_prompts, login_timeout)
        if index < 0:
          self.close_connection()
          raise Exception('Failed to expect login prompt: %s' % to_text(out))
        self.match_prompt(match)
        self.add_raw_outputs(out)
        tn.write(to_bytes('%s\n' % user))

      if password:
        index, match, out = tn.expect(password_prompts, login_timeout)
        if index < 0:
          self.close_connection()
          raise Exception('Failed to expect password prompt: %s' % to_text(out))
        self.match_prompt(match)
        self.add_raw_outputs(out)
        tn.write(to_bytes('%s\n' % password))

      # wait for command prompt
      index, match, out = tn.expect(command_prompts, login_timeout)
      if index < 0:
        self.close_connection()
        raise Exception('Wrong password or failed to expect prompt: %s' % to_text(out))
      self.match_prompt(match)
      self.add_raw_outputs(out)

      self.on_login()
      self.on_become()

    except EOFError as e:
      self.close_connection()
      raise Exception('Telnet action failed: %s' % to_text(e))


  def on_login(self):
    network_os = self.network_os()

    if network_os == 'ios':
      self.send_and_wait('terminal length 0')
      self.send_and_wait('terminal width 512')
      return

    if network_os in ('fujitsu_sir', 'fujitsu_srs'):
      self.send_and_wait('terminal pager disable')
      return


  def on_become(self):
    if self.prompt.endswith('#'):
      return

    if self.become() is not True:
      return

    become_pass = self.become_pass()
    if not become_pass:
      return

    network_os = self.network_os()
    if network_os == 'ios':
      # in case of ios, send 'enable' and wait for Password:
      self.send_and_wait('enable', prompt='[Pp]assword: ?', answer=become_pass)
      if not self.prompt or not self.prompt.endswith('#'):
        self.close_connection()
        raise Exception('failed to elevate privilege to enable mode still at prompt [%s]' % self.prompt)

    if network_os in ('fujitsu_sir', 'fujitsu_srs'):
      # in case of fujitsu device, send 'admin' and wait for Password:
      self.send_and_wait('admin', prompt='[Pp]assword: ?', answer=become_pass)
      if not self.prompt or not self.prompt.endswith(b'#'):
        self.close_connection()
        raise Exception('failed to elevate privilege to enable mode still at prompt [%s]' % self.prompt)


  def logout(self):
    """Logout from the host"""
    tn = self.get_connection()
    if tn is None:
      return

    network_os = self.network_os()

    if network_os == 'ios':
      self.send_command('quit')

    if network_os in ('fujitsu_sir', 'fujitsu_srs'):
      self.send_command('exit')

    self.close_connection()


  def send_command(self, command):
    tn = self.get_connection()
    tn.write(to_bytes('%s\n' % command))
    self.add_command_histories(command)


  def match_prompt(self, match):
    """regex match object to prompt string
    """
    if not match:
      return ''
    matched_prompt = to_text(match.group()).strip()
    self.add_prompt_histories(matched_prompt)
    return matched_prompt


  def send_and_wait(self, command, prompt=None, answer=None):
    """Send a command and wait for prompt"""
    tn = self.get_connection()

    command_timeout = self.command_timeout()

    try:
      self.send_command(command)

      if prompt:
        index, match, out = tn.expect([to_bytes(prompt)], command_timeout)
        if index < 0:
          self.close_connection()
          raise Exception('Failed to expect prompt: %s : %s' % (command, prompt))
        matched_prompt = self.match_prompt(match)
        self.add_raw_outputs(out)

        if answer is not None:
          self.send_command(answer)
          # in case of no output like this, we need to wait for the second prompt
          # simply wait 1 second here.
          # csr#>
          # csr#>
          sleep(1)
        else:
          return to_text(out, errors='surrogate_or_strict')

      index, match, out = tn.expect(self.command_prompts, command_timeout)
      if index < 0:
        self.close_connection()
        raise Exception('Failed to expect prompts: %s' % command)
      matched_prompt = self.match_prompt(match)
      self.add_raw_outputs(out)

      # remove command echo and tailing prompt
      # lines = out.splitlines()
      # if len(lines) >= 1:
      #   lines = lines[1:-1]
      # out = '\n'.join(lines)
      cleaned = []
      for line in to_text(out, errors='surrogate_or_strict').splitlines():
        if (command and line.strip() == command.strip()) or (matched_prompt and (matched_prompt == line.strip())):
          continue
        cleaned.append(line)

      return '\n'.join(cleaned).strip()

    except EOFError as e:
      self.close_connection()
      raise Exception('Telnet action failed: %s' % to_text(e))


  def run_commands(self):
    commands = self.commands()
    commands = to_list(commands)
    pause = self.pause()

    responses = list()
    for i, cmd in enumerate(commands):
      if isinstance(cmd, dict):
        command = cmd.get('command', '')
        prompt = cmd.get('prompt', None)
        answer = cmd.get('answer', None)
      else:
        command = cmd
        prompt = None
        answer = None

      out = self.send_and_wait(command, prompt=prompt, answer=answer)
      responses.append(out)

      if i != len(commands) -1:
        sleep(pause)

    return responses
