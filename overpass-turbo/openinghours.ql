// Niels Elgaard Larsen
// restaurant without opening hours
[timeout:25];
(
{{geocodeArea:Denmark}}->.searchArea;
  node["amenity"="restaurant"]["opening_hours"!~"."](area.searchArea);
  way["amenity"="restaurant"]["opening_hours"!~"."](area.searchArea);
);
(._;>;);
out body;
>;
