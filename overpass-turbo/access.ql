// Niels Elgaard Larsen
// restaurant without opening hours
[timeout:25];
(
{{geocodeArea:Denmark}}->.searchArea;
  way["highway"="footway"]["access"~"."]["vehicle"!~"."]["motor_vehicle"!~"."](area.searchArea);
);
(._;>;);
out body;
>;
