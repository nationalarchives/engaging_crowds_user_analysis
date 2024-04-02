import util
from os import linesep as nl

HEAD = None

WORKFLOW_NAMES = {
  18611: '1-admission-number',
  18612: '2-date-of-entry',
  18613: '3-name',
  18454: '4-quality',
  18616: '5-age',
  18344: '6-creed',
  18617: '7-place-of-birth-nationality',
  18621: '8-ship-ship-or-place-of-employment-last-ship',
  18347: '9-of-what-port-port-of-registration',
  18618: '10-where-from',
  18622: '11-nature-of-complaint',
  18623: '12-date-of-discharge',
  20285: '13-how-disposed-of',
  18625: '14-number-of-days-in-hospital',
}

WORKFLOW_KEEPERS = {
  18611: ['3.1', '58.65', '58.132'],
  18612: ['47.30', '47.47'],
  18613: ['23.19', '23.34'],
  18454: ['19.70', '21.70'],
  18616: ['25.36', '25.51'],
  18344: ['26.117', '28.117'],
  18617: ['22.46'],
  18621: ['22.49'],
  18347: ['24.49', '26.49'],
  18618: ['21.44', '21.45'],
  18622: ['21.55', '21.68'],
  18623: ['29.41', '33.43'],
  20285: ['22.79', '23.82'],
  18625: ['30.47'],
}

#Nested JSON data to keep (sits insides cells, will be expanded out to columns)
METADATA_KEEPERS = ['started_at', 'finished_at', 'utc_offset']
ALL_SUBJECT_KEEPERS = ['#priority', 'retired.retired_at']

WORKFLOW_SUBJECT_KEEPERS = {
  18611: ['Filename'],
  18612: ['Filename'],
  18613: ['Filename'],
  18454: ['Filename'],
  18616: ['Filename'],
  18344: ['Filename'],
  18617: ['Filename'],
  18621: ['Filename'],
  18347: ['Filename'],
  18618: ['Filename'],
  18622: ['Filename'],
  18623: ['Filename'],
  20285: ['Filename'],
  18625: ['Filename'],
}

#I believe that STARTSTAMP is only used when generating the "user behaviour" classifications, i.e. not for the individual project data dumps
#'2022-02-01T00:00:00.000000' #Might be a better STARTSTAMP
_HMS_NHS_STARTSTAMP='2021-06-29T16:19:00.000000Z' #STARTSTAMP for phase 1
WORKFLOW_STARTSTAMP = {
  18611: _HMS_NHS_STARTSTAMP,
  18612: _HMS_NHS_STARTSTAMP,
  18613: _HMS_NHS_STARTSTAMP,
  18454: _HMS_NHS_STARTSTAMP,
  18616: _HMS_NHS_STARTSTAMP,
  18344: _HMS_NHS_STARTSTAMP,
  18617: _HMS_NHS_STARTSTAMP,
  18621: _HMS_NHS_STARTSTAMP,
  18347: _HMS_NHS_STARTSTAMP,
  18618: _HMS_NHS_STARTSTAMP,
  18622: _HMS_NHS_STARTSTAMP,
  18623: _HMS_NHS_STARTSTAMP,
  20285: _HMS_NHS_STARTSTAMP,
  18625: _HMS_NHS_STARTSTAMP,
}

STOPSTAMP = '2024-01-01T00:00:00.000000'

HMS = 'HMS NHS'
SUBJECTS = {
  HMS: 'hms-nhs-the-nautical-health-service-subjects.csv',
}
PROJECTS = {
    HMS: [
        18611,
        18612,
        18613,
        18454,
        18616,
        18344,
        18617,
        18621,
        18347,
        18618,
        18622,
        18623,
        20285,
        18625,
    ],
}
LABELS = {
  18611: '01. Admission Number',
  18612: '02. Date of Entry',
  18613: '03. Name',
  18454: '04. Quality',
  18616: '05. Age',
  18344: '06. Creed',
  18617: '07. Place of Birth/Nationality',
  18621: '08. Ship/Ship or Place of Employment/Last Ship',
  18347: '09. Of What Port/Port of Registration',
  18618: '10. Where From',
  18622: '11. Nature of Complaint',
  18623: '12. Date of Discharge',
  20285: '13. How Disposed Of',
  18625: '14. Number of Days in Hospital',
}

workflow_map = {
  18611: 'col-num',
  18612: 'col-date',
  18613: 'col-noun',
  18454: 'col-dropdown',
  18616: 'col-num',
  18344: 'col-noun',
  18617: 'col-noun',
  18621: 'col-noun',
  18347: 'col-noun',
  18618: 'col-noun',
  18622: 'col-noun',
  18623: 'col-date',
  20285: 'col-noun',
  18625: 'col-num',
}

PROJECT_URLS = {
  HMS:  'https://www.zooniverse.org/projects/msalmon/hms-nhs-the-nautical-health-service/',
}

