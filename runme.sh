#!/bin/bash

KMLDIR='/var/www/maps'
TMPDIR='/tmp/tormap'
BINDIR='/usr/local/bin/'

if [ ! -d /tmp/tormap ]; then
	mkdir -p $TMPDIR
fi

if [ -e $KMLDIR/tormap_auth.kml ]; then
	# Find a random Authority:
	AUTHORITY=`grep -A1 IP $KMLDIR/tormap_auth.kml | \
		sed -e 's/.*\">\(.*\)<\/a.*/\1/g' -e 's/.*DirPort.*: \(.*\)<.*/\1/g' -e 's/\r//g' \
		| grep -v -- "--" | xargs -n 2 | awk '{ print $1":"$2 }' | sort -R | head -n1`

	# Get microdescriptors
	wget "http://${AUTHORITY}/tor/server/all.z" -O $TMPDIR/all.z -o /dev/null -q

	# Get consensus
	wget "http://${AUTHORITY}/tor/status-vote/current/consensus.z" -O $TMPDIR/consensus.z -o /dev/null -q
else
	# use dannenberg.ccc.de as fallback
	wget "http://193.23.244.244/tor/server/all.z" -O $TMPDIR/all.z -o /dev/null -q
	wget "http://193.23.244.244/tor/status-vote/current/consensus.z" -O $TMPDIR/consensus.z -o /dev/null -q
fi

cd $TMPDIR
printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" |cat - $TMPDIR/all.z |gzip -dc > $TMPDIR/all 2>/dev/null
printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" |cat - $TMPDIR/consensus.z |gzip -dc > $TMPDIR/consensus 2>/dev/null
if [ -s $TMPDIR/all ]; then
	rm -f $TMPDIR/all.z 
else
	echo "all file uncompression failed. exiting."
	exit 2
fi
if [ -s $TMPDIR/consensus ]; then
	rm -f $TMPDIR/consensus.z
else
	echo "consensus file uncompression failed. exiting."
	exit 2
fi

#Download geolitecity database once a month
if [ -e $TMPDIR/GeoLiteCity.dat ]; then
	DBAGE=`stat -c %Z $TMPDIR/GeoLiteCity.dat`
	CDATE=`date +%s`
	if [ $(( $CDATE - $DBAGE )) -gt 2592000 ]; then
		wget "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz" -O $TMPDIR/GeoLiteCity.dat.gz -o /dev/null -q
		gunzip $TMPDIR/GeoLiteCity.dat.gz
	fi
else
	wget "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz" -O $TMPDIR/GeoLiteCity.dat.gz -o /dev/null -q
	gunzip $TMPDIR/GeoLiteCity.dat.gz
fi

if [ -e $TMPDIR/GeoLiteCity.dat ] && [ -e $TMPDIR/all ] && [ -e $TMPDIR/consensus ]; then
	python $SDIR/tormap.py
else
	echo "missing important files. exiting."
	exit 2
fi
