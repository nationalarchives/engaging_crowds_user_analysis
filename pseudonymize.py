#!/usr/bin/env python3

import pandas as pd
import numpy as np
import csv
import argparse
import json
import os
import sys
import secrets
import string
from collections import Counter

#For debugging
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#pd.set_option('display.expand_frame_repr', None)

#Dictionary storing individual CSV files minimally altered
minimal_pseudonyms = {}

WORKFLOW_NAMES = {
  18504: 'meetings',
  18505: 'people',
  18611: '1-admission-number',
  18612: '2-date-of-entry',
  18613: '3-name',
  18614: 'quality-dd',
  18616: '5-age',
  18617: '7-place-of-birth-nationality',
  18618: '10-where-from',
  18619: 'years-at-sea',
  18621: '8-ship-ship-or-place-of-employment-last-ship',
  18622: '11-nature-of-complaint',
  18623: '12-date-of-discharge',
  18624: 'how-disposed-of-dd',
  18625: '14-number-of-days-in-hospital',
  19381: 'geography',
  19385: 'latitude-longitude'
}

EARLY_WORKFLOW_NAMES = {
  18504: 'meetings',
  18505: 'people',
  18611: '1-admission-number',
  18612: '2-date-of-entry',
  18613: '3-name',
  18614: '4-quality',
  18616: '5-age',
  18617: '6-place-of-birth',
  18618: '7-port-sailed-out-of',
  18619: '8-years-at-sea',
  18621: '9-last-services',
  18622: '10-under-what-circumstances-admitted-or-nature-of-complaint',
  18623: '11-date-of-discharge',
  18624: '12-how-disposed-of',
  18625: '13-number-of-days-victualled'
}

#Nested JSON data to keep (sits insides cells, will be expanded out to columns)
METADATA_KEEPERS = ['started_at', 'finished_at', 'utc_offset']
ALL_SUBJECT_KEEPERS = ['#priority', 'retired.retired_at']
_HMS_NHS_SUBJECT_KEEPERS = ['Filename']
_RBGE_SUBJECT_KEEPERS = ['Botanist','Group','Format','Species','Barcode']
WORKFLOW_SUBJECT_KEEPERS = {
  18504: ['Date', 'Page', 'Catalogue'],
  18505: ['Surnames starting with'],
  18611: _HMS_NHS_SUBJECT_KEEPERS,
  18612: _HMS_NHS_SUBJECT_KEEPERS,
  18613: _HMS_NHS_SUBJECT_KEEPERS,
  18614: _HMS_NHS_SUBJECT_KEEPERS,
  18616: _HMS_NHS_SUBJECT_KEEPERS,
  18617: _HMS_NHS_SUBJECT_KEEPERS,
  18618: _HMS_NHS_SUBJECT_KEEPERS,
  18619: _HMS_NHS_SUBJECT_KEEPERS,
  18621: _HMS_NHS_SUBJECT_KEEPERS,
  18622: _HMS_NHS_SUBJECT_KEEPERS,
  18623: _HMS_NHS_SUBJECT_KEEPERS,
  18624: _HMS_NHS_SUBJECT_KEEPERS,
  18625: _HMS_NHS_SUBJECT_KEEPERS,
  19381: _RBGE_SUBJECT_KEEPERS,
  19385: _RBGE_SUBJECT_KEEPERS,
}

#Workflow version to keep (will remove rows where the workflow with name 'key' has version not in 'value')
WORKFLOW_KEEPERS = {
  18504: [132.205],
  18505: [56.83],
  18611: [3.1],
  18612: [3.1, 4.1],
  18613: [3.1],
  18614: [3.1],
  18616: [3.1],
  18617: [3.1],
  18618: [3.1],
  18619: [3.1],
  18621: [3.1],
  18622: [3.1],
  18623: [3.1],
  18624: [3.1, 6.4],
  18625: [3.1],
  19381: [122.201],
  19385: [46.223],
}

#Based on displayed timestamp in the emails as I received them
HMS_NHS_LAUNCH_EMAIL_STAMP = '2021-06-29T16:19:00.000000Z'
SB_LAUNCH_EMAIL_STAMP = '2021-11-16T17:30:00.000000Z'
RBGE_LAUNCH_EMAIL_STAMP = '2022-01-11T17:11:00.000000Z'
WORKFLOW_STARTSTAMP = {
  18504: SB_LAUNCH_EMAIL_STAMP,
  18505: SB_LAUNCH_EMAIL_STAMP,
  18611: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18612: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18613: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18614: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18616: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18617: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18618: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18619: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18621: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18622: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18623: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18624: HMS_NHS_LAUNCH_EMAIL_STAMP,
  18625: HMS_NHS_LAUNCH_EMAIL_STAMP,
  19381: RBGE_LAUNCH_EMAIL_STAMP,
  19385: RBGE_LAUNCH_EMAIL_STAMP,
}

STOPSTAMP = '2022-02-01T00:00:00.000000'

parser = argparse.ArgumentParser()
parser.add_argument('workflows',
                    nargs = '*',
                    type = int,
                    default = WORKFLOW_NAMES.keys(),
                    help = 'Workflows to pseudonymise')
