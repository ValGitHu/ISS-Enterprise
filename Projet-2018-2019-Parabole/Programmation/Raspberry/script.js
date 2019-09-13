var geocoder;
var map;
var id_spot = "undefined";
var imgTestInternet = new Image();
var isSpot = 0;
var isOnline = 1;
var azimuth; var orZoom = 0;
var dernier_marker;
var dernier_info;
var dernier_point;
var dernier_poly;
var dernier_flech1;
var dernier_flech2;

const googleKey = "AIzaSyArU9fki2OkDjzmQNIVLgnjzBKnwz_6sQw";

var jsi = "<script type='text/javascript' src='https://maps.google.com/maps/api/js?key=" + googleKey + "&language=";
jsi += String.locale;
jsi += "'></script>";
document.write(jsi);

function modeStyle(m) {

	if (m == 1) {

		document.getElementById('connect').src = "../images/online.png";
		document.getElementById('logoMode').className = 'on';
		document.getElementById('logoMode').lastChild.nodeValue = localize("%online");
		document.getElementById('centre_online').style.display = 'block';
		document.getElementById('centre_offline').style.display = 'none';
		isOnline = 1;
	}

	else {
		document.getElementById('connect').src = "../images/offline.png";
		document.getElementById('logoMode').className = 'off';
		document.getElementById('logoMode').lastChild.nodeValue = localize("%offline");
		document.getElementById('centre_online').style.display = 'none';
		document.getElementById('centre_offline').style.display = 'block';
		isOnline = 0;
	}

}


//	calcul des l'azimuth et l'Ã©levation
function calc(form, l, n) {
	if (isNaN(l) || isNaN(n)) {
		form.azimuth.value = "";
		form.elevation.value = "";
	}

	else {
		var azi;
		var ele;
		var g = (-9 + n);
		var grad = (g / 57.29578);
		var lrad = (l / 57.29578);
		azi = (3.14159 -
			(-Math.atan((Math.tan(grad) / Math.sin(lrad)))));
		//alert(azi*57.29578);
		form.azimuth.value = (azi * 57.29578).toFixed(2);
		azimuth = (azi * 57.29578);

		a = Math.cos(grad);
		b = Math.cos(lrad);
		ele = Math.atan((a * b - .1512) / (Math.sqrt(1 - (a * a) * (b * b))));
		form.elevation.value = (ele * 57.29578).toFixed(2);


		var pnt = { x: l, y: n };
		var bool = false;

		for (i = 0; i < spotsJson.spots.length - 1 && bool == false; i++) {

			bool = trouveSpot(spotsJson.spots[i], pnt)[0];
			id_spot = trouveSpot(spotsJson.spots[i], pnt)[1];
		}
		afficherCouleur();
	}
}
//fin calcul des l'azimuth et l'Ã©levation

//autocompletion adresse

$(document).ready(function () {
	mode();
	if (isOnline) {
		geocoder = new google.maps.Geocoder();
		$(function () {
			$("#address").autocomplete({
				source: function (request, response) {
					geocoder.geocode({ 'address': request.term, 'language': String.locale }, function (results, status) {
						response($.map(results, function (item) {
							return {
								label: item.formatted_address,
								value: item.formatted_address,
								latitude: item.geometry.location.lat(),
								longitude: item.geometry.location.lng()
							};
						}));
					});
				},
				// si on utilise la fonction du gÃ©ocodage :
				select: function (event, ui) {
					$("#latitude").val((ui.item.latitude).toFixed(5));
					$("#longitude").val((ui.item.longitude).toFixed(5));
					$("#address").val((ui.item.label));
					var pnt = { x: ui.item.latitude, y: ui.item.longitude };
					calc(document.forms[1], parseFloat(ui.item.latitude), parseFloat(ui.item.longitude));
					ajoutMarker(pnt);
				}
			});
		});

	}
});

//fin autocompletion adresse


//div onglets
function reposit(lat, lon, zoom) {
	var posit = new google.maps.LatLng(lat + zoom, lon);
	map.setCenter(posit);
}
function changeOnglet(elem) {
	var getOnglets = document.getElementById('mes_onglets').getElementsByTagName('li');
	for (i = 0; i < getOnglets.length; i++) {
		if (getOnglets[i].id) {
			if (getOnglets[i].id == elem.id) {
				getOnglets[i].className = 'mon_onglet_selected';
				document.getElementById('c_' + elem.id).style.display = 'block';
				google.maps.event.trigger(map, 'resize');
				//centrer la carte au changement d'onglet
				if (dernier_marker != null) {
					var zoom = map.getZoom();
					var lat = dernier_marker.getPosition().lat();
					var lon = dernier_marker.getPosition().lng();

					if (zoom < 6) reposit(lat, lon, (4 / zoom));

					else if (zoom < 13 && zoom >= 6) reposit(lat, lon, (0.25 / zoom));

					else if (zoom < 17 && zoom >= 13) reposit(lat, lon, (0.01 / zoom));

					else reposit(lat, lon, (0.0001 / zoom));

				}
				//fin
			}
			else {
				getOnglets[i].className = 'mon_onglet';
				document.getElementById('c_' + getOnglets[i].id).style.display = 'none';

			}
		}
	}
}
//fin div onglets


//carte


