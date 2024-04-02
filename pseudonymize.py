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
import tempfile
import shutil
import importlib
import util
from collections import Counter

#For debugging
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#pd.set_option('display.expand_frame_repr', None)

#Dictionary storing individual CSV files minimally altered
minimal_pseudonyms = {}

def config_checks():
  def compare(comparator):
    baseline = set(config.WORKFLOW_NAMES.keys())
    comparator = set(comparator)
    assert baseline == comparator, f'Mismatch in config checks:\n{sorted(baseline)}\nvs\n{sorted(comparator)}'
  compare(config.WORKFLOW_KEEPERS.keys())
  compare(config.WORKFLOW_SUBJECT_KEEPERS.keys())
  compare(config.WORKFLOW_STARTSTAMP.keys())
  compare(config.WORKFLOW_STARTSTAMP.keys())
  all_proj_workflows = []
  for proj_workflows in config.PROJECTS.values():
    all_proj_workflows.extend(proj_workflows)
  compare(all_proj_workflows)
  assert len(set(all_proj_workflows)) == len(all_proj_workflows)
  compare(config.LABELS.keys())
  compare(config.workflow_map.keys())
  if not os.path.isfile(args.dictionary):
    with open(args.dictionary, 'w') as f: pass #confirm that we can write a file here
    os.unlink(args.dictionary)

def make_shareables(copied_df):
  for project, wids in config.PROJECTS.items():
    print(f'  {project}')
    proj_df = copied_df[copied_df.workflow_id.isin(wids)].drop('START', axis = 'columns').dropna(axis='columns', how = 'all')

    #We have to use the subjects file to get the subject set id.
    #If I understand correctly, this file is NOT synchronized with the
    #classifications and does not record historical information, but
    #rather just the membership of the subjects at the time that it was
    #generated. This means that if a subject has moved from one subject
    #set to another, or been removed from workflow, it will not appear in
    #this file.
    #So we hope that the subject files that we are working with
    #accurately describe the current subject_set for each subject.
    #If this does not hold, then we can at least get the 'raw' location of the
    #subject (location.zooniverse.plain in the below), so long as the subject id
    #is mentioned somewhere in this file.
    #If the subject id is not in the file at all then we give up. I suppose
    #that it might be possible to use a subject set id known to be associated
    #with a workflow to generate a URL for it -- but if it is not in this file,
    #it seems unlikely that that URL would be valid.
    #For some projects we can also point to file locations on the home
    #institution's site.
    #(In principle it is more efficient to compute subject locations once,
    #but we do it per-classification. This is partly because it makes for
    #simpler code -- thus easier to understand/maintain/reuse. Note also
    #that the 'location.zooniverse.project' field can legitimately
    #have different values for the same subject, depending upon which workflow
    #it was classified in and which subject set it belonged to.)
    subj_df = pd.read_csv(f'{args.exports}/{config.SUBJECTS[project]}',
                          usecols = ['subject_id', 'workflow_id', 'subject_set_id', 'locations'])
    subj_sets = subj_df.set_index(['subject_id', 'workflow_id']).subject_set_id
    subj_locs = subj_df.set_index('subject_id').locations
    if project in config.LOCATION_FIXUPS:
      config.LOCATION_FIXUPS[project](proj_df)

    #This function is only needed to get the 'project' location
    def get_subject_set_id(row):
      subj_set = None
      try:
        subj_set = subj_sets.loc[(row['subject_ids'], row['workflow_id'])]
      except KeyError:
        print(f'No subjects file entry for subject {row.subject_ids} with workflow {row.workflow_id}', file = sys.stderr)
        return f"<MISSING SUBJECT SET ID>"
      if not isinstance(subj_set, np.int64):
        #This constraint might not hold for other projects, but I expect it to be true
        #across the Engaging Crowds family. If it breaks down then the code will need modification
        #to handle a single subject in multiple subject sets -- whether this is caused by that
        #currently being the case, or by the file choosing to keep an entry for each subject_id that
        #a subject set has ever belonged to (if, indeed, it is allowed to do that)
        raise Exception('Expected single integer value for subject_set_id for subject in workflow')
      return f"{config.PROJECT_URLS[project]}classify/workflow/{row['workflow_id']}/subject-set/{subj_set}/subject/{row['subject_ids']}"
    proj_df['location.zooniverse.project'] = proj_df.apply(get_subject_set_id, axis = 1)

    #This function is only needed to get the 'raw' location
    def parse_subj_loc(sid):
      if not sid in subj_locs:
        print(f'No subjects file entry for subject_id {sid}', file = sys.stderr)
        return '<UNLISTED SUBJECT>'
      loc = subj_locs.loc[sid]
      if isinstance(loc, pd.Series):
        loc = loc.unique() #Returns ndarray or ExtensionArray. I'm assuming len and [] work the same either way.
        if len(loc) == 1: loc = loc[0]
        else:
          #We assume that all of the locations show the same image
          print(f'Using final of multiple locations for subject {sid}', file = sys.stderr)
          loc = loc[-1]
      loc = json.loads(loc)

      #Make sure that the data is shaped as we expect
      if len(loc) != 1:
        if len(loc > 1): raise Exception(f'Encountered multiple locations for subject_id {sid} in single row')
        else: raise Exception(f'Missing location for subject_id {sid}')
      if not '0' in loc:
        raise Exception('Location missing key "0" for subject_id {sid} -- should be its only key')
      if len(loc['0'].strip()) == 0:
        print(f'Empty subjects file entry for subject_id {sid}', file = sys.stderr)
        return '<UNLISTED SUBJECT>'
      else: return loc['0']
    proj_df['location.zooniverse.plain'] = proj_df.subject_ids.apply(parse_subj_loc)
    if project in config.ZOONIVERSE_LOCATION_FIXUPS:
      config.ZOONIVERSE_LOCATION_FIXUPS[project](proj_df)

    with tempfile.TemporaryDirectory('.') as tmpdir:
      basedir = f'{tmpdir}/{util.fnam_norm(project)}_data'
      os.mkdir(basedir)
      with open(f'{basedir}/README.txt', 'w') as f:
        f.write(config.readme_blurb([project]))
      proj_df.to_csv(f'{basedir}/classifications.csv', index = False, date_format='%Y-%m-%dT%H:%M:%S.%fZ%z')
      for ar_format in ('zip', 'xztar'):
        shutil.make_archive(f'sharing/{util.fnam_norm(project)}', ar_format, tmpdir)

