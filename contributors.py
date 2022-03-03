import data as d
import numpy as np

def contributors(df, subsets):
  print('Breakdown of volunteers by number of projects contributed to')
  print('=' * len('Breakdown of volunteers by number of projects contributed to'))

  #Get a series listing projects contributed to, indexed by pseudonym and project
  #Although the values in this series are relevant to the problem, we never
  #actually use them -- operations on the index do everything that we need. So we
  #could store any value at all in here.
  projects = df.groupby(['pseudonym', 'project'])['project'].unique()

  #Get a series listing number of projects contributed to, indexed by pseudonym
  counts = df.groupby('pseudonym')['project'].nunique()

  c3 = counts[counts == 3]
  c2 = counts[counts == 2]
  c1 = counts[counts == 1]

  print(f'{"Contributors to all projects:":41}',       f'{len(c3):9}')
  print(f'{"Contributors to exactly 2 projects:":41}', f'{len(c2):9}')
  print(f'{"Contributors to exactly 1 project:":41}',  f'{len(c1):9}')

  print('-' * 30)

  mono_total = 0
  for project in d.HMS, d.SB, d.RBGE:
    #Starting with volunteers who contributed to 1 project, filter down to just the project of interest.
    x = projects.loc[c1.index] #Volunteers contributing to just one project
    x = x.index.get_level_values('project') == project #All rows with project of interest
    x = np.count_nonzero(x) #in this context, counts the Trues
    mono_total += x
    header = f'{project} only:'
    print(f'{header:41} {x:9}')
  print('Total mono contributors:', mono_total, '(should equal contributors to exactly one project, above)')

  print('-' * 30)

  pair_total = 0
  for pair, exclusion in [[[d.HMS, d.SB], d.RBGE], [[d.HMS, d.RBGE], d.SB], [[d.SB, d.RBGE], d.HMS]]:
    x = projects.loc[c2.index] #Volunteers contributing to exactly 2 projects
    x = projects.reindex(c2.index, level = 0)
    x = x[x.index.get_level_values('project') != exclusion]

    #Now each pseudonym that appears twice has contributed to both projects
    #As we started with all pseudonyms that appear exactly twice (x = project.loc[c2.index]), now
    #all pseudonyms appear once or twice. So by marking one instance of each duplicate as True, and
    #everything else as False, we get an array containing a number of Trues that is equal to the number
    #of contributors to each project.
    x = x.index.get_level_values('pseudonym').duplicated()
    x = np.count_nonzero(x) #in this context, counts the Trues

    pair_total += x
    header = f'{pair[0]} and {pair[1]} only:'
    print(f'{header:41} {x:9}')
  print('Total pair contributors:', pair_total, '(should equal contributors to exactly two projects, above)')

  print('-' * 30)

  for project in d.HMS, d.SB, d.RBGE:
    heading = f'Total contributors to {project}:'
    total = np.count_nonzero(projects.index.get_level_values('project') == project)
    print(f'{heading:41}', total)

    x = df[df.project == project] #All classifications on current project
    x = x.pseudonym.value_counts() #Number of classifications per volunteer on current project

    m_count = np.count_nonzero(x == 1)
    heading = f'Mono  contributors to {project}:'
    print(f'{heading:41}', m_count)

    p_count = np.count_nonzero(x != 1)
    heading = f'Multi contributors to {project}:'
    print(f'{heading:41}', p_count)

    assert m_count + p_count == total
    print('Mono + multi ==', m_count + p_count, f'(should equal total {total})')
#This is a way to do it all with one series, indexed by pseudonym and project, with values
#equal to the number of projects that the pseudonym has contributed to. It might not be any
#more efficient than the two-series solution above, and has the further disadvantage that we
#have to divide the counts[counts == 3] equivalent by 3, and counts[counts == 2] equivalent by
#2, as there will be one row for each pseudonum,project combination.
#count = df.groupby('pseudonym').project.nunique()
#count.name = 'proj_count'
#projects = df.join(count, on = 'pseudonym').set_index(['pseudonym', 'project'])['proj_count']
#dup_mask = projects.index.duplicated()
#unique_mask = ~dup_mask
#projects = projects[unique_mask]
#counts = projects

