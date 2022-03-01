#!/bin/bash

HASH="`git rev-parse HEAD`"
SHOW=1
while getopts "t:p:g:H:S" arg; do
  case "${arg}" in
    t) TYPES+=("${OPTARG}");; #project workflow workflow_type
    p) POPULATIONS+=("${OPTARG}");; #all_classifiers multi_classifiers mono_classifiers first_last_days
    g) GRAPHS+=("${OPTARG}");; #identifying extension in graph e.g. _q[34]
    H) HASH="${OPTARG}";;
    S) SHOW=0;; 
  esac
done
shift $((OPTIND - 1))

HELPER="-t `ls secrets/graphs/${HASH}/class_times`"
for TYPE in "${TYPES[@]}"; do
  HELPER="-p `ls secrets/graphs/${HASH}/class_times/${TYPE}`"
  for POPULATION in "${POPULATIONS[@]}"; do
    HELPER="-g `ls secrets/graphs/${HASH}/class_times/${TYPE}/${POPULATION}/dynamic | sed 's/\.html//g'`"
    for GRAPH in "${GRAPHS[@]}"; do
      #echo secrets/graphs/"${HASH}"/class_times/"${TYPE}"/"${POPULATION}"/ -name "*${GRAPH}.html" >&2
      find secrets/graphs/"${HASH}"/class_times/"${TYPE}"/"${POPULATION}"/ -name "*${GRAPH}.html"
    done | sort -t / -g -k 5,6 -k 6,7 -k 8  | { if [ $SHOW -ne 1 ]; then xargs google-chrome --new-window & else echo "${TYPE^^}" "${POPULATION^^}"; tee; fi }
  done
done
echo $HELPER
