#!/usr/bin/env python3
import tempfile
import os
from shutil import copy, copy2, copytree, make_archive, ignore_patterns
from multiprocessing import Process
import filecmp
import subprocess
import sys
import csv
import util as u

os.makedirs('sharing', exist_ok = True)
with tempfile.TemporaryDirectory(dir = './secrets') as tmpdir:
  inner_dir = f'{tmpdir}/data_analysis'
  os.mkdir(inner_dir)
  copy('all_classifications.csv', inner_dir)
  copy('README_all_classifications', f'{inner_dir}/README.txt')

  #Confirm that the supplied data matches the data used for analysis, modulo expected changes
  #At time of writing, this is just that we've added a couple of subject fields in the final all_classifications -- no actual data has changed
  with open('all_classifications.csv', 'r') as infile:
    reader = csv.DictReader(infile)
    out_cols = list(filter(lambda x: x != 'subj.image' and x != 'subj.id', reader.fieldnames))
    with open(f'{tmpdir}/csv.tmp', 'x') as outfile:
      writer = csv.DictWriter(outfile, out_cols, lineterminator = '\n')
      writer.writeheader()
      for row in reader:
        del row['subj.image']
        del row['subj.id']
        writer.writerow(row)
  try:
    if not filecmp.cmp(f'{tmpdir}/csv.tmp', f'secrets/all_classifications.csv_{u.git_report_original()}', shallow = False):
      print('all_classifications.csv does not match report_original', file = sys.stderr)
      sys.exit(1)
    if not filecmp.cmp(f'{tmpdir}/csv.tmp', f'secrets/all_classifications.csv_{u.git_report_final()}', shallow = False):
      print('all_classifications.csv does not match report_final', file = sys.stderr)
      sys.exit(1)
    if not filecmp.cmp(f'secrets/requirements.txt_{u.git_report_final_deps()}', 'requirements.txt', shallow = False):
      print('requirements.txt does not match the pip deps used to generate the final reports', file = sys.stderr)
      sys.exit(1)
  except FileNotFoundError:
    print(f'''At least one comparison file is missing.

To generate these files:
git stash && git checkout report_original && ./pseudonymize.py && mv all_classifications.csv secrets/all_classifications.csv_{u.git_report_original()} && git co {u.git_HEAD()}
git stash && git checkout report_final && ./pseudonymize.py && mv all_classifications.csv secrets/all_classifications.csv_{u.git_report_final()} && git co {u.git_HEAD()}
git stash && git checkout {u.git_report_final_deps()} && cp requirements.txt secrets/requirements.txt_{u.git_report_final_deps()} && git co {u.git_HEAD()}''', file = sys.stderr)
    sys.exit(1)
  with open(f'{tmpdir}/freeze.tmp', 'x') as f:
    subprocess.run(['pip', 'freeze'], check = True, stdout = f)
  with open(f'{tmpdir}/freeze.tmp', 'r+') as f:
    deps = f.read()
    f.seek(0)
    f.write('''#Dependencies used in producing the final charts for the report
#The less accessible charts that were used in analysis may not have used the exact same dependencies
''' + deps)
  if not filecmp.cmp(f'{tmpdir}/freeze.tmp', 'requirements.txt', shallow = False):
    print('pip freeze does not match requirements.txt', file = sys.stderr)
    sys.exit(1)
  os.remove(f'{tmpdir}/csv.tmp')
  os.remove(f'{tmpdir}/freeze.tmp')

  procs = []
  for ar_format in ('zip', 'xztar'):
    p = Process(target = make_archive, args = ('sharing/data_analysis', ar_format, tmpdir))
    p.start()
    procs.append(p)
  for p in procs: p.join()
