HEAD = None

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

SB = 'Scarlets & Blues'
HMS = 'HMS NHS'
RBGE = 'RBGE Herbarium'
SUBJECTS = {
  SB: 'scarlets-and-blues-subjects.csv',
  HMS: 'hms-nhs-the-nautical-health-service-subjects.csv',
  RBGE: 'the-rbge-herbarium-exploring-gesneriaceae-the-african-violet-family-subjects.csv',
}
PROJECTS = {
    SB: [
        1,     #Attendance pseudo-workflow
        18504, #"Meetings",
        18505, #"People",
    ],
    HMS: [
        18611, #"1. 'ADMISSION NUMBER'",
        18612, #"2. 'DATE OF ENTRY'",
        18613, #"3. 'NAME'",
        18614, #"4. 'QUALITY'",
        18616, #"5. 'AGE'",
        18617, #"6. 'PLACE OF BIRTH' ",
        18618, #"7. 'PORT SAILED OUT OF'",
        18619, #"8.'YEARS AT SEA'",
        18621, #"9. 'LAST SERVICES'",
        18622, #"10. UNDER WHAT CIRCUMSTANCES ADMITTED (or NATURE OF COMPLAINT)",
        18623, #"11. 'DATE OF DISCHARGE'",
        18624, #"12. 'HOW DISPOSED OF'",
        18625, #"13. 'NUMBER OF DAYS VICTUALLED'",
    ],
    RBGE: [
        19381, #"Geography",
        19385, #"Latitude/Longitude",
    ]
}
LABELS = {
      1: 'Attendance',
  18504: 'Minutes',
  18505: 'People',
  18611: '01. Admission Number',
  18612: '02. Date of Entry',
  18613: '03. Name',
  18614: '04. Quality',
  18616: '05. Age',
  18617: '06. Place of Birth',
  18618: '07. Port Sailed Out Of',
  18619: '08. Years At Sea',
  18621: '09. Last Services',
  18622: '10. Nature of Complaint',
  18623: '11. Date of Discharge',
  18624: '12. How Disposed Of',
  18625: '13. Days Victualled',
  19381: 'Geography',
  19385: 'Latitude/Longitude',
}

workflow_map = {
  1:     'trans-dropdown',
  18504: 'trans-page',
  18505: 'trans-row',
  18611: 'col-num',
  18612: 'col-date',
  18613: 'col-noun',
  18614: 'col-dropdown',
  18616: 'col-num',
  18617: 'col-noun',
  18618: 'col-noun',
  18619: 'col-num',
  18621: 'col-noun',
  18622: 'col-noun',
  18623: 'col-date',
  18624: 'col-dropdown',
  18625: 'col-num',
  19381: 'trans-noun', #Reading place names off a label
  19385: 'trans-num'   #Reading numbers (lat/long) off a label
}

PROJECT_URLS = {
  SB:   'https://www.zooniverse.org/projects/bogden/scarlets-and-blues/',
  HMS:  'https://www.zooniverse.org/projects/msalmon/hms-nhs-the-nautical-health-service/',
  RBGE: 'https://www.zooniverse.org/projects/emhaston/the-rbge-herbarium-exploring-gesneriaceae-the-african-violet-family/',
}

WORKFLOW_TYPES_BACKMAP = {}
for k, v in workflow_map.items():
  if v in WORKFLOW_TYPES_BACKMAP: WORKFLOW_TYPES_BACKMAP[v].append(k)
  else: WORKFLOW_TYPES_BACKMAP[v] = [k]

WORKFLOW_TYPES = sorted(set(workflow_map.values()))

TIME_COLS = ['created_at','md.started_at','md.finished_at','duration']

SUBJECT_DESCRIPTIONS = {
  HMS: ["subj.filename                Filename of the image"],
  RBGE: ['subj.id                      Unique identifier for the specimen',
           'subj.botanist                The botanist who collected the specimen',
           'subj.group                   The geographical region that the specimen was collected from',
           "subj.image                   Filename of the image",
           "subj.format                  The format of the record itself (either 'herbarium sheet' or 'herbarium specimen')",
           'subj.species                 The species of the specimen',
           'subj.barcode                 Barcode used to identify the specimen',
  ],
  SB:['subj.date                    Date of the meeting',
        'subj.page                    Page number in the minute book',
        '''subj.catalogue               Intended catalogue reference for the transcription. Only the top two levels
                             exist in the catalogue at time of writing. The third level will be added as
                             one of the outputs from this project.''',
        "subj.image                   Filename of the image",
        'subj.surnames starting with  First letter(s) of surnames on the page',
  ],
}

LOCATION_DESCRIPTIONS = {
  HMS: '',
  RBGE: 'location.rbge                Citable location of the classified file on the RBGE website',
  SB:   'location.tna                 Location of the classified file in the TNA online catalogue',
}

def _RBGE_LOCATION_FIXUP(df):
  df['location.rbge'] = 'https://data.rbge.org.ul/herb/' + df['subj.barcode']

def _SB_LOCATION_FIXUP(df):
  df['location.tna'] = 'https://discovery.nationalarchives.gov.uk/details/r/C' + df['subj.image'].apply(lambda x: str(int(x.split('_')[2]) - 433 + 170195))

LOCATION_FIXUPS = {
  RBGE: _RBGE_LOCATION_FIXUP,
  SB:   _SB_LOCATION_FIXUP,
}

def _SB_ZOONIVERSE_LOCATION_FIXUP(df):
  df['location.zooniverse.plain'] = 'https://tanc-ahrc.github.io/EngagingCrowds/galleries/terms_wrapper.html?img=' + df['location.zooniverse.plain']

ZOONIVERSE_LOCATION_FIXUPS = {
  SB: _SB_ZOONIVERSE_LOCATION_FIXUP
}

def readme_blurb(projects):
  import util
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
    'subj.page': 'UInt64',
    'subj.catalogue': str, #'category',
    'subj.surnames starting with': str,#'category',
    'subj.filename': str,
    'subj.id': str,
    'subj.botanist': str,
    'subj.group': str,
    'subj.image': str,
    'subj.format': str,
    'subj.species': str,
    'subj.barcode': str,
    'pseudonym': str,#'category',
    'md.utc_offset': int #TODO: Best choice?
}

dates = [
    'created_at',
    'subj.retired.retired_at',
    'subj.date',
    'md.started_at',
    'md.finished_at',
]