parser = argparse.ArgumentParser()
parser.add_argument('workflows',
                    nargs = '*',
                    type = int,
                    help = 'Workflows to pseudonymise')
parser.add_argument('--exports', '-e',
                   default = 'exports',
                   help = 'Location of exported classifications files')
parser.add_argument('--dictionary', '-d',
                    default = 'secrets/identities.json',
                    help = 'Dictionary file to record the pseudonymisation result')
parser.add_argument('--config',
                    default = 'data',
                    help = 'Python file to set the built-in configuration')
parser.add_argument('--config-checks',
                    action = argparse.BooleanOptionalAction,
                    default = True,
                    help = 'Run config checks on the config, to make sure that data structures share the same keys')
args = parser.parse_args()
config = importlib.import_module(args.config)
if args.config_checks:
  config_checks()
if len(args.workflows) == 0:
  args.workflows = list(config.WORKFLOW_NAMES.keys())
else:
  assert set(args.workflows) <= set(config.WORKFLOW_NAMES.keys()) #if workflows are given on CLI, all given workflows must be given in the config

#Validate CLI
for workflow in args.workflows:
  if not workflow in config.WORKFLOW_KEEPERS:
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

#df must have a default index -- otherwise it will not align with the output of pd.json_normalize
#json_fields must be the not-lower-case 'spelling' in cases where there are lower-case and not-lower-case spellings of the same field
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

    #At this point we know that there are two case-variants of the same name. For the rest of this code to work,
    #we need to know both 'spellings'. For now, just reqire that the passed-in name is the not-lower-case name
    #TODO: An alternative to aborting in this case would be to just figure out what the non-lowercase variant is
    if json_field == lower_field:
      raise Exception(f'json_fields argument {json_field!r} must be the non-lower-case variant')

    #Check that the nulls line up consistently with this being the same field with inconsistent case in name
    if jn[[json_field, lower_field]].isnull().sum(axis = 1).ne(1).any():
      bad = jn[[json_field, lower_field]].isnull().sum(axis = 1).ne(1)
      raise Exception(f'Apparent multicased JSON field {json_field} does not align: some rows have values in both or neither spelling of the field.\n' + str(jn[bad][[json_field, lower_field]]))
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
  print(workflow, config.WORKFLOW_NAMES[workflow])
  csv_file = f'{args.exports}/{config.WORKFLOW_NAMES[workflow]}-classifications.csv'
  df = pd.read_csv(csv_file, converters = { 'workflow_version': lambda x: str(x) })
  if not len(df.workflow_id.unique()) == 1:
    raise Exception(f'Too many workflow ids in {csv_file}')
  if df.workflow_id.iloc[0] != workflow:
    raise Exception(f'Expected workflow id {workflow} in CSV file {csv_file}. Got {df.workflow_id.iloc[0]}.')

  minimal_pseudonyms[workflow] = df.copy() #Store the original classification

  df = df[df['workflow_version'].isin(config.WORKFLOW_KEEPERS[workflow])]
  df = df.reset_index(drop = True) #Reset the index so that we line up with the JSON expansion

  df['START'] = config.WORKFLOW_STARTSTAMP[workflow]
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
  df = expand_json(df, 'subject_data', config.ALL_SUBJECT_KEEPERS + config.WORKFLOW_SUBJECT_KEEPERS[workflow], 'subj', parse_subj_info)

  return df

