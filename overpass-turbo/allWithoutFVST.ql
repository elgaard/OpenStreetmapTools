// Niels Elgaard Larsen
// restaurant, cafe, fast_food in Denmark without opening hours
[timeout:125];
(
{{geocodeArea:Denmark}}->.searchArea;
  node["amenity"="restaurant"]["fvst:navnelbnr"!~"."](area.searchArea);
  way["amenity"="restaurant"]["fvst:navnelbnr"!~"."](area.searchArea);
  node["amenity"="cafe"]["fvst:navnelbnr"!~"."](area.searchArea);
  way["amenity"="cafe"]["fvst:navnelbnr"!~"."](area.searchArea);
  node["amenity"="fast_food"]["fvst:navnelbnr"!~"."](area.searchArea);
  way["amenity"="fast_food"]["fvst:navnelbnr"!~"."](area.searchArea);
);
(._;>;);
out body;
>;
