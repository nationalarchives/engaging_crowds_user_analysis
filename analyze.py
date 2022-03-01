#!/usr/bin/env python3

import data as d
import util as u
from analyze_time import start_times
from analyze_startstop import start_stop_dates

import pandas as pd

import os
import shutil

def get_project(wid):
    for proj_name, wids in d.PROJECTS.items():
        if wid in wids: return proj_name

def load():
  df = pd.read_csv('all_classifications.csv', parse_dates = d.dates, dtype = d.dtypes)
  for date in d.dates:
    if date == 'subj.date': continue
    df[date] = df[date].dt.tz_convert(None)
  #At this point, all date/time columns are datetime64[ns, UTC], except for subj.data, which is datetime64[ns]
  if len(df) != len(df.index.unique()): raise Exception("Index is not unique")
  if len(df.classification_id) != len(df.classification_id.unique()): raise Exception("Classification ids are not unique")
  #Uniques are returned in order of appearance, so this should maintain the correct id:name pairing
  d.WORKFLOWS = pd.Series(df.workflow_name.unique(), df.workflow_id.unique())
  return df

def prepare(class_df):
  class_df['project'] = class_df.workflow_id.apply(get_project)
  if class_df.project.isna().any(): raise Exception(class_df[class_df.project.isna()])

  class_df['workflow_type'] = class_df.workflow_id.apply(lambda x: d.workflow_map[x])

  class_df['duration'] = class_df['md.finished_at'].subtract(class_df['md.started_at'])

  utc_offset = class_df['md.utc_offset'].apply(lambda x: pd.Timedelta(x, unit = 'seconds'))
  class_df['local.started_at'] = class_df['md.started_at'] - utc_offset
  class_df['local.finished_at'] = class_df['md.finished_at'] - utc_offset

  #At this stage, we have just added columns to the original dataframe. No data has been lost.
  pre_discards = class_df.copy()

  #Data to discard
  negative_df = class_df[class_df.duration.apply(lambda x: x.total_seconds()) < 0].copy()
  class_df = class_df.drop(negative_df.index)

  anon_df = class_df[class_df.pseudonym.apply(lambda x: x[0] == 'a')].copy()
  class_df = class_df.drop(anon_df.index)

  #Useful subsets of the kept data
  p_counts = class_df.pseudonym.value_counts()
  mono_class_index = class_df[class_df.pseudonym.isin(p_counts.index[p_counts == 1])].index.copy()
  plural_class_index = class_df.index.drop(mono_class_index)

  return (
    class_df,
    {
      'mono': mono_class_index,
      'plural': plural_class_index,
    },
    pre_discards,
    ('Negative duration', negative_df, d.TIME_COLS, 'Uninterpretable'),
    ('Anonymous', anon_df, ['pseudonym'], 'May not be an individual; hashes can change, resulting in inconsistent identification across workflows/projects')
  )

if __name__ == '__main__':
  SAMPLE = 10
  d.HEAD = u.git_HEAD()
  if os.path.isdir(f'./secrets/graphs/{d.HEAD}/'):
    shutil.rmtree(f'./secrets/graphs/{d.HEAD}/')
  os.makedirs(f'./secrets/graphs/{d.HEAD}')

  u.Logger(f'./secrets/graphs/{d.HEAD}/log.txt')

  print('Loading data')
  original_df = load()
  print('Preparing data')
  class_df, subsets, undeleted_df, *deletions = prepare(original_df.copy())

  full_size = len(class_df)
  original_full_size = len(original_df)

  print('Discards')
  print('-' * len('discards'))
  print()
  discarded_count = 0
  for label, df, cols, justification in deletions:
    size = len(df)
    discarded_count += size
    if SAMPLE < size:
      sample_df = df.sample(SAMPLE)
      sample = SAMPLE
    else:
      sample_df = df
      sample = size
    print(f'{label} (showing {sample}/{size})')
    print('Justification:', justification)
    print(f'Discards a further {size} of original {original_full_size} classifications ({size / original_full_size:.2%})')
    print(sample_df[['workflow_name', 'classification_id', 'subject_ids'] + cols])
    for breakdown in ['project', 'workflow_name']:
      vc = pd.concat({'Discarded': df.value_counts(breakdown), 'of total': undeleted_df.value_counts(breakdown)}, axis = 1, verify_integrity = True).fillna(0)
      vc['% discarded'] = 100 * vc.iloc[:, 0] / vc.iloc[:, 1]
      print(f'Breakdown by {breakdown}')
      print(vc)

  print(f'Discarded a total of {discarded_count} ({discarded_count/original_full_size:.2%}) of {original_full_size:,} classifications.')
  print('\n')

  print('Subsets of undiscarded data')
  print('-' * len('subsets of undiscarded data'))
  print()
  for k, v in subsets.items():
    c = len(v)
    print(f'{k + ":":10}{c:7,} classifications ({c / full_size:06.2%} of {full_size} undiscarded classifications.)')
  print('\n\n')

  start_times(class_df.copy(), subsets)
  start_stop_dates(class_df.copy(), subsets)
