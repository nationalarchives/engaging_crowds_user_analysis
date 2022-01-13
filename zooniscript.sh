#!/bin/bash

. ${HOME}/.local/bin/virtualenvwrapper.sh

cd $ENGAGINGROOT/engagement/
mkdir -p secrets/zoonalysis
cd $ENGAGINGROOT/Data-digging/scripts_GeneralPython/
workon data-digging_python2
for x in `(cd secrets; ls *.csv)`; do
  workflow="${x%-classifications.csv}"
  python basic_classification_processing.py secrets/"$x" --time_elapased                                             > secrets/zoonalysis/"${workflow}-basic.stdout"
  mv secrets/"${x%.csv}"_*.csv secrets/zoonalysis/
  python sessions_inproj_byuser.py          secrets/"$x" "secrets/zoonalysis/${workflow}-sessions.csv" > secrets/zoonalysis/"${workflow}-sessions.stdout"
done
