#!/usr/bin/env python3
import tempfile
import os
from shutil import copy, copy2, copytree, make_archive, ignore_patterns
from multiprocessing import Process
import util as u

os.makedirs('sharing', exist_ok = True)
with tempfile.TemporaryDirectory(dir = '.') as tmpdir:
  inner_dir = f'{tmpdir}/data_analysis'
  os.mkdir(inner_dir)
  copy('all_classifications.csv', inner_dir)
  copy('README_all_classifications', f'{inner_dir}/README.txt')

  copytree(f'secrets/graphs/{u.git_HEAD()}/', f'{inner_dir}/graphs', symlinks = True, ignore = ignore_patterns('static'), copy_function = os.link)
  with open(f'{inner_dir}/README.txt', 'a') as f:
    f.write(f'''
To regenerate these charts:
* git clone https://github.com/nationalarchives/engagingcrowds_engagement.git
* cd engagingcrowds_engagement
* git co {u.git_HEAD()} #git co 97cedb41511b9494b750152b26d91cfe24bd46d1 to use the same version as the charts in the report
* pip install pandas@1.4.1  #You might prefer to do this in a virtualenv
* pip install plotly@5.6.0  #You might prefer to do this in a virtualenv
* pip install kaleido@0.2.1 #You might prefer to do this in a virtualenv
* wget https://tanc-ahrc.github.io/EngagingCrowds/data/all_classifications.csv
* ./analyse.py
Graphs will appear in secrets/graphs/{u.git_HEAD()}
The CSV files can be used to confirm that the graphs are based upon the same input data
The overall run log and the *_desc.txt files contain additional data.

''')

  procs = []
  for ar_format in ('zip', 'xztar'):
    p = Process(target = make_archive, args = ('sharing/data_analysis', ar_format, tmpdir))
    p.start()
    procs.append(p)
  for p in procs: p.join()
