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
import data as d
import util as u
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
_RBGE_SUBJECT_KEEPERS = ['id', 'Botanist','Group','Image','Format','Species','Barcode']
WORKFLOW_SUBJECT_KEEPERS = {
  18504: ['Date', 'Page', 'Catalogue', 'image'],
  18505: ['Surnames starting with', 'image'],
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
  18504: ['132.205'],
  18505: ['56.83'],
  18611: ['3.1'],
  18612: ['3.1', '4.1'],
  18613: ['3.1'],
  18614: ['3.1'],
  18616: ['3.1'],
  18617: ['3.1'],
  18618: ['3.1'],
  18619: ['3.1'],
  18621: ['3.1'],
  18622: ['3.1'],
  18623: ['3.1'],
  18624: ['3.1', '6.4'],
  18625: ['3.1'],
  19381: ['122.201'],
  19385: ['46.223'],
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

SUBJECT_DESCRIPTIONS = {
  d.HMS: ["subj.filename                Filename of the image"],
  d.RBGE: ['subj.id                      Unique identifier for the specimen',
           'subj.botanist                The botanist who collected the specimen',
           'subj.group                   The geographical region that the specimen was collected from',
           "subj.image                   Filename of the image",
           "subj.format                  The format of the record itself (either 'herbarium sheet' or 'herbarium specimen')",
           'subj.species                 The species of the specimen',
           'subj.barcode                 Barcode used to identify the specimen',
  ],
  d.SB:['subj.date                    Date of the meeting',
        'subj.page                    Page number in the minute book',
        '''subj.catalogue               Intended catalogue reference for the transcription. Only the top two levels
                             exist in the catalogue at time of writing. The third level will be added as
                             one of the outputs from this project.''',
        "subj.image                   Filename of the image",
        'subj.surnames starting with  First letter(s) of surnames on the page',
  ],
}

LOCATION_DESCRIPTIONS = {
  d.HMS: '',
  d.RBGE: 'location.rbge                Citable location of the classified file on the RBGE website',
  d.SB:   'location.tna                 Location of the classified file in the TNA online catalogue',
}

def readme_blurb(projects):
  from os import linesep as nl
  for_all = len(projects) == len(LOCATION_DESCRIPTIONS)
  assert len(projects) == 1 or for_all
  blurb = f'''About This Data
===============

This data describes the individual classifications made by volunteers in this Zooniverse
project. It is provided as a Comma Separated Values (CSV) file. The easiest way to view the
data is to open it in standard spreadsheet software such as Excel, Numbers or Google sheets.
This will show the data as a table, with column headings at the top. These column headings
label the 'fields' making up the data. A field is a single entity in the data, such as a user
name or the time at which a classification was completed. Each row in the table gives
information about a single classification of a single record by a single volunteer.

The complete list of fields that we provide is:

classification_id            Unique identifier for the classification
workflow_id                  Unique identifier for the workflow within which the classification was made'''
  if for_all:
    blurb += """
                             ID 1 is a made-up ID number for the 'Attendance' branch for the 'Meetings' workflow in
                             'Scarlets and Blues' (see 'workflow_name', below)"""
  blurb += '''
workflow_name                The human-readable name of the workflow within which the classification was made'''
  if for_all:
    blurb += """
                             'Attendance' is the branch of the 'Meetings' workflow for dealing with the initial 'attendance and standard minutes'
                             page of a set of meeting minutes. It is treated as a separate workflow for analysis purposes."""
  blurb += f'''
workflow_version             The version of the workflow within which the classification was made
created_at                   The server-side date/time that the classification was made
annotations                  The volunteer's transcription of the record. This is a JSON structure recording the volunteer's path
                             through the whole workflow for this record. Forthcoming scripts will reconcile these transcriptions
                             into a convenient form to describe the records.
subject_ids                  Unique identifier of the subject to which the classification applied.
                             There is only ever 1 subject id per classification in the Engaging Crowds projects.
subj.#priority               Number used by the indexer to order the subjects.
subj.retired.retired_at      UTC date/time that the subject acquired enough classifications to be considered complete.
{nl.join(dict.fromkeys([line for p in projects for line in SUBJECT_DESCRIPTIONS[p]]).keys())}
pseudonym                    Pseudonym for the user who made the classification. Pseudonyms are consistent across all three projects.
                             A pseudonym beginning 'user': indicates a logged-in user. A pseudonym beginning 'anon:' indicates an
                             anonymous user, identified by a hash of their IP address. This should be treated as a much less reliable
                             identification than a user login.
md.started_at                Client-side UTC start date/time of classification
md.finished_at               Client-side UTC finish date/time of classification
md.utc_offset                Offset from client's local time to UTC (subtract utc_offset to convert to local time)
{nl.join(filter(lambda x: len(x.strip()), [LOCATION_DESCRIPTIONS[p] for p in projects]))}
location.zooniverse.project  Location of the subject in the project's index
location.zooniverse.plain    Location of the subject image on the Zooniverse servers


Alterations to the Original Data
================================

The original Zooniverse data export contains two metadata columns: record metadata, describing
the record being classified, and classification metadata, describing the act of classification.
Each row in these metadata columns contains multiple fields which we 'flatten' into
new columns. Record metadata fields are prefixed with 'subj.' Classification metadata
fields are prefixed with 'md.'

Classification metadata is provided by the Zooniverse platform. Some record metadata is
provided by the Zooniverse platform and some is provided by project administrators. We keep
all of the metadata that comes from the project administrators but discard most of the metadata
that comes from the platform. The following platform-provided metadata fields are useful for
our engagment analysis and so are kept:
  * subj.retired.retired_at
  * md.started_at
  * md.finished_at
  * md.utc_offset

Metadata field names in mixed case are all treated as being the same field, as are field names
differing only by the presence or absence of a single '#' character. Field names are all presented in
lower case in this CSV file.

All other data from the Zooniverse data export is included here, but user names have been replaced
by pseudonyms.


Information on Reuse
====================
'''
  if for_all: blurb += '''
HMS NHS
-------
'''
  if for_all or projects[0] == d.HMS:
    blurb += '''The records of the Dreadnought Seamen’s Hospital are Public Records (Crown copyright, see https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/), held by the National Maritime Museum as an official place of deposit under the terms of the Public Records Acts. The images of these records are used online by the National Maritime Museum with permission from Ancestry.

The images are made available under the terms of the CC-BY-NC-ND 4.0 licence (https://creativecommons.org/licenses/by-nc-nd/4.0/). Users can view but not download the images. Users can re-use the images for non-commercial research, education or private study only.

The data are transcriptions of Public Records, which are also covered by Crown Copyright. The data is made available under the terms of the Open Government Licence (OGL, see https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/), which is compatible with CC BY 4.0 licence (https://creativecommons.org/licenses/by/4.0/). Users can copy, publish, distribute, transmit and adapt the data for both commercial and non-commercial use.
'''
  if for_all: blurb += '''
Scarlets and Blues
------------------
'''
  if for_all or projects[0] == d.SB:
    blurb += '''(c) Images used in Scarlets and Blues are reproduced by permission of The National Archives. The National Archives does not guarantee the accuracy, completeness or fitness for the purpose of the information provided. Images may be used only for purposes of research, private study or education. Applications for any other use should be made to The National Archives Image Library at images@nationalarchives.gov.uk.

The National Archives is a government department, which means that all of the material we create is subject to Crown copyright (https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/). Data produced by volunteers is available for re-use under the terms of the Open Government Licence (OGL, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). This licence allows people to copy, publish and distribute information, as long as they acknowledge its source. It is compatible with the CC BY 4.0 Licence (https://creativecommons.org/licenses/by/4.0/)and the Open Data Commons Attribution Licence (https://opendatacommons.org/licenses/by/).
'''
  if for_all: blurb += '''
The RBGE Herbarium
------------------
'''
  if for_all or projects[0] == d.RBGE:
    blurb += '''These images are licensed according to the CC BY 4.0 licence (https://creativecommons.org/licenses/by/4.0/). This licence allows people to freely use images as long as they give appropriate credit and indicate if any changes have been made.

The data transcribed by volunteers is licensed according to the CC0 licence (https://creativecommons.org/share-your-work/public-domain/cc0). This licence means there are no copyright restrictions on this data and it can be freely reused.
'''

  blurb += '''

Citation Information
====================

'''
  if for_all or projects[0] == d.HMS:
    blurb += "Any use of the images or data from HMS NHS should credit 'National Maritime Museum' as the source."
  if for_all: blurb += nl
  if for_all or projects[0] == d.SB:
    blurb += "Any use of the images or data from Scarlets and Blues should credit 'The National Archives' as the source."
  if for_all: blurb += nl
  if for_all or projects[0] == d.RBGE:
    blurb += "Any use of the images or data from The RBGE Herbarium should credit 'Royal Botanic Garden Edinburgh' as the source."

  blurb += f'''


Reproduction
============

Reproduction of this data requires access to the original classifications, which is limited to the project team.
However, the reproduction recipe is:
* git clone https://github.com/nationalarchives/engaging_crowds_user_analysis.git
* cd engaging_crowds_user_analysis
* git checkout {u.git_HEAD()} #Optional, to use the scripts at the point when this bundle was generated
* pip install -r requirements.txt #You might prefer to do this in a virtualenv
* (Download the original project export files from the relevant Engaging Crowds project(s) to engaging_crowds_user_analysis/exports/)
* ./pseudonymise.py

'''

  if for_all:
    blurb += '''The output will appear as all_classifications.csv and README_all_classifications. To bundle it into a .zip or a
.tar.xz file, run ./share_analysis.py and follow the instructions that it gives you.'''
  else:
    blurb += '''The output will appear in the sharing/ directory.

Note that the generated output might not be exactly identical to the files on the website. This is because changes in the
uploaded subjects can mean that URLs giving the location of the original subject can appear and disappear (and perhaps even
be incorrect).'''

  blurb += '''

Pseudonyms are randomly generated so will differ from run to run. They are unique per user-id.
'''

  if for_all:
    blurb += f'''
To generate the charts:
* git clone https://github.com/nationalarchives/engaging_crowds_user_analysis.git
* cp <all_classifications.csv from this bundle> engaging_crowds_user_analysis/
* cd engaging_crowds_user_analysis
* pip install -r requirements.txt  #You might prefer to do this in a virtualenv
* ./analyze.py

Graphs appear in engaging_crowds_user_analysis/secrets/graphs/.

Two sets of charts were generated in producing the report.

The first set, produced by the commit tagged report_original, were used in the analysis described in the text of the report.

The second set, produced by the commit tagged report_final, are the charts actually printed in the report. These versions of the charts have improved accessibility in some respects.

To regenerate either set of charts using in producing the report, check out the appropriate tag before running ./analyse.py. For example:
git checkout report_final

The pip dependencies must be installed before the checkout is changed. This is because requirements.txt was commited at a later time.
requirements.txt matches the dependencies used to generate both the final charts for the report and the contents of this bundle.
The dependencies used for the analysis are lost but should at least be similar.

The all_classifications.csv produced in this bundle is identical to the all_classifications.csv used for the reports, except that it has gained the subj.image and subj.id columns.
'''

  blurb += f'''

This bundle generated from git state {u.git_condition()}
'''

  return blurb

def make_shareables(copied_df):
  for project, wids in d.PROJECTS.items():
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
    subj_df = pd.read_csv(f'exports/{d.SUBJECTS[project]}',
                          usecols = ['subject_id', 'workflow_id', 'subject_set_id', 'locations'])
    subj_sets = subj_df.set_index(['subject_id', 'workflow_id']).subject_set_id
    subj_locs = subj_df.set_index('subject_id').locations
    if project == d.RBGE: proj_df['location.rbge'] = 'https://data.rbge.org.uk/herb/' + proj_df['subj.barcode']
    elif project == d.SB: proj_df['location.tna'] = 'https://discovery.nationalarchives.gov.uk/details/r/C' + \
                          proj_df['subj.image'].apply(lambda x: str(int(x.split('_')[2]) - 433 + 170195))

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
      return f"{d.PROJECT_URLS[project]}classify/workflow/{row['workflow_id']}/subject-set/{subj_set}/subject/{row['subject_ids']}"
    proj_df['location.zooniverse.project'] = proj_df.apply(get_subject_set_id, axis = 1)

    #This function is only needed to get the 'raw' location
    def parse_subj_loc(sid):
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
        print(f'No subjects file entry for subject_id {sid}', file = sys.stderr)
        return '<UNLISTED SUBJECT>'
      else: return loc['0']
    proj_df['location.zooniverse.plain'] = proj_df.subject_ids.apply(parse_subj_loc)
    if project == d.SB:
      proj_df['location.zooniverse.plain'] = 'https://tanc-ahrc.github.io/EngagingCrowds/galleries/terms_wrapper.html?img=' + proj_df['location.zooniverse.plain']

    with tempfile.TemporaryDirectory('.') as tmpdir:
      basedir = f'{tmpdir}/{u.fnam_norm(project)}_data'
      os.mkdir(basedir)
      with open(f'{basedir}/README.txt', 'w') as f:
        f.write(readme_blurb([project]))
      proj_df.to_csv(f'{basedir}/classifications.csv', index = False, date_format='%Y-%m-%dT%H:%M:%S.%fZ%z')
      for ar_format in ('zip', 'xztar'):
        shutil.make_archive(f'sharing/{u.fnam_norm(project)}', ar_format, tmpdir)

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
  print(workflow, WORKFLOW_NAMES[workflow])
  csv_file = f'{args.exports}/{WORKFLOW_NAMES[workflow]}-classifications.csv'
  df = pd.read_csv(csv_file, converters = { 'workflow_version': lambda x: str(x) })
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
  df = expand_json(df, 'metadata', METADATA_KEEPERS, 'md')

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
  df = df[df['md.finished_at'] < np.datetime64(STOPSTAMP)]

  df = df.drop('annotations', axis = 'columns')

  with open('README_all_classifications', 'w') as f:
    f.write(readme_blurb([d.SB, d.HMS, d.RBGE]))
  df.to_csv('all_classifications.csv', index = False, date_format='%Y-%m-%dT%H:%M:%S.%fZ%z')

  #paranoia checks
  if len(identities) != len(set(identities.keys())):   raise Exception('User names in args.dictionary are not unique')
  if len(identities) != len(set(identities.values())): raise Exception('Pseudonames in args.dictionary are not unique')
  with open(args.dictionary, 'w') as f:
    json.dump(identities, f, indent = 2, sort_keys = True)

  #This should be updated for STOPSTAMP, but I'm anyway not using it at the moment.
  for k, v in minimal_pseudonyms.items():
    v['KEEP'] = v['metadata'].apply(lambda x: json.loads(x)['started_at'] >= WORKFLOW_STARTSTAMP[k])
    v = v[v['KEEP']]
    v = v.drop('KEEP', axis = 'columns')
    v.to_csv(f'secrets/{WORKFLOW_NAMES[k]}-classifications.csv', index = False)

main()
