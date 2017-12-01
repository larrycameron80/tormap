#!/usr/bin/env python
# encoding: utf-8

'''
 quick and dirty hack Moritz Bartl moritz@torservers.net
 13.12.2010

 Changes by George Kargiotakis kargig[at]void[dot]gr
 01.11.2012

 Change script to use https://onionoo.torproject.org/
 28.11.2017 - George Kargiotakis kargig[at]void[dot]gr

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
FAST = 5000000
KMLDIR = '/var/www/maps/'
HTMLDIR = '/var/www/'
TMPDIR= '/tmp/tormap/'

import os
import re
from string import Template
import random
import json
import sys

def parsejson():
  with open(TMPDIR+'relays.json', 'r') as relay_file:
    types = json.load(relay_file)
    for relay in types['relays']:
      # use only the ones that are found running in consensus
      if relay['running'] == True:
        # add jitter for geolocation
        try:
            relay['latitude'] = relay['latitude'] + random.random()/(5*10)
            relay['longitude'] = relay['longitude'] + random.random()/(5*10)
        except:
            relay['latitude'] = random.random()/(5*10)
            relay['longitude'] = random.random()/(5*10)
        for address in relay['or_addresses']:
          if address.startswith('['):
            try:
                result = re.search('\[(.*)\]:(.*)', address)
                ipv6  = result.group(1)
                oport = result.group(2)
                relay['ipv6'] = ipv6
                relay['orport6'] = oport
            except:
                pass
          else:
            oport = address.split(':')[-1]
            ip = address.split(':')[0]
            relay['ipv4'] = ip
            relay['orport4'] = oport
        try:
            dport = relay['dir_address'].split(':')[1]
            relay['dirport'] = dport
        except:
            relay['dirport'] = 'None'
        fingerprint = relay['fingerprint']
        if 'BadExit' in relay['flags']:
            badRelays[fingerprint] = relay
        elif 'Authority' in relay['flags']:
            authRelays[fingerprint] = relay
        elif 'Exit' in relay['flags']:
          if relay.has_key('observed_bandwidth') and relay['observed_bandwidth']>FAST:
            exitFastRelays[fingerprint] = relay
          else:
            exitRelays[fingerprint] = relay
        elif 'Stable' in relay['flags']:
          if relay.has_key('observed_bandwidth') and relay['observed_bandwidth']>FAST:
            stableFastRelays[fingerprint] = relay
          else:
            stableRelays[fingerprint] = relay
        else:
            otherRelays[fingerprint] = relay
    print 'Bad:', len(badRelays)
    print 'Exit:', len(exitRelays)
    print 'Fast exit:', len(exitFastRelays)
    print 'Non-exit stable:', len(stableRelays)
    print 'Fast non-exit stable:', len(stableFastRelays)
    print 'Authority:', len(authRelays)
    print 'Other:', len(otherRelays)
    inConsensus = len(authRelays)+len(badRelays)+len(exitRelays)+len(stableRelays)+len(otherRelays)
    print '[ in consensus:', inConsensus, ']'
    notInConsensus = len(types['relays'])-len(badRelays)-len(exitRelays)-len(stableRelays)-len(otherRelays)
    print '[ cached descriptors not in consensus:', notInConsensus, ']'

def generateFolder(name, styleUrl, relays):
        placemarkTemplate = Template ('<Placemark>\n\
            <name>$nickname</name>\n\
            <description>\n\
            <![CDATA[\n\
            <p><strong>IPv4</strong>: <a href="https://centralops.net/co/DomainDossier.aspx?dom_whois=1&net_whois=1&dom_dns=1&addr=$ipv4">$ipv4</a> <strong>ORPort</strong>: $orport4</p>\n\
            <p><strong>IPv6</strong>: <a href="https://centralops.net/co/DomainDossier.aspx?dom_whois=1&net_whois=1&dom_dns=1&addr=$ipv6">$ipv6</a> <strong>ORPort</strong>: $orport6</p>\n\
            <p><strong>DirPort</strong>: $dirport</p>\n\
            <p><strong>Bandwidth</strong>: $observed_bandwidth</p>\n\
            <p><strong>Flags</strong>: $flatflags</p>\n\
            <p><strong>Up since</strong>: $last_restarted</p>\n\
            <p><strong>Contact</strong>: $contact</p>\n\
            <p><strong>IPv4 Policy</strong>: $exit_policy_summary</p>\n\
            <p><strong>IPv6 Policy</strong>: $exit_policy_v6_summary</p>\n\
            <p><strong>Fingerprint</strong>: <a href="https://atlas.torproject.org/#details/$fingerprint">$prettyFingerprint</a></p>\n\
            <p><strong>Platform</strong>: $platform</p>\n\
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
            relay['flatflags'] = ",".join(relay['flags'])
            if 'ipv6' not in relay:
                relay['ipv6'] = ''
                relay['orport6'] = ''
            if 'exit_policy_v6_summary' not in relay:
                relay['exit_policy_v6_summary'] = ''
            else:
                relay['exit_policy_v6_summary'] = json.dumps(relay['exit_policy_v6_summary']).replace("{","").replace("}", "").replace('"','')
            if 'contact' not in relay:
                relay['contact'] = 'None'
            relay['exit_policy_summary'] = json.dumps(relay['exit_policy_summary']).replace("{","").replace("}", "").replace('"','')
            placemark = placemarkTemplate.safe_substitute(relay)
            group = group + placemark
        group = group + "\n</Folder>"
        return group

def genkml():
        # generate KML
        kmlBody = ()

        parts = icon_dict.keys()
        for part in parts:
            kmlBody = ''
            if part == 'auth':
                kmlBody = kmlBody + generateFolder("%s Authority nodes" % len(authRelays), "#auth", authRelays)
            elif part == 'bad':
                kmlBody = kmlBody + generateFolder("%s Bad" % len(badRelays), "#bad", badRelays)
            elif part == 'exitFast':
                kmlBody = kmlBody + generateFolder("%s Fast Exits (>= 5MB/s)" % len(exitFastRelays), "#exitFast", exitFastRelays)
            elif part == 'exit':
                kmlBody = kmlBody + generateFolder("%s Exits" % len(exitRelays), "#exit", exitRelays)
            elif part == 'stableFast':
                kmlBody = kmlBody + generateFolder("%s Fast stable nodes (>= 5MB/s)" % len(stableFastRelays), "#stableFast", stableFastRelays)
            elif part == 'stable':
                kmlBody = kmlBody + generateFolder("%s Stable nodes" % len(stableRelays), "#stable", stableRelays)
            elif part == 'other':
                kmlBody = kmlBody + generateFolder("%s Other" % len(otherRelays), "#other", otherRelays)

            if not os.path.exists(KMLDIR):
                os.makedirs(KMLDIR)
            kml = open(KMLDIR + 'tormap_' + part + '.kml', 'w')

            styletag=(
                '   <Style id="'+ part + '">\n'
                '        <IconStyle>\n'
                '            <Icon>\n'
                '                <href>' + icon_dict[part] + '</href>\n'
                '            </Icon>\n'
                '        </IconStyle>\n'
                '    </Style>\n'
             )

            kmlHeader_top = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<kml xmlns="https://www.opengis.net/kml/2.2" xmlns:gx="https://www.google.com/kml/ext/2.2" xmlns:kml="https://www.opengis.net/kml/2.2" xmlns:atom="https://www.w3.org/2005/Atom">\n'
                '<Document>\n'
                '    <name>Tor relays</name>\n'
            )

            kmlFooter = ('</Document>\n'
                             '</kml>\n')

            kml.write(kmlHeader_top)
            kml.write(styletag)
            kml.write(kmlBody)
            kml.write(kmlFooter)
            kml.close()

def genhtml():
        htmlHeader_top = (
            '<html>\n'
            '  <head>\n'
            '    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">\n'
            '    <meta charset="utf-8">\n'
            '    <title>World City Map of Tor Nodes</title>\n'
            '    <link href="default.css" rel="stylesheet">\n'
            '    <script type="text/javascript" src="tormap.js"></script>\n'
            '  </head>\n'
            '  <body onload="initialize()">\n'
            '    <p align="left">\n'
            '    <a href="https://www.torproject.org"><img alt="Tor Logo" src="tor-logo.jpg" /></a>\n'
        )

        htmlFooter = (
            '    <br /></p>\n'
            '    <div id="map_canvas" style="width: 79%; height: 80%; float: left"></div>\n'
            '    <div id="content_window" style="width: 21%; height: 80%; float: left"></div>\n'
            '    <br />Read more at <a href="https://github.com/kargig/tormap">https://github.com/kargig/tormap</a>\n'
            '    <script async defer src="https://maps.googleapis.com/maps/api/js?key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&callback=initialize"\n'
            '    type="text/javascript"></script>\n'
            '  </body>\n'
            '</html>\n'
        )

        htmlBody = ()
        htmlBody = ''
        #we need a certain order inside the html
        parts = ['other','stable','stableFast','exit','exitFast','auth','bad']
        for part in parts:
            if part == 'auth':
                htmlBody += (
                        '    <img alt="Authority" src="' + icon_dict[part] + '" />\n'
                        '    <input onclick="toggleAuthority();" type="checkbox" value="Authority" checked/>Authority ('
                        + str(len(authRelays)) + ')\n'
                        )
            elif part == 'bad':
                htmlBody += (
                        '    <img alt="Bad" src="'+ icon_dict[part] + '" />\n'
                        '    <input onclick="toggleBad();" type="checkbox" value="Bad" checked/>Bad ('
                        + str(len(badRelays)) + ')\n'
                        )
            elif part == 'exitFast':
                htmlBody += (
                        '    <img alt="FastExit" src="' + icon_dict[part] + '" />\n'
                        '    <input onclick="toggleFastExit();" type="checkbox" value="Fast Exits" checked/>Fast Exit (>5Mb/s) ('
                        + str(len(exitFastRelays)) + ')\n'
                        )
            elif part == 'exit':
                htmlBody += (
                        '    <img alt="Exit" src="' + icon_dict[part] + '" />\n'
                        '    <input onclick="toggleExit();" type="checkbox" value="Exit" checked/>Exit ('
                        + str(len(exitRelays)) + ')\n'
                        )
            elif part == 'stableFast':
                htmlBody += (
                        '    <img alt="FastStable" src="' + icon_dict[part] + '" />\n'
                        '    <input onclick="toggleFastStable();" type="checkbox" value="Fast Stable"/>Fast Stable (>5Mb/s) ('
                        + str(len(stableFastRelays)) + ')\n'
                        )
            elif part == 'stable':
                htmlBody += (
                        '    <img alt="Stable" src="' + icon_dict[part] + '" />\n'
                        '    <input onclick="toggleStable();" type="checkbox" value="Stable" />Stable ('
                        + str(len(stableRelays)) + ')\n'
                        )
            elif part == 'other':
                htmlBody += (
                        '    <img alt="Other" src="' + icon_dict[part] + '" />\n'
                        '    <input onclick="toggleOther();" type="checkbox" value="Other" />Other ('
                        + str(len(otherRelays)) + ')\n'
                        )

        if not os.path.exists(HTMLDIR):
            os.makedirs(HTMLDIR)
        html = open(HTMLDIR + 'gmaps.html', 'w')
        html.write(htmlHeader_top)
        html.write(htmlBody)
        html.write(htmlFooter)
        html.close()

def main(argv=None):
    parsejson()
    genkml()
    genhtml()

if __name__ == "__main__":
    icon_dict = {
        'auth':'https://maps.google.com/mapfiles/kml/paddle/blu-stars.png',
        'bad':'https://maps.google.com/mapfiles/kml/pal3/icon41.png',
        'exitFast':'https://maps.google.com/mapfiles/kml/paddle/red-stars.png',
        'exit':'https://maps.google.com/mapfiles/kml/paddle/grn-blank.png',
        'stableFast':'https://maps.google.com/mapfiles/kml/paddle/purple-blank.png',
        'stable':'https://maps.google.com/mapfiles/kml/paddle/ylw-blank.png',
        'other':'https://maps.google.com/mapfiles/kml/paddle/wht-blank.png',
    }
    badRelays = dict() # Bad in flags, eg. BadExit, BadDirectory
    exitFastRelays = dict() # Exit flag, >= FAST
    exitRelays = dict() # Exit flag, slower than FAST
    stableFastRelays = dict() # Stable flag, but not Exit
    stableRelays = dict() # Stable flag, but not Exit
    authRelays = dict() # Authority flag
    otherRelays = dict() # non Stable, non Exit
    sys.exit(main())
