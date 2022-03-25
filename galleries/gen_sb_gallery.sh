#!/bin/bash
cat "`dirname $0`"/header.html > "`dirname $0`"/../sharing/sb_gallery.html
csvtool namedcols subj.image,location <(tar xf sharing/Scarlets_and_Blues.tar.xz ./Scarlets_and_Blues_data/classifications.csv -O)  | sed 1d | sort -t, -k1,1 -u | csvtool col 2 - | sed 's#.*#{type: "image", url: "&"},#' >> "`dirname $0`"/../sharing/sb_gallery.html
cat "`dirname $0`"/footer.html >> "`dirname $0`"/../sharing/sb_gallery.html
