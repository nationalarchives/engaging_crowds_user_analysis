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
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/1._ADMISSION_NUMBER${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/5._AGE${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/14._NUMBER_OF_DAYS_IN_HOSPITAL${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/YEARS_AT_SEA${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/2._DATE_OF_ENTRY${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/12._DATE_OF_DISCHARGE${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/QUALITY_\(DD\)${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/HOW_DISPOSED_OF_\(DD\)${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/7._PLACE_OF_BIRTH_NATIONALITY${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/10._WHERE_FROM${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/3._NAME${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/8._SHIP_SHIP_OR_PLACE_OF_EMPLOYMENT_LAST_SHIP${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/11._NATURE_OF_COMPLAINT${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/People${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/attendance${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/Meetings${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/Latitude_Longitude${1}.html \
  file://"${PWD}"/secrets/graphs/"${HASH}"/class_times/workflow/all_classifiers/dynamic/Geography${1}.html \
  &
