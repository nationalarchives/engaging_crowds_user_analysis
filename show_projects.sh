#!/bin/bash
#e.g. ./show_projects.sh will show the overview
#     ./show_projects.sh _q[34] will show the top/other quartiles breakdown
google-chrome --new-window \
  secrets/graphs/`git rev-parse HEAD`/class_times/project/all_classifiers/dynamic/HMS_NHS${1}.html \
  secrets/graphs/`git rev-parse HEAD`/class_times/project/all_classifiers/dynamic/Scarlets_and_Blues${1}.html \
  secrets/graphs/`git rev-parse HEAD`/class_times/project/all_classifiers/dynamic/RBGE_Herbarium${1}.html
