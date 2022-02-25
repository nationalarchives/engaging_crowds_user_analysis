#!/bin/bash
#As written, is just comparing 'all classifiers' at 'project' level

first="$1"
second="$2"

echo "Only differences should be local URL paths (e.g. 'url(#...)') to ids that I have deleted for comparison purposes."
echo "And the git info embedded in the title."
echo "Likely to be plenty of other differences otherwise."
ls secrets/graphs/"$first"/class_times/project/all_classifiers/static/*.svg
for x in secrets/graphs/"$first"/class_times/project/all_classifiers/static/*.svg; do
  filename="`basename $x`"
  echo "Comparing '$filename' in '$first' and '$second'"
  xmllint --format "$x" | xmlstarlet ed -d '//@id' > "A_${filename}"
  xmllint --format secrets/graphs/"$second"/class_times/project/all_classifiers/static/`basename $x` | xmlstarlet ed -d '//@id' > "B_${filename}"
  meld "A_${filename}" "B_${filename}" #tkdiff too slow to cope
  rm  "A_${filename}" "B_${filename}"
done
