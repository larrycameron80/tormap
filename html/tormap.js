var togglestate_Other      = 0;
var togglestate_Stable     = 0;
var togglestate_FastStable = 1;
var togglestate_Exit       = 1;
var togglestate_FastExit   = 1;
var togglestate_Bad        = 1;
var togglestate_Authority  = 1;

var kmlPATH='https://tormap.void.gr/maps/';

var geoXML_Other;
var geoXML_Authority;
var geoXML_Bad;
var geoXML_FastExit;
var geoXML_Exit;
var geoXML_Stable;
var geoXML_FastStable;

function initialize() {
    var latlng = new google.maps.LatLng(40.00,40.00);
    var myOptions = {
      zoom: 2,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    }

geoXML_Authority = new google.maps.KmlLayer( kmlPATH + 'tormap_auth.kmz', {suppressInfoWindows: true, preserveViewport: true});
geoXML_Bad = new google.maps.KmlLayer( kmlPATH + 'tormap_bad.kmz',{suppressInfoWindows: true, preserveViewport: true});
geoXML_FastExit = new google.maps.KmlLayer( kmlPATH + 'tormap_exitFast.kmz',{suppressInfoWindows: true, preserveViewport: true});
geoXML_Exit = new google.maps.KmlLayer(kmlPATH + 'tormap_exit.kmz',{suppressInfoWindows: true, preserveViewport: true});
geoXML_FastStable = new google.maps.KmlLayer( kmlPATH + 'tormap_stableFast.kmz',{suppressInfoWindows: true, preserveViewport: true});
geoXML_Stable = new google.maps.KmlLayer( kmlPATH + 'tormap_stable.kmz',{suppressInfoWindows: true, preserveViewport: true});
geoXML_Other = new google.maps.KmlLayer( kmlPATH + 'tormap_other.kmz',{suppressInfoWindows: true, preserveViewport: true});

    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
//    geoXML_Other.setMap(map);
//    geoXML_Stable.setMap(map);
    geoXML_FastStable.setMap(map);
    geoXML_Exit.setMap(map);
    geoXML_FastExit.setMap(map);
    geoXML_Bad.setMap(map);
    geoXML_Authority.setMap(map);

    google.maps.event.addListener(geoXML_Other, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });
    google.maps.event.addListener(geoXML_Stable, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });
    google.maps.event.addListener(geoXML_FastStable, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });
    google.maps.event.addListener(geoXML_Exit, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });
    google.maps.event.addListener(geoXML_FastExit, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });
    google.maps.event.addListener(geoXML_Bad, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });
    google.maps.event.addListener(geoXML_Authority, 'click', function(kmlEvent) {
      var nodename = kmlEvent.featureData.name;
      var description = kmlEvent.featureData.description;
      var text = nodename + "\n" + description
      showInContentWindow(text);
    });

    function showInContentWindow(text) {
      var sidediv = document.getElementById('content_window');
      sidediv.innerHTML = text;
    }
}
function toggleFastExit()  {
    if (togglestate_FastExit == 1)   {
    geoXML_FastExit.setMap(null);
    togglestate_FastExit = 0;
    }  else  {
    geoXML_FastExit.setMap(map);
    togglestate_FastExit = 1;
    }
}

function toggleAuthority() {
    if (togglestate_Authority == 1) {
    geoXML_Authority.setMap(null);
    togglestate_Authority = 0;
    } else {
    geoXML_Authority.setMap(map);
    togglestate_Authority = 1;
    }
}

function toggleBad() {
    if (togglestate_Bad == 1) {
    geoXML_Bad.setMap(null);
    togglestate_Bad = 0;
    } else {
    geoXML_Bad.setMap(map);
    togglestate_Bad = 1;
    }
}

function toggleExit() {
    if (togglestate_Exit == 1) {
    geoXML_Exit.setMap(null);
    togglestate_Exit = 0;
    } else {
    geoXML_Exit.setMap(map);
    togglestate_Exit = 1;
    }
}

function toggleStable() {
    if (togglestate_Stable == 1) {
    geoXML_Stable.setMap(null);
    togglestate_Stable = 0;
    } else {
    geoXML_Stable.setMap(map);
    togglestate_Stable = 1;
    }
}

function toggleFastStable() {
    if (togglestate_FastStable == 1) {
    geoXML_FastStable.setMap(null);
    togglestate_FastStable = 0;
    } else {
    geoXML_FastStable.setMap(map);
    togglestate_FastStable = 1;
    }
}

function toggleOther() {
    if (togglestate_Other == 1) {
    geoXML_Other.setMap(null);
    togglestate_Other = 0;
    } else {
    geoXML_Other.setMap(map);
    togglestate_Other = 1;
    }
}
