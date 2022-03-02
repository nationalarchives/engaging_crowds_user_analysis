#!/bin/bash
#e.g. ./show_projects.sh will show the overview
#     ./show_projects.sh _q[34] will show the top/other quartiles breakdown
google-chrome --new-window \
  secrets/graphs/`git rev-parse HEAD`/class_times/workflow_type/all_classifiers/dynamic/col-num${1}.html \
  secrets/graphs/`git rev-parse HEAD`/class_times/workflow_type/all_classifiers/dynamic/col-date${1}.html \
  secrets/graphs/`git rev-parse HEAD`/class_times/workflow_type/all_classifiers/dynamic/col-dropdown${1}.html \
  secrets/graphs/`git rev-parse HEAD`/class_times/workflow_type/all_classifiers/dynamic/col-noun${1}.html
