import git

def path_norm(x):
  y = '_'.join(x.split())
  return y.replace('&', 'and').replace('"', '').replace("'", '')

def fnam_norm(x):
  return path_norm(x).replace('/', '_')

def git_HEAD():
  return git.cmd.Git('.').rev_parse('HEAD')

def git_condition():
  g = git.cmd.Git('.')
  fetch = g.fetch()
  head = g.rev_parse('HEAD')
  status = g.status('--porcelain', '-b')
  return head + ' ' + status
  
#https://stackoverflow.com/a/14906787
import sys
class Logger(object):
  def __init__(self, logfile):
    self.terminal = sys.stdout
    self.log = open(logfile, 'w')
    sys.stdout = self
  def write(self, message):
    self.terminal.write(message)
    self.log.write(message)
  def flush(self):
    self.terminal.flush()
    self.log.flush()
  def close(self):
    self.log.close()
    self.terminal.flush()
    sys.stdout = self.terminal
  def __del__(self):
    self.close()
