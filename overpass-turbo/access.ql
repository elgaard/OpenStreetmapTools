// Niels Elgaard Larsen
// path,footway,cycleway that allow vehicles
[timeout:40];
(
{{geocodeArea:Denmark}}->.searchArea;
  way["highway"="path"]["access"~"."]["access"!="no"]["vehicle"!~"."]["motor_vehicle"!~"."](area.searchArea);
  way["highway"="footway"]["access"~"."]["access"!="no"]["vehicle"!~"."]["motor_vehicle"!~"."](area.searchArea);
  way["highway"="cycleway"]["access"~"."]["access"!="no"]["vehicle"!~"."]["motor_vehicle"!~"."](area.searchArea);

);
(._;>;);
out body;
>;
