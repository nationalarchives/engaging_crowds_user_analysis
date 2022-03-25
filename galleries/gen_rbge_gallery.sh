#!/bin/bash
cat "`dirname $0`"/header.html > "`dirname $0`"/../sharing/rbge_gallery.html
csvtool namedcols subj.barcode,location <(tar xf sharing/RBGE_Herbarium.tar.xz ./RBGE_Herbarium_data/classifications.csv -O)  | sed 1d | sort -t, -k1,1 -u | csvtool col 2 - | sed 's#.*#{type: "image", url: "&"},#' >> "`dirname $0`"/../sharing/rbge_gallery.html
cat "`dirname $0`"/footer.html >> "`dirname $0`"/../sharing/rbge_gallery.html
