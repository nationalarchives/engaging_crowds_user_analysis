#!/bin/bash
cat "`dirname $0`"/header.html > "`dirname $0`"/../sharing/hms_gallery.html
csvtool namedcols subj.filename,location <(tar xf sharing/HMS_NHS.tar.xz ./HMS_NHS_data/classifications.csv -O)  | sed 1d | sort -t, -k1,1 -u | csvtool col 2 - | sed 's#.*#{type: "image", url: "&"},#' >> "`dirname $0`"/../sharing/hms_gallery.html
cat "`dirname $0`"/footer.html >> "`dirname $0`"/../sharing/hms_gallery.html