WORKFLOW_TYPES_BACKMAP = {}
for k, v in workflow_map.items():
  if v in WORKFLOW_TYPES_BACKMAP: WORKFLOW_TYPES_BACKMAP[v].append(k)
  else: WORKFLOW_TYPES_BACKMAP[v] = [k]

WORKFLOW_TYPES = sorted(set(workflow_map.values()))

TIME_COLS = ['created_at','md.started_at','md.finished_at','duration']

SUBJECT_DESCRIPTIONS = {
  HMS: ["subj.filename                Filename of the image"],
}

LOCATION_DESCRIPTIONS = {
  HMS: '',
}

LOCATION_FIXUPS = {}
ZOONIVERSE_LOCATION_FIXUPS = {}

def readme_blurb(projects):
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
  if for_all or projects[0] == HMS:
    blurb += '''The records of the Dreadnought Seamen’s Hospital are Public Records (Crown copyright, see https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/), held by the National Maritime Museum as an official place of deposit under the terms of the Public Records Acts. The images of these records are used online by the National Maritime Museum with permission from Ancestry.

The images are made available under the terms of the CC-BY-NC-ND 4.0 licence (https://creativecommons.org/licenses/by-nc-nd/4.0/). Users can view but not download the images. Users can re-use the images for non-commercial research, education or private study only.

The data are transcriptions of Public Records, which are also covered by Crown Copyright. The data is made available under the terms of the Open Government Licence (OGL, see https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/), which is compatible with CC BY 4.0 licence (https://creativecommons.org/licenses/by/4.0/). Users can copy, publish, distribute, transmit and adapt the data for both commercial and non-commercial use.
'''
  if for_all: blurb += '''
Scarlets and Blues
------------------
'''
  if for_all or projects[0] == SB:
    blurb += '''(c) Images used in Scarlets and Blues are reproduced by permission of The National Archives. The National Archives does not guarantee the accuracy, completeness or fitness for the purpose of the information provided. Images may be used only for purposes of research, private study or education. Applications for any other use should be made to The National Archives Image Library at images@nationalarchives.gov.uk.

The National Archives is a government department, which means that all of the material we create is subject to Crown copyright (https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/). Data produced by volunteers is available for re-use under the terms of the Open Government Licence (OGL, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). This licence allows people to copy, publish and distribute information, as long as they acknowledge its source. It is compatible with the CC BY 4.0 Licence (https://creativecommons.org/licenses/by/4.0/)and the Open Data Commons Attribution Licence (https://opendatacommons.org/licenses/by/).
'''
  if for_all: blurb += '''
The RBGE Herbarium
------------------
'''
  if for_all or projects[0] == RBGE:
    blurb += '''These images are licensed according to the CC BY 4.0 licence (https://creativecommons.org/licenses/by/4.0/). This licence allows people to freely use images as long as they give appropriate credit and indicate if any changes have been made.

The data transcribed by volunteers is licensed according to the CC0 licence (https://creativecommons.org/share-your-work/public-domain/cc0). This licence means there are no copyright restrictions on this data and it can be freely reused.
'''

  blurb += '''

Citation Information
====================

'''
  if for_all or projects[0] == HMS:
    blurb += "Any use of the images or data from HMS NHS should credit 'National Maritime Museum' as the source."
  if for_all: blurb += nl
  if for_all or projects[0] == SB:
    blurb += "Any use of the images or data from Scarlets and Blues should credit 'The National Archives' as the source."
  if for_all: blurb += nl
  if for_all or projects[0] == RBGE:
    blurb += "Any use of the images or data from The RBGE Herbarium should credit 'Royal Botanic Garden Edinburgh' as the source."

  blurb += f'''


Reproduction
============

Reproduction of this data requires access to the original classifications, which is limited to the project team.
However, the reproduction recipe is:
* git clone https://github.com/nationalarchives/engaging_crowds_user_analysis.git
* cd engaging_crowds_user_analysis
* git checkout {util.git_HEAD()} #Optional, to use the scripts at the point when this bundle was generated
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

This bundle generated from git state {util.git_condition()}
'''

  return blurb

#Opted to go with 'str' over 'category' -- while category seems to make sense in many cases, it sometimes behaves
#in confusingly different ways (e.g. seemingly not respecting filters). While this surely all makes sense given
#full understanding of the model, I'll keep it simple and use str.
dtypes = {
    'classification_id': int,
    'workflow_id': int, #Not many of these... a category would be more memory-efficient, but direct compare to int might be more CPU efficient and is certainly more convenient
    'workflow_name': str, #'category',
    'workflow_version': float,
    'subject_ids': int,
    'subj.#priority': 'UInt64', #was an int, but the misspelling of this field in some workflows currently means that it is sometimes empty
    'subj.filename': str,
    'pseudonym': str,#'category',
    'md.utc_offset': int #TODO: Best choice?
}

dates = [
    'created_at',
    'subj.retired.retired_at',
    'md.started_at',
    'md.finished_at',
]
