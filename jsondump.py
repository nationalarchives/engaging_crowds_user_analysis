#!/usr/bin/env python3

import pandas as pd
import json
import os
import sys

#Read workflow's CSV file into a dataframe and do workflow-specific transformations
def read_workflow(workflow):
  df = pd.read_csv(f'exports/{workflow}-classifications.csv')

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
    return json.dumps(subj_info[next(iter(subj_info))])
  df['subject_data'] = df['subject_data'].apply(parse_subj_info)
  return df

def dump_keys(d, depth = 0):
  for key, value in d.items():
    print(f'{" " * depth * 2}{key}')
    if isinstance(value, dict):
      dump_keys(value, depth + 1)

def update_keys(c, u):
  for key, value in c.items():
    if not key in u: u[key] = {}
    if isinstance(value, dict):
      update_keys(c[key], u[key])

def main():
  #Read in all of the CSVs with a generator expression, as suggested here:
  #https://stackoverflow.com/a/21232849
  workflows = sys.argv[1:]
  if len(workflows) == 0: workflows = [x[0:-20] for x in os.listdir('exports/')]
  df = pd.concat([read_workflow(x) for x in workflows], ignore_index = True)

  for column in ('metadata', 'subject_data'):
    union = {}
    df[column].apply(lambda x: update_keys(json.loads(x), union))
    print(column.upper())
    dump_keys(union)
    print()

main()
