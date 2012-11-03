#!/usr/bin/env python
# encoding: utf-8

'''  
 quick and dirty hack Moritz Bartl moritz@torservers.net
 13.12.2010

 Changes by George Kargiotakis kargig[at]void[dot]gr
 01.11.2012

 requires: 
 - pygeoip, https://code.google.com/p/pygeoip/
 - geoIP city database, eg. https://www.maxmind.com/app/geolitecity

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License (LGPL) 
 as published by the Free Software Foundation, either version 3 of the 
 License, or any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 https://www.gnu.org/licenses/
'''

#Variables
FAST = 1000000
KMLDIR = 'maps/'
WWWDIR = ''

import os
import base64, shelve, pygeoip, cgi, re
from operator import attrgetter, itemgetter
from string import Template
import random

def parse():
        cachedRelays = dict()
        currentRouter = dict()
        # parse cached-descriptors to extract uptime and announced bandwidth
        with open('all') as f:
            for line in f:
                line = line.strip()
                if line.startswith('router '):
                    [nil,name,ip,orport,socksport,dirport] = line.split()
                    currentRouter['name'] = name
                    currentRouter['ip'] = ip
                    currentRouter['orport'] = orport
                    currentRouter['socksport'] = socksport
                    currentRouter['dirport'] = dirport
                if line.startswith('platform '):
                    currentRouter['version']=line[9:]
                if line.startswith('opt fingerprint'):
                    fingerprint=line[16:]
                    currentRouter['fingerprint'] = fingerprint.replace(' ','').lower()
                if line.startswith('fingerprint'):
                    fingerprint=line[12:]
                    currentRouter['fingerprint'] = fingerprint.replace(' ','').lower()
                if line.startswith('uptime '):
                    currentRouter['uptime']=line[7:]
                if line.startswith('bandwidth '):
                    currentRouter['bandwidth'] = line[10:]
                    try:
                        currentRouter['bw-observed'] = int(line.split()[3])
                    except:
                        pass
                    bandwidth = line[10:]
                if line.startswith('contact '):
                    currentRouter['contact'] = cgi.escape(line[8:])
                if line == 'router-signature':
                    fingerprint = currentRouter['fingerprint']
                    cachedRelays[fingerprint] = currentRouter
                    currentRouter = dict()

        # parse cached-consensus for flags and correlate to descriptors


        count = 0
        with open('consensus') as f:
            for line in f:
                line = line.strip()
                if line.startswith('r '):
                    [nil,name,identity,digest,date,time,ip,orport,dirport] = line.split()
                    identity = identity.strip()
                    fingerprint = base64.decodestring(identity + '=\n').encode('hex')
                    # php: unpack('H*',decode_base64($identity))
                    currentRouter = dict()
                    if fingerprint in cachedRelays:
                        currentRouter = cachedRelays[fingerprint]
                    # trust consensus more than cached-descriptors, replace info
                    currentRouter['fingerprint'] = fingerprint
                    currentRouter['name'] = name
                    currentRouter['ip'] = ip
                    currentRouter['orport'] = orport
                    currentRouter['dirport'] = dirport
                if line.startswith('p '):
                    currentRouter['policy'] = line[2:]
                if line.startswith('s '):
                    flags = line[2:]
                    currentRouter['flags'] = flags
                    if flags.find('Bad')>-1:
                        badRelays[fingerprint] = currentRouter
                    elif flags.find('Authority')>-1:
                        authRelays[fingerprint] = currentRouter
                    elif flags.find('Exit')>-1:
                        if currentRouter.has_key('bw-observed') and currentRouter['bw-observed']>FAST:
                            exitFastRelays[fingerprint] = currentRouter
                        else:
                            exitRelays[fingerprint] = currentRouter
                    elif flags.find('Stable')>-1:
                        if currentRouter.has_key('bw-observed') and currentRouter['bw-observed']>FAST:
                            stableFastRelays[fingerprint] = currentRouter
                        else:
                            stableRelays[fingerprint] = currentRouter
                    elif flags.find('Named')>-1:
                        namedRelays[fingerprint] = currentRouter
                    else:
                        otherRelays[fingerprint] = currentRouter

        print 'Bad:', len(badRelays)
        print 'Exit:', len(exitRelays)
        print 'Fast exit:', len(exitFastRelays)
        print 'Non-exit stable:', len(stableRelays)
        print 'Fast non-exit stable:', len(stableFastRelays)
        print 'Authority:', len(authRelays)
        print 'Named:', len(namedRelays)
        print 'Other:', len(otherRelays)

        inConsensus = len(namedRelays)+len(authRelays)+len(badRelays)+len(exitRelays)+len(stableRelays)+len(otherRelays)
        print '[ in consensus:', inConsensus, ']'
        notInConsensus = len(cachedRelays)-len(badRelays)-len(exitRelays)-len(stableRelays)-len(otherRelays)
        print '[ cached descriptors not in consensus:', notInConsensus, ']'

        # put all relays we want to plot in one list for geoIP
        allRelays.update(exitRelays)
        allRelays.update(exitFastRelays)
        allRelays.update(stableRelays)
        allRelays.update(stableFastRelays)
        allRelays.update(authRelays)
        allRelays.update(namedRelays)
        allRelays.update(otherRelays)
        allRelays.update(badRelays)

