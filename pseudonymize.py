#!/usr/bin/env python3

import pandas as pd
import numpy as np
import csv
import argparse
import json
import os

#For debugging
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#pd.set_option('display.expand_frame_repr', None)

#Dictionary storing individual CSV files minimally altered
minimal_pseudonyms = {}

#Nested JSON data to keep (sits insides cells, will be expanded out to columns)
METADATA_KEEPERS = ['started_at', 'finished_at']
ALL_SUBJECT_KEEPERS = ['#priority', 'retired.retired_at']
_HMS_NHS_SUBJECT_KEEPERS = ['Filename']
WORKFLOW_SUBJECT_KEEPERS = {
  'meetings':                                               ['Date', 'Page', 'Catalogue'],
  'people':                                                    ['Surnames starting with'],
  '1-admission-number':                                          _HMS_NHS_SUBJECT_KEEPERS,
  '2-date-of-entry':                                             _HMS_NHS_SUBJECT_KEEPERS,
  '3-name':                                                      _HMS_NHS_SUBJECT_KEEPERS,
  '4-quality':                                                   _HMS_NHS_SUBJECT_KEEPERS,
  '5-age':                                                       _HMS_NHS_SUBJECT_KEEPERS,
  '6-place-of-birth':                                            _HMS_NHS_SUBJECT_KEEPERS,
  '7-port-sailed-out-of':                                        _HMS_NHS_SUBJECT_KEEPERS,
  '8-years-at-sea':                                              _HMS_NHS_SUBJECT_KEEPERS,
  '9-last-services':                                             _HMS_NHS_SUBJECT_KEEPERS,
  '10-under-what-circumstances-admitted-or-nature-of-complaint': _HMS_NHS_SUBJECT_KEEPERS,
  '11-date-of-discharge':                                        _HMS_NHS_SUBJECT_KEEPERS,
  '12-how-disposed-of':                                          _HMS_NHS_SUBJECT_KEEPERS,
  '13-number-of-days-victualled':                                _HMS_NHS_SUBJECT_KEEPERS,
}

#Workflow version to keep (will remove rows where the workflow with name 'key' has version less than 'value')
WORKFLOW_KEEPERS = {
  'meetings': 132.205,
  'people': 56.83,
  '1-admission-number': 3.1,
  '2-date-of-entry': 3.1,
  '3-name': 3.1,
  '4-quality': 3.1,
  '5-age': 3.1,
  '6-place-of-birth': 3.1,
  '7-port-sailed-out-of': 3.1,
  '8-years-at-sea': 3.1,
  '9-last-services': 3.1,
  '10-under-what-circumstances-admitted-or-nature-of-complaint': 3.1,
  '11-date-of-discharge': 3.1,
  '12-how-disposed-of': 3.1,
  '13-number-of-days-victualled': 3.1,
}

#Based on displayed timestamp in the emails as I received them
HMS_NHS_LAUNCH_EMAIL_STAMP = '2021-06-29T16:19:00.000000Z'
SB_LAUNCH_EMAIL_STAMP = '2021-11-16T17:30:00.000000Z'
WORKFLOW_STARTSTAMP = {
  'meetings': SB_LAUNCH_EMAIL_STAMP,
  'people': SB_LAUNCH_EMAIL_STAMP,
  '1-admission-number': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '2-date-of-entry': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '3-name': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '4-quality': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '5-age': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '6-place-of-birth': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '7-port-sailed-out-of': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '8-years-at-sea': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '9-last-services': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '10-under-what-circumstances-admitted-or-nature-of-complaint': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '11-date-of-discharge': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '12-how-disposed-of': HMS_NHS_LAUNCH_EMAIL_STAMP,
  '13-number-of-days-victualled': HMS_NHS_LAUNCH_EMAIL_STAMP,
}

parser = argparse.ArgumentParser()
parser.add_argument('workflows',
                    nargs = '*',
                    default = WORKFLOW_KEEPERS.keys(),
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
    assert len(identities) == len(set(identities.keys())), 'User names in args.dictionary are not unique'
    assert len(identities) == len(set(identities.values())), 'Pseudonames in args.dictionary are not unique'
else:
  identities = {}

def pseudonymize(row):
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
    pseudonym = len(identities) + 1
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
    #Check that key in original JSON matches what is in the column
    #Assume that '.' is a path separator
    for path in json_fields:
      d = row[json_column]
      for k in path.split('.'):
        d = d[k]
        if d is None:
          break

      def errstring():
        return (f'For path "{path}", the following should match:\n'
                f'"{d}" in JSON at col "{json_column}"\n'
                f'"{row[path]}" in col "{path}"')
      if d is None: assert np.isnan(row[path]), errstring()
      else:         assert d == row[path], errstring()

  df[json_column] = df[json_column].apply(json_parser)
  jn = pd.json_normalize(df[json_column], meta = json_fields)[json_fields]
  df = df.join(jn)
  df.apply(check_metadata, axis = 'columns') #Just a paranoia check that I am combining the dataframes correctly
  df = df.rename(columns = {x: f'{prefix}.{x}' for x in json_fields})
  df = df.drop(json_column, axis = 'columns')
  return df

#Read workflow's CSV file into a dataframe and do workflow-specific transformations
def read_workflow(workflow):
  df = pd.read_csv(f'{args.exports}/{workflow}-classifications.csv')

  minimal_pseudonyms[workflow] = df #Store the original classification

  df = df[df['workflow_version'] >= WORKFLOW_KEEPERS[workflow]]
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
  return df

def main():
  #Read in all of the CSVs with a generator expression, as suggested here:
  #https://stackoverflow.com/a/21232849
  df = pd.concat([read_workflow(x) for x in args.workflows], ignore_index = True)

  #Pseudonymise the individual files, building pseudonyms for everyone who has ever classified as a side effect
  for k, v in minimal_pseudonyms.items():
    v[['user_name', 'user_id', 'user_ip']] = v[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns', result_type = 'expand')

  #Pseudonymize using the previously-generated pseuondyms, and then drop the useless field
  df['pseudonym'] = df[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns', result_type = 'expand')[0]
  df = df.drop(['user_name', 'user_id', 'user_ip'], axis = 'columns')

  #Drop fields that we do not need at all
  df = df.drop(['gold_standard', 'expert', 'annotations'], axis = 'columns')

  #Expand out the interesting bits of the metadata, drop the rest
  df = expand_json(df, 'metadata', METADATA_KEEPERS, 'md')

  df['md.started_at'] = df['md.started_at'].astype(np.datetime64)
  df = df[df['md.started_at'] >= df['START']]
  df = df.drop('START', axis = 'columns')

  df.to_csv('all_classifications.csv', index = False, date_format='%Y-%m-%dT%H:%M:%S.%fZ%z')

  with open(args.dictionary, 'w') as f:
    f.write(json.dumps(identities))

  for k, v in minimal_pseudonyms.items():
    v.to_csv(f'secrets/{k}-classifications.csv', index = False)

main()
