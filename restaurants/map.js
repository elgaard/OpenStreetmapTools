var POImap = {};

POImap.init = function () {
  var attr_osm = 'Map data &copy; <a href="//openstreetmap.org/">OpenStreetMap</a> contributors',
      attr_overpass = 'POI via <a href="//www.overpass-api.de/">Overpass API</a>';

  var osm = new L.TileLayer('//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: [attr_osm, attr_overpass].join(', ')});

  var mapbox=L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'user.yyyyy',
    accessToken: 'pk.xxxxxxxxxxxxxxxxxxxxxxx'
  });
		
  var map = new L.Map('map', {
    // Default Denmark
      center: new L.LatLng(56,12.5),
      zoom: 8,
      layers: osm,mapbox
  });

  map.getControl = function () {
    var ctrl = new L.Control.Layers({
	'OpenSteetMap': osm,
	'Mapbox': mapbox
    });
    return function () {
      return ctrl;
    };
  }();
  map.addControl(map.getControl());

  L.LatLngBounds.prototype.toOverpassBBoxString = function (){
    var a = this._southWest,
        b = this._northEast;
    return [a.lat, a.lng, b.lat, b.lng].join(",");
  };

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
      var center = new L.LatLng(position.coords.latitude, position.coords.longitude);
      map.setView(center, 10);
    });
  }
  POImap.map = map;
  return map;
};

