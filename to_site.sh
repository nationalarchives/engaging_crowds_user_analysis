#Usage ./to_site.sh <path up to and including simple-site/

HASH=`git rev-parse HEAD`

DATA="$1"/docs/data
cp sharing/{HMS_NHS,Scarlets_and_Blues,RBGE_Herbarium}.{zip,tar.xz} "${DATA}"

SITE="${DATA}"/analysis/time
PREFIX=secrets/graphs/"${HASH}"/class_times/
cp "${PREFIX}"/project/all_classifiers/dynamic/plotly.min.js "${SITE}"
cp "${PREFIX}"/project/all_classifiers/dynamic/HMS_NHS.html "${SITE}"
cp "${PREFIX}"/workflow_type/all_classifiers/dynamic/col-num.html "${SITE}"
cp "${PREFIX}"/workflow/all_classifiers/dynamic/1._ADMISSION_NUMBER.html "${SITE}"
cp "${PREFIX}"/workflow/all_classifiers/dynamic/5._AGE.html "${SITE}"
cp "${PREFIX}"/workflow/all_classifiers/dynamic/YEARS_AT_SEA.html "${SITE}"
cp "${PREFIX}"/workflow/all_classifiers/dynamic/14._NUMBER_OF_DAYS_IN_HOSPITAL.html "${SITE}"

SITE="${DATA}"/analysis/active
cp "${PREFIX}"/project/first_last_day/dynamic/plotly.min.js "${SITE}"
cp "${PREFIX}"/project/first_last_day/dynamic/HMS_NHS_agg_gain.html "${SITE}"
cp "${PREFIX}"/workflow_type/first_last_day/dynamic/Numbers_agg_gain.html "${SITE}"
