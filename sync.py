import os

import paramiko
from paramiko import SSHClient
from scp import SCPClient


class ScpHelper(object):
  def __init__(self):
    self.ssh = None
    self.scp = None

  def connect(self, key_file, dest, port, username):
    self.ssh = SSHClient()
    # paramiko.util.log_to_file("/tmp/tmp.log")
    k = paramiko.RSAKey.from_private_key_file(key_file)
    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh.connect(dest, port=port, username=username, pkey=k)

    self.scp = SCPClient(self.ssh.get_transport())

  def shortcut(self, name):
    path = os.getenv("HOME")
    key_file = os.path.join(path, '.ssh', 'id_rsa')
    dest = ''
    port = 22
    username = ''
    if name == 'sun':
      dest = '202.112.113.219'
      username = 'qjin'
    elif name == 'uranus':
      dest = '202.112.113.30'
      username = 'jiac'
    elif name == 'mercurial':
      dest = '202.112.113.209'
      username = 'qjin'
    elif name == 'jupiter':
      dest = '222.29.195.82'
      port = 222
      username = 'qjin'
    elif name == 'earth':
      dest = '222.29.193.172'
      port = 226
      username = 'chenjia'
    elif name == 'rocks':
      dest = 'rocks.is.cs.cmu.edu'
      username = 'jiac'
    elif name == 'aladdin1':
      dest = 'aladdin1.inf.cs.cmu.edu'
      username = 'jiac'
    elif name == 'yy':
      dest = 'vid-gpu1.inf.cs.cmu.edu'
      username = 'jiac'
    elif name == 'xcl':
      dest = 'vid-gpu4.inf.cs.cmu.edu'
      username = 'informedia'
    elif name == 'hl':
      dest = 'vid-gpu6.inf.cs.cmu.edu'
      username = 'jiaac'

    return key_file, dest, port, username

  def connect_shortcut(self, name):
    key_file, dest, port, username = self.shortcut(name)
    self.connect(key_file, dest, port, username)

  def get(self, remote_file, local_file, recursive=False):
    self.scp.get(remote_file, local_file, recursive=recursive)

  def put(self, local_files, remote_path, recursive=False):
    self.scp.put(local_files, remote_path, recursive=recursive)

  def disconnect(self):
    self.scp.close()
