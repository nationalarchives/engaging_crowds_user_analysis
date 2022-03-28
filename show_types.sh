#!/bin/bash
#e.g. ./show_projects.sh will show the overview
#     ./show_projects.sh _q[34] will show the top/other quartiles breakdown
HASH="`git rev-parse HEAD`"
while getopts "H:" arg; do
  case "${arg}" in
    H) HASH="${OPTARG}";;
  esac
done
shift $((OPTIND - 1))

google-chrome --new-window \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow_type/all_classifiers/dynamic/col-num${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow_type/all_classifiers/dynamic/col-date${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow_type/all_classifiers/dynamic/col-dropdown${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow_type/all_classifiers/dynamic/col-noun${1}.html \
  &
