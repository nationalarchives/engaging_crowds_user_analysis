#!/bin/bash
cat > sharing/sb_gallery.html <<EOF
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/3.0.0/openseadragon.min.js" type="text/javascript"></script>
</head>
<body>
  <input oninput="viewer.goToPage(this.value)">Go to record</input>
  <div id="record" style="height: 100%"></div>
  <script>
    var viewer = OpenSeadragon({
      id: 'record',
      prefixUrl: 'https://cdnjs.cloudflare.com/ajax/libs/openseadragon/3.0.0/images/',
      sequenceMode: true,
      tileSources: [
EOF
csvtool namedcols subj.image,location <(tar xf sharing/Scarlets_and_Blues.tar.xz ./Scarlets_and_Blues_data/classifications.csv -O)  | sed 1d | sort -t, -k1,1 -u | csvtool col 2 - | sed 's#.*#{type: "image", url: "&"},#' >> sharing/sb_gallery.html
cat >> sharing/sb_gallery.html<<EOF
      ]
    });
  </script>
</body>
</html>
EOF
