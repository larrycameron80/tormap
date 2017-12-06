var togglestate_Other      = 0;
var togglestate_Stable     = 0;
var togglestate_FastStable = 0;
var togglestate_Exit       = 1;
var togglestate_FastExit   = 1;
var togglestate_Bad        = 1;
var togglestate_Authority  = 1;

var kmlPATH='https://tormap.void.gr/maps/';

var loaded_stable = 0;
var loaded_faststable = 0;
var loaded_other = 0;

var geoXML_Authority;
var geoXML_Bad;
var geoXML_FastExit;
var geoXML_Exit;
var geoXML_Stable;
var geoXML_FastStable;
var geoXML_Other;
var map;

function initialize() {
    map = new L.Map('map_canvas');                       
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
       attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
       center: [0.0, 0.0],
       zoom: 1,
       maxZoom: 18
    }).addTo(map);
    map.attributionControl.setPrefix('tormap.void.gr'); // Don't show the 'Powered by Leaflet' text.
                                                        
    geoXML_Authority = new L.KML(kmlPATH + "tormap_auth.kml", {async: true});
    geoXML_Bad = new L.KML(kmlPATH + "tormap_bad.kml", {async: true});
    geoXML_FastExit = new L.KML(kmlPATH + "tormap_exitFast.kml", {async: true});
    geoXML_Exit = new L.KML(kmlPATH + "tormap_exit.kml", {async: true});
                                                         
    geoXML_Exit.on("loaded", function(e) { 
       map.fitBounds(e.target.getBounds());
    });
                                           
	//Draw these layers by default
    map.addLayer(geoXML_Authority);
    map.addLayer(geoXML_Bad);
    map.addLayer(geoXML_FastExit);
    map.addLayer(geoXML_Exit);
}

function toggleFastExit()  {
    if (togglestate_FastExit == 1)   {
		map.removeLayer(geoXML_FastExit);
		togglestate_FastExit = 0;
    }  else  {
		map.addLayer(geoXML_FastExit);
		togglestate_FastExit = 1;
    }
}

function toggleAuthority() {
    if (togglestate_Authority == 1) {
		map.removeLayer(geoXML_Authority);
		togglestate_Authority = 0;
    } else {
		map.addLayer(geoXML_Authority);
		togglestate_Authority = 1;
    }
}

function toggleBad() {
    if (togglestate_Bad == 1) {
		map.removeLayer(geoXML_Bad);
		togglestate_Bad = 0;
    } else {
		map.addLayer(geoXML_Bad);
		togglestate_Bad = 1;
    }
}

function toggleExit() {
    if (togglestate_Exit == 1) {
		map.removeLayer(geoXML_Exit);
		togglestate_Exit = 0;
    } else {
		map.addLayer(geoXML_Exit);
		togglestate_Exit = 1;
    }
}

function toggleStable() {
    if (togglestate_Stable == 1) {
		map.removeLayer(geoXML_Stable);
		togglestate_Stable = 0;
    } else {
		if (loaded_stable == 0) {
			geoXML_Stable = new L.KML(kmlPATH + "tormap_stable.kml", {async: true});
			loaded_stable = 1;
		}
		map.addLayer(geoXML_Stable);
		togglestate_Stable = 1;
    }
}

function toggleFastStable() {
    if (togglestate_FastStable == 1) {
		map.removeLayer(geoXML_FastStable);
		togglestate_FastStable = 0;
    } else {
		if (loaded_faststable == 0) {
			geoXML_FastStable = new L.KML(kmlPATH + "tormap_stableFast.kml", {async: true});
			loaded_faststable = 1;
		}
		map.addLayer(geoXML_FastStable);
		togglestate_FastStable = 1;
    }
}

function toggleOther() {
    if (togglestate_Other == 1) {
		map.removeLayer(geoXML_Other);
		togglestate_Other = 0;
    } else {
		if (loaded_other == 0) {
			geoXML_Other = new L.KML(kmlPATH + "tormap_other.kml", {async: true});
			loaded_other = 1;
		}
		map.addLayer(geoXML_Other);
		togglestate_Other = 1;
    }
}