parser.add_argument('--exports', '-e',
                   default = 'exports',
                   help = 'Location of exported classifications files')
parser.add_argument('--dictionary', '-d',
                    default = 'secrets/identities.json',
                    help = 'Dictionary file to record the pseudonymisation result')
args = parser.parse_args()

#Validate CLI
for workflow in args.workflows:
  if not workflow in WORKFLOW_KEEPERS:
    raise Exception(f'Workflow "{workflow}" unknown to this script.')

if os.path.exists(args.dictionary):
  with open(args.dictionary) as f:
    identities = json.loads(f.read())

    #paranoia checks
    if len(identities) != len(set(identities.keys())):   raise Exception('User names in args.dictionary are not unique')
    if len(identities) != len(set(identities.values())): raise Exception('Pseudonames in args.dictionary are not unique')
else:
  identities = {}

def pseudonymize(row):
  def random_name():
    failcount = 0
    while failcount < 10:
      #TODO: 6 digits provides enough unique strings for Engaging Crowds. Should really be calculated.
      rnd = ''.join(secrets.choice(string.digits) for i in range(6))
      if f'{prefix}{rnd}' in identities.values():
        failcount += 1
      else:
        return rnd
    raise Exception('10 failures to generate a unique pseudonym. Try increasing the number of characters in the pseudonyms.')

  uid = row['user_id']
  if np.isnan(uid):
    #Anonymous user -- use the ip addr as the uid, so that all
    #classifications from the apparent-same IP addr get the same pseudonym
    uid = row['user_ip']
    prefix = 'anon:'
  else:
    #Written out as a stringified int, so force what we read from the
    #dataframe to the same format. Otherwise the keys will not match.
    uid = str(int(uid))
    prefix = 'name:'

  if uid in identities:
    user_name = identities[uid]
    prefix = user_name[:5]
    pseudonym = user_name[5:]
  else:
    pseudonym = random_name()
    identities[uid] = f'{prefix}{pseudonym}'
    user_name = identities[uid]

  if prefix == 'name:':
    return [user_name, pseudonym, '']
  elif prefix == 'anon:':
    return [user_name, '', pseudonym]
  else:
    raise Exception(f'{prefix} {user_name} {pseudonym}')

def expand_json(df, json_column, json_fields, prefix, json_parser = json.loads):
  def check_metadata(row):
    #Check that key in original JSON matches what is in the column -- but case-insensitively
    #Also confirms that all of the expected metadata is actually in there
    #Assume that '.' is a path separator

    #Return a copy of a dict with all keys lower-cased
    #Dictionaries are deep copied, but any other data structures contained in the dictionary are shallow-copied
    #We only mutate the keys, so the original structure inside the DataFrame is unchanged
    def lc_dict(d):
      d = d.copy()
      keys = list(d.keys())
      for k in keys:
        lk = k.lower()
        if k != lk:
          if lk in d:
            raise Exception('Key collision when normalising JSON in DataFrame to lowercase')
          d[lk] = d.pop(k)
        if isinstance(d[lk], dict):
          d[lk] = lc_dict(d[lk])
      return d

    normalized_json = lc_dict(row[json_column]) #The original JSON as a dict, but with the keys lower-cased
    for path in json_fields:
      d = normalized_json
      for k in [x.lower() for x in path.split('.')]:
        if not k in d:
          if k == '#priority':
            if 'priority' in d: #Accept (but warn about) use of priority for #priority
              print(f'Allowing priority instead of #priority for subject {row.subject_ids}', file = sys.stderr)
              d = None
              break
              #In all other cases, I'll get an exception, which'll make me aware of another metadata anomaly to handle
        d = d[k]
        if d is None:
          break

      def errstring():
        return (f'For path "{path}", the following should match:\n'
                f'"{d}" in JSON at col "{json_column}"\n'
                f'"{row[path]}" in col "{path}"')
      if d is None:
        if not np.isnan(row[path]):
          raise Exception(errstring())
      else:
        if d != row[path]:
          raise Exception(errstring())

  df[json_column] = df[json_column].apply(json_parser)
  jn = pd.json_normalize(df[json_column].tolist())#, meta = json_fields)[json_fields]

  #Handle the JSON having been treated as case-insensitive
  for json_field in json_fields:
    lower_field = json_field.lower()
    insensitive_count = Counter([x.lower() for x in jn.columns])[lower_field]
    if insensitive_count == 1:
      continue
    if insensitive_count != 2:
      raise Exception(f'{lower_field}: {insensitive_count}') #Only wrote code to handle lowercase + one other version

    #Check that the nulls line up consistently with this being the same field with inconsistent case in name
    if jn[[json_field, lower_field]].isnull().sum(axis = 1).ne(1).any():
      raise Exception('Apparent multicased JSON field does not align: some rows have values in both or neither spelling of the field.')
    print(f'Fixing up apparent use of both {json_field} and {lower_field}', file = sys.stderr)

    jn[lower_field] = jn[lower_field].combine_first(jn[json_field])
    jn = jn.drop(json_field, axis = 1)
    assert not jn[lower_field].isnull().any(), jn[jn[lower_field].isnull()][lower_field]
  jn = jn.rename({x: x.lower() for x in json_fields}, axis = 1)
  json_fields =     [x.lower() for x in json_fields]

  for x in json_fields:
    if x in df.columns:
      raise Exception(f'JSON field {x!r} already exists in dataframe columns')

  df = df.join(jn[json_fields])
  df.apply(check_metadata, axis = 'columns') #Check that the metadata looks right -- has caught real problems at least once
  df = df.rename(columns = {x: f'{prefix}.{x}' for x in json_fields})
  df = df.drop(json_column, axis = 'columns')
  return df