def main():
  #Read in all of the CSVs with a generator expression, as suggested here:
  #https://stackoverflow.com/a/21232849
  df = pd.concat([read_workflow(x) for x in args.workflows], ignore_index = True)

  print('Pseudonymising')
  #Pseudonymise the individual files, building pseudonyms for everyone who has ever classified as a side effect
  for v in minimal_pseudonyms.values():
    v[['user_name', 'user_id', 'user_ip']] = v[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns', result_type = 'expand')

  #Pseudonymize using the previously-generated pseuondyms, and then drop the useless field
  df['pseudonym'] = df[['user_name', 'user_id', 'user_ip']].apply(pseudonymize, axis = 'columns', result_type = 'expand').iloc[:,0]
  df = df.drop(['user_name', 'user_id', 'user_ip'], axis = 'columns')

  #Drop fields that we do not need at all
  df = df.drop(['gold_standard', 'expert'], axis = 'columns')

  print('Expanding metadata')
  #Expand out the interesting bits of the metadata, drop the rest
  df = expand_json(df, 'metadata', config.METADATA_KEEPERS, 'md')

  #Output data for the data sharing platform
  print('Generating per-project outputs for data sharing platform')
  os.makedirs('sharing', exist_ok = True)
  make_shareables(df.copy())

  #Output data for analysis
  #Much the same as the data sharing platform output, but everything goes into a single file and classifications outside of the relevant date range are dropped
  #And we make a fake workflow of the attendance branch of the meetings workflow
  #Important to do this *before* we drop any rows! Otherwise the first page within a date group is not necessarily an attendance page.
  #FIXME: Read in the subjects file and use that to identify the attendance pages -- this won't break if we happen to start dropping rows earlier then here.
  print('Generating all_classifications.csv for analysis')
  attendance_subjects = df[df.workflow_id == 18504].sort_values('subj.page')[['subj.date', 'subject_ids']].groupby(['subj.date']).first().subject_ids
  df.loc[df.subject_ids.isin(attendance_subjects), ('workflow_id', 'workflow_name')] = (1, 'attendance')

  df['md.started_at'] = df['md.started_at'].astype(np.datetime64)
  df = df[df['md.started_at'] >= df['START']]
  df = df.drop('START', axis = 'columns')

  df['md.finished_at'] = df['md.finished_at'].astype(np.datetime64)
  df = df[df['md.finished_at'] < np.datetime64(config.STOPSTAMP)]

  df = df.drop('annotations', axis = 'columns')

  with open('README_all_classifications', 'w') as f:
    f.write(config.readme_blurb([config.SUBJECTS.keys()]))
  df.to_csv('all_classifications.csv', index = False, date_format='%Y-%m-%dT%H:%M:%S.%fZ%z')

  #paranoia checks
  if len(identities) != len(set(identities.keys())):   raise Exception('User names in args.dictionary are not unique')
  if len(identities) != len(set(identities.values())): raise Exception('Pseudonames in args.dictionary are not unique')
  with open(args.dictionary, 'w') as f:
    json.dump(identities, f, indent = 2, sort_keys = True)

  #This should be updated for STOPSTAMP, but I'm anyway not using it at the moment.
  for k, v in minimal_pseudonyms.items():
    v['KEEP'] = v['metadata'].apply(lambda x: json.loads(x)['started_at'] >= config.WORKFLOW_STARTSTAMP[k])
    v = v[v['KEEP']]
    v = v.drop('KEEP', axis = 'columns')
    v.to_csv(f'secrets/{config.WORKFLOW_NAMES[k]}-classifications.csv', index = False)

main()
