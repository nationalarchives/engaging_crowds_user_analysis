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

#Hack -- use in combination with | sort | uniq -c to get a quick field name dump
def dump_json(cell):
  def dump_dict(d, depth = 0):
    for key, value in d.items():
      print(f'{"*"*depth}{key}')
      if isinstance(value, dict):
        dump_dict(value, depth + 1)
  dump_dict(json.loads(cell))

def pseudonymize(row):
  uid = row['user_id']
  if np.isnan(uid):
    #Anonymous user -- use the ip addr as the uid, so that all
    #classifications from the apparent-same IP addr get the same pseudonym
    uid = row['user_ip']
    prefix = 'anon'
  else:
    #Written out as a stringified int, so force what we read from the
    #dataframe to the same format. Otherwise the keys will not match.
    uid = str(int(uid))
    prefix = 'name'
  if not uid in identities:
    pseudonym = len(identities) + 1
    identities[uid] = f'{prefix}:{pseudonym}'
  return identities[uid]

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

  df = df[df['workflow_version'] >= WORKFLOW_KEEPERS[workflow]]
  df = df.reset_index(drop = True) #Reset the index so that we line up with the JSON expansion

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

  #HACK -- comment in to dump what is in the metadata, use with sort | uniq -c
  #df['metadata'].apply(dump_json)
  #df['subject_data'].apply(dump_json)

  #Pseudonymize and then drop private field(s)
  df['pseudonym'] = df[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns')
  df = df.drop(['user_name', 'user_id', 'user_ip'], axis = 'columns')

  #Drop fields that we do not need at all
  df = df.drop(['gold_standard', 'expert', 'annotations'], axis = 'columns')

  #Expand out the interesting bits of the metadata, drop the rest
  df = expand_json(df, 'metadata', METADATA_KEEPERS, 'md')

  df.to_csv('all_classifications.csv', index = False)

  with open(args.dictionary, 'w') as f:
    f.write(json.dumps(identities))

main()
