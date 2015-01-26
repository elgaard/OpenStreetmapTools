// Niels Elgaard Larsen:
// finds danish  address nodes on ways
node
  ['osak:identifier'~'']
  ({{bbox}});
 rel(bn)->.x;
way(bn);
node(w)['osak:identifier'~''];
out;
