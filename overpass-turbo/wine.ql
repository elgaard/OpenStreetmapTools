[out:json][timeout:25];
(
  node["amenity"="restaurant"]({{bbox}})['drink:wine'~'served'];
  way["amenity"="restaurant"]({{bbox}})['drink:wine'~'served'];
);
out body;
>;
out skel qt;
