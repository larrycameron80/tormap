#!/bin/bash

KMLDIR='/var/www/maps'
TMPDIR='/tmp/tormap'
BINDIR='/usr/local/bin'

if [ ! -d $TMPDIR ]; then
	mkdir -p $TMPDIR
fi

cd $TMPDIR || exit 1
rm -f relays.json
curl -sH 'Accept-encoding: gzip' "https://onionoo.torproject.org/details" -o /tmp/tormap/relays.json.gz
gunzip relays.json.gz
python $BINDIR/tormap.py
cd $KMLDIR || exit 1
for i in *.kml; do BASE=`basename "${i}" .kml`; zip "${BASE}".kmz "${i}"; done
