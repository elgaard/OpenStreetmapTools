// Niels Elgaard Larsen
// All restaurants, cafe, fast_food
[timeout:120];
(
  node["amenity"="restaurant"]({{bbox}});
  way["amenity"="restaurant"]({{bbox}});
  node["amenity"="cafe"]({{bbox}});
  way["amenity"="cafe"]({{bbox}});
  node["amenity"="fast_food"]({{bbox}});
  way["amenity"="fast_food"]({{bbox}});
  node["amenity"="bar"]({{bbox}});
  way["amenity"="bar"]({{bbox}});
  node["amenity"="pub"]({{bbox}});
  node["shop"="farm"]({{bbox}});
  way["amenity"="pub"]({{bbox}});
);
(._;>;);
out center;
>;
