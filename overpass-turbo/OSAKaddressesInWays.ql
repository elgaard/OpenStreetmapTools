// Niels Elgaard Larsen:
// finds danish  address nodes on ways
node
  ['osak:identifier'~'']
  ({{bbox}});
way(bn);
node(w)['osak:identifier'~''];
out;
