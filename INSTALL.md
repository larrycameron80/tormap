Installation instructions:
1. copy html/* files to your web path
1. go to your web patch and
   1. git clone https://github.com/pointhi/leaflet-color-markers.git  
   1. git clone https://github.com/shramov/leaflet-plugins.git 
1. copy tormap.py along with runme.sh to a directory of your choice (BINDIR)
1. edit runme.sh and change the following variables:
	KMLDIR='/var/www/maps'
	TMPDIR='/tmp/tormap'
	BINDIR='/usr/local/bin/'
1. edit tormap.py and change the following variables:
	KMLDIR = '/var/www/maps/'
	HTMLDIR = '/var/www/'
	TMPDIR= '/tmp/tormap/'
1. edit html/osm.js and change the kmlPATH variable:
	var kmlPATH='https://tormap.void.gr/maps/';
1. run runme.sh from crontab
