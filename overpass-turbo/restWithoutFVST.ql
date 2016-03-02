// Niels Elgaard Larsen
// restaurant without opening hours
[timeout:25];
(
{{geocodeArea:Denmark}}->.searchArea;
  node["amenity"="restaurant"]["fvst:navnelbnr"!~"."](area.searchArea);
  way["amenity"="restaurant"]["fvst:navnelbnr"!~"."](area.searchArea);
);
(._;>;);
out body;
>;