#Read workflow's CSV file into a dataframe and do workflow-specific transformations
def read_workflow(workflow):
  print(workflow, WORKFLOW_NAMES[workflow])
  csv_file = f'{args.exports}/{WORKFLOW_NAMES[workflow]}-classifications.csv'
  df = pd.read_csv(csv_file)
  if not len(df.workflow_id.unique()) == 1:
    raise Exception(f'Too many workflow ids in {csv_file}')
  if df.workflow_id.iloc[0] != workflow:
    raise Exception(f'Expected workflow id {workflow} in CSV file {csv_file}. Got {df.workflow_id.iloc[0]}.')

  minimal_pseudonyms[workflow] = df.copy() #Store the original classification

  df = df[df['workflow_version'].isin(WORKFLOW_KEEPERS[workflow])]
  df = df.reset_index(drop = True) #Reset the index so that we line up with the JSON expansion

  df['START'] = WORKFLOW_STARTSTAMP[workflow]
  df['START'] = df['START'].astype(np.datetime64)

  #Pull interesting bits of subject info out into their own fields
  def parse_subj_info(cell):
    subj_info = json.loads(cell)

    #Make sure that the data is shaped as we expect
    if len(subj_info) != 1:
      if len(subj_info > 1):
        raise Exception(f'Encountered subject info for multiple subject ids: {subj_info.keys()}')
      else: #0-length dictionary
        raise Exception('Missing subject info')

    #Remove the single top-level key (which is the subject id) and just return the info about this subject
    #(See https://www.geeksforgeeks.org/python-get-the-first-key-in-dictionary/ for the next iter trick)
    return subj_info[next(iter(subj_info))] 
  df = expand_json(df, 'subject_data', ALL_SUBJECT_KEEPERS + WORKFLOW_SUBJECT_KEEPERS[workflow], 'subj', parse_subj_info)

  #Special handling for attendance vs minutes pages in S&B meetings workflow
  if workflow == 18504:
    attendance_subjects = df.sort_values('subj.page')[['subj.date', 'subject_ids']].groupby(['subj.date']).first().subject_ids
    df.loc[df.subject_ids.isin(attendance_subjects), ('workflow_id', 'workflow_name')] = (1, 'attendance')

  return df

def main():
  #Read in all of the CSVs with a generator expression, as suggested here:
  #https://stackoverflow.com/a/21232849
  df = pd.concat([read_workflow(x) for x in args.workflows], ignore_index = True)

  #Pseudonymise the individual files, building pseudonyms for everyone who has ever classified as a side effect
  for v in minimal_pseudonyms.values():
    v[['user_name', 'user_id', 'user_ip']] = v[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns', result_type = 'expand')

  #Pseudonymize using the previously-generated pseuondyms, and then drop the useless field
  df['pseudonym'] = df[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns', result_type = 'expand').iloc[:,0]
  df = df.drop(['user_name', 'user_id', 'user_ip'], axis = 'columns')

  #Drop fields that we do not need at all
  df = df.drop(['gold_standard', 'expert', 'annotations'], axis = 'columns')

  #Expand out the interesting bits of the metadata, drop the rest
  df = expand_json(df, 'metadata', METADATA_KEEPERS, 'md')

  df['md.started_at'] = df['md.started_at'].astype(np.datetime64)
  df = df[df['md.started_at'] >= df['START']]
  df = df.drop('START', axis = 'columns')

  df['md.finished_at'] = df['md.finished_at'].astype(np.datetime64)
  df = df[df['md.finished_at'] < np.datetime64(STOPSTAMP)]

  df.to_csv('all_classifications.csv', index = False, date_format='%Y-%m-%dT%H:%M:%S.%fZ%z')

  with open(args.dictionary, 'w') as f:
    json.dump(identities, f, indent = 2, sort_keys = True)

  #This should be updated for STOPSTAMP, but I'm anyway not using it at the moment.
  for k, v in minimal_pseudonyms.items():
    v['KEEP'] = v['metadata'].apply(lambda x: json.loads(x)['started_at'] >= WORKFLOW_STARTSTAMP[k])
    v = v[v['KEEP']]
    v = v.drop('KEEP', axis = 'columns')
    v.to_csv(f'secrets/{WORKFLOW_NAMES[k]}-classifications.csv', index = False)

main()