function orientation(pt, elem, angle, zoom) {


	var endlat = 0.0;

	var endlong = 0.0;

	if (elem == 0) {
		endlat = pt.x + zoom * Math.cos(angle / 57.29578);
		endlong = pt.y + zoom * Math.sin(angle / 57.29578);
		var linepath = [new google.maps.LatLng(pt.x, pt.y), new google.maps.LatLng(endlat, endlong)];
	}

	else {
		endlat = pt.x + (zoom - (0.1 * zoom)) * Math.cos(angle / 57.29578);
		endlong = pt.y + (zoom - (0.1 * zoom)) * Math.sin(angle / 57.29578);
		var linepath = [endPath, new google.maps.LatLng(endlat, endlong)];
	}
	var pline = new google.maps.Polyline({

		path: linepath,

		strokeColor: "#0093d1",

		strokeOpacity: 1.0,

		strokeWeight: 3

	});

	pline.setMap(map);

	if (elem == 0) {
		dernier_poly = pline;
		endPath = linepath[1];
		//alert("ok");
	}
	if (elem == 1) {
		dernier_flech1 = pline;

	}
	if (elem == 2) {
		dernier_flech2 = pline;

	}


}

function ajoutMarker(pt) {

	if (dernier_marker != null) {
		dernier_poly.setMap(null);
		dernier_flech1.setMap(null);
		dernier_flech2.setMap(null);
		dernier_marker.setMap(null);
		dernier_info.open(null);
	}
	var location = new google.maps.LatLng(pt.x, pt.y);
	var marker = new google.maps.Marker({
		position: location,
		map: map
	});
	var infowindow = new google.maps.InfoWindow({
		content: localize("%latitude") + " : " + (pt.x).toFixed(5) + " <br> " + localize("%longitude") + " : " + (pt.y).toFixed(5),
		position: location
	});

	infowindow.open(map);
	dernier_point = pt;
	dernier_marker = marker;
	dernier_info = infowindow;

	var z = map.getZoom();
	var tabZoom = new Array(6, 5, 2.5, 4 / 3, 1, 4 / 5, 0.5, 0.3, 0.18, 0.09, 0.05, 0.028, 0.016, 0.008, 0.0045, 0.0025, 0.0016, 0.0009, 0.0005, 0.0003, 0.00018, 0.0001);
	orZoom = tabZoom[z];

	orientation(pt, 0, (azimuth), orZoom);
	orientation(pt, 1, (azimuth + 20), orZoom);
	orientation(pt, 2, (azimuth - 20), orZoom);

}

function load() {

	mode();

	if (isOnline) {
		var latlng = new google.maps.LatLng(48.774, 3.868);

		var myOptions = {
			zoom: 4,
			center: latlng,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};

		map = new google.maps.Map(document.getElementById("map"), myOptions);

		google.maps.event.addListener(map, 'click', function (event) {
			var pnt = { x: event.latLng.lat(), y: event.latLng.lng() };
			calc(document.forms[1], event.latLng.lat(), event.latLng.lng());
			ajoutMarker(pnt);
			document.forms[0].latitude.value = (event.latLng.lat()).toFixed(5);
			document.forms[0].longitude.value = (event.latLng.lng()).toFixed(5);
			codeLatLng(event.latLng.lat(), event.latLng.lng());
		});
		google.maps.event.addListener(map, 'zoom_changed', function () {
			if (dernier_marker != null) {
				ajoutMarker(dernier_point);
			}

		});
	}
}


function codeLatLng(lat, lng) {
	var latlng = new google.maps.LatLng(lat, lng);
	geocoder.geocode({ 'latLng': latlng, 'language': String.locale }, function (results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			if (results[1]) {
				document.forms[0].address.value = results[0].formatted_address;
			}
		}
	});
}
//fin carte

//pour afficher la couleur du spot
function trouveSpot(poly, pt) {

	var ret = new Array;
	var id = "non definit";
	for (var c = false, i = -1, l = poly.latitude.length, j = l - 1; ++i < l; j = i)
		((poly.longitude[i] <= pt.y && pt.y < poly.longitude[j]) || (poly.longitude[j] <= pt.y && pt.y < poly.longitude[i]))
			&& (pt.x < (poly.latitude[j] - poly.latitude[i]) * (pt.y - poly.longitude[i]) / (poly.longitude[j] - poly.longitude[i]) + poly.latitude[i])
			&& (c = !c) && (id = poly.famille);

	ret[0] = c;
	ret[1] = id;
	return ret;
}


function afficherCouleur() {
	document.getElementById('msgSpot').innerHTML = "";
	if (id_spot == "bleu") {
		document.getElementById('msgSpot').innerHTML = "<p align='center'><img src='../images/spots/bleu.png'/></p>";
		isSpot = 1;
	}
	else if (id_spot == "orange") {
		document.getElementById('msgSpot').innerHTML = "<p align='center'><img src='../images/spots/orange.png'/></p>";
		isSpot = 1;
	}
	else if (id_spot == "vert") {
		document.getElementById('msgSpot').innerHTML = "<p align='center'><img src='../images/spots/vert.png'/></p>";
		isSpot = 1;
	}
	else if (id_spot == "violet") {
		document.getElementById('msgSpot').innerHTML = "<p align='center'><img src='../images/spots/violet.png'/></p>";
		isSpot = 1;
	}
	else {
		document.getElementById('msgSpot').innerHTML = localize("%msgSpot");
		isSpot = 0;

	}
}
//fin afficher couleur spot

//mode de connexion

function mode() {
	if (navigator.onLine) {
		imgTestInternet.onload = function () {
			modeStyle(1);
		};
		imgTestInternet.onerror = function () {
			modeStyle(0);
		};
		imgTestInternet.src = "../../servTest.png";
	}
	else {
		modeStyle(0);
	}


}

//fin mode connexion

function imprimer() {
	window.print();
}