def geoiplookup():
        # geoIP
        geoIPcache = shelve.open('geoip-cache')
        geoIPdb = None

        for relay in allRelays.values():
            ip = relay['ip']
            if geoIPcache.has_key(ip):
                info = geoIPcache[ip]
            else:
                if geoIPdb is None:
                    geoIPdb = pygeoip.GeoIP('GeoLiteCity.dat',pygeoip.STANDARD)
                info = geoIPdb.record_by_addr(ip)
                geoIPcache[ip] = info
            if info is None:
                print 'GeoIP problem: ',relay['name'],ip
            if info is not None:
                relay['location'] = info
                relay['latitude'] = info['latitude'] + random.random()/(5*10)
                relay['longitude'] = info['longitude'] + random.random()/(5*10)
            
        geoIPcache.close()


def generateFolder(name, styleUrl, relays):
        placemarkTemplate = Template ('<Placemark>\n\
            <name>$name</name>\n\
            <description>\n\
            <![CDATA[\n\
            <p><strong>IP</strong>: <a href="https://tools.whois.net/whoisbyip/$ip">$ip</a></p>\n\
            <p><strong>ORPort</strong>: $orport <strong>DirPort</strong>: $dirport</p>\n\
            <p><strong>Bandwidth</strong>: $bandwidth</p>\n\
            <p><strong>Flags</strong>: $flags</p>\n\
            <p><strong>Uptime</strong>: $uptime</p>\n\
            <p><strong>Contact</strong>: $contact</p>\n\
            <p><strong>Policy</strong>: $policy</p>\n\
            <p><strong>Fingerprint</strong>: <a href="https://torstatus.blutmagie.de/router_detail.php?FP=$fingerprint">$prettyFingerprint</a></p>\n\
            <p><strong>Version</strong>: $version</p>\n\
            ]]>\n\
            </description>\n\
            <styleUrl>$styleUrl</styleUrl>\n\
            <Point>\n\
                <coordinates>$longitude,$latitude</coordinates>\n\
            </Point>\n\
            </Placemark>\n\
            ')

        group = '<Folder>\n<name>%s</name>\n' % name
        for fingerprint,relay in relays.items():
            # for displaying: pretty fingerprint in blocks of four, uppercase
            relay['prettyFingerprint'] = " ".join(filter(None, re.split('(\w{4})', fingerprint.upper())))
            relay['styleUrl'] = styleUrl
            if 'contact' not in relay:
                relay['contact'] = 'None'
            placemark = placemarkTemplate.safe_substitute(relay)
            group = group + placemark
        group = group + "\n</Folder>"
        return group

def genkml():
        # generate KML
        kmlBody = ()

        parts = icon_dict.keys()
