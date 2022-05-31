#Usage ./to_site.sh <path up to and including simple-site/

HASH=`git rev-parse HEAD`

DATA="$1"/docs/data
cp sharing/{HMS_NHS,Scarlets_and_Blues,RBGE_Herbarium}.{zip,tar.xz} "${DATA}"
