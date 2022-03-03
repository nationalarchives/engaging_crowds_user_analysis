#!/bin/bash

#users_to_count.sh must declare an associative array USER_ID mapping user_name to user_id
#For example:
#declare -A USER_ID
#USER_ID["janedoe"]=1
#USER_ID["joebloggs"]=2
. secrets/users_to_count.sh

HASH="`git rev-parse HEAD`"

total=0
{
  echo 'Username ID Pseudonym Classifications'
  echo '-------- -- --------- ---------------'
  for key in "${!USER_ID[@]}"; do
    pseudonym=`cat secrets/identities.json | jq --raw-output ".[\"${USER_ID[${key}]}\"]"`
    classifications=`csvtool namedcol pseudonym secrets/graphs/${HASH}/prepared_classifications.csv | grep "^${pseudonym}$" | wc -l`
    total=$((total + classifications))
    echo "${key} (${USER_ID[${key}]}) (${pseudonym}): ${classifications}"
  done
  echo ---
  echo TOTAL: $total
} | column -t