#        parts = ['auth','bad','exitFast','exit','stableFast','stable','named','other']
        for part in parts:
            kmlBody = ''
            if part == 'auth':
                kmlBody = kmlBody + generateFolder("%s Authority nodes" % len(authRelays), "#auth", authRelays)
            elif part == 'bad':
                kmlBody = kmlBody + generateFolder("%s Bad" % len(badRelays), "#bad", badRelays)
            elif part == 'exitFast':
                kmlBody = kmlBody + generateFolder("%s Fast Exits (>= 1MB/s)" % len(exitFastRelays), "#exitFast", exitFastRelays)
            elif part == 'exit':
                kmlBody = kmlBody + generateFolder("%s Exits" % len(exitRelays), "#exit", exitRelays)
            elif part == 'stableFast':
                kmlBody = kmlBody + generateFolder("%s Fast stable nodes (>= 1MB/s)" % len(stableFastRelays), "#stableFast", stableFastRelays)
            elif part == 'stable':
                kmlBody = kmlBody + generateFolder("%s Stable nodes" % len(stableRelays), "#stable", stableRelays)
            elif part == 'named':
                kmlBody = kmlBody + generateFolder("%s Named nodes" % len(namedRelays), "#named", namedRelays)
            elif part == 'other':
                kmlBody = kmlBody + generateFolder("%s Other" % len(otherRelays), "#other", otherRelays)

            if not os.path.exists(KMLDIR):
                os.makedirs(KMLDIR)
            kml = open(KMLDIR + 'tormap_' + part + '.kml', 'w')

            styletag=(
                '   <Style id="'+ part + '">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>' + icon_dict[part] + '</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
             )

            kmlHeader_top = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<kml xmlns="https://www.opengis.net/kml/2.2" xmlns:gx="https://www.google.com/kml/ext/2.2" xmlns:kml="https://www.opengis.net/kml/2.2" xmlns:atom="https://www.w3.org/2005/Atom">\n'
                '<Document>\n'
                '	<name>Tor relays</name>\n'
            )

            kmlHeader_all = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<kml xmlns="https://www.opengis.net/kml/2.2" xmlns:gx="https://www.google.com/kml/ext/2.2" xmlns:kml="https://www.opengis.net/kml/2.2" xmlns:atom="https://www.w3.org/2005/Atom">\n'
                '<Document>\n'
                '	<name>Tor relays</name>\n'
                '	<Style id="exit">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/grn-blank.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="exitFast">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/red-stars.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="stable">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/ylw-blank.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="stableFast">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/purple-blank.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="other">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="auth">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/blu-stars.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="named">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/paddle/wht-stars.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                '	<Style id="bad">\n'
                '		<IconStyle>\n'
                '			<Icon>\n'
                '				<href>https://maps.google.com/mapfiles/kml/pal3/icon41.png</href>\n'
                '			</Icon>\n'
                '		</IconStyle>\n'
                '	</Style>\n'
                )
           
            kmlFooter = ('</Document>\n'
                             '</kml>\n')
              
            kml.write(kmlHeader_top)
            kml.write(styletag)
            kml.write(kmlBody)
            kml.write(kmlFooter)
            kml.close()

def genhtml():
        # generate HTML
        htmlBody = ()

def main(argv=None):
    parse()
    geoiplookup()
    genkml()
#    genhtml()

import sys
if __name__ == "__main__":
    icon_dict = {
        'auth':'https://maps.google.com/mapfiles/kml/paddle/blu-stars.png', 
        'bad':'https://maps.google.com/mapfiles/kml/pal3/icon41.png',
        'exitFast':'https://maps.google.com/mapfiles/kml/paddle/red-stars.png',
        'exit':'https://maps.google.com/mapfiles/kml/paddle/grn-blank.png',
        'stableFast':'https://maps.google.com/mapfiles/kml/paddle/purple-blank.png',
        'stable':'https://maps.google.com/mapfiles/kml/paddle/ylw-blank.png',
        'named':'https://maps.google.com/mapfiles/kml/paddle/wht-stars.png',
        'other':'https://maps.google.com/mapfiles/kml/paddle/wht-blank.png',
    }
    allRelays = dict()
    badRelays = dict() # Bad in flags, eg. BadExit, BadDirectory
    exitFastRelays = dict() # Exit flag, >= FAST
    exitRelays = dict() # Exit flag, slower than FAST
    stableFastRelays = dict() # Stable flag, but not Exit
    stableRelays = dict() # Stable flag, but not Exit
    authRelays = dict() # Authority flag
    namedRelays = dict() # Named flag
    otherRelays = dict() # non Stable, non Exit
    sys.exit(main())
