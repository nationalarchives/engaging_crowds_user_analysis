import git

def path_norm(x):
  y = '_'.join(x.split())
  return y.replace('&', 'and')

def git_HEAD():
  return git.cmd.Git('.').rev_parse('HEAD')

def git_condition():
  g = git.cmd.Git('.')
  fetch = g.fetch()
  head = g.rev_parse('HEAD')
  status = g.status('--porcelain', '-b')
  return head + ' ' + status
  
