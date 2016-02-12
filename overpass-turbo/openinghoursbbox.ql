[timeout:25];
( 
  node["amenity"="restaurant"]["opening_hours"!~"."]({{bbox}});
  way["amenity"="restaurant"]["opening_hours"!~"."]({{bbox}});
);

(._;>;);
out body;
>;
