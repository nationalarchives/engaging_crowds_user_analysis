import pandas as pd

HEAD = None

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
    'subj.botanist': str,
    'subj.group': str,
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

class_cap = {
    SB: pd.Timedelta(150, 'm'),
    HMS: pd.Timedelta(30, 'm'),
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

WORKFLOW_TYPES_BACKMAP = {}
for k, v in workflow_map.items():
  if v in WORKFLOW_TYPES_BACKMAP: WORKFLOW_TYPES_BACKMAP[v].append(k)
  else: WORKFLOW_TYPES_BACKMAP[v] = [k]

WORKFLOW_TYPES = sorted(set(workflow_map.values()))

TIME_COLS = ['created_at','md.started_at','md.finished_at','duration']

