# Integer polygons

The supplied polygons have integer vertices, given in boundary order. They are
simple, have no holes, and may be concave. For each polygon find its area A, the
number B of integer points on its boundary (vertices included once), and the
number I of integer points strictly inside it.

Investigate a relation among A, B, and I. Test it on every supplied polygon and
try to explain its general scope. A formula recalled from memory still needs
an argument and a check against these inputs. State any assumptions needed to
extend the relation beyond these examples. Include reproducible code for any
counts, and discuss one different representation or approach you actually tried
or evaluated, including any failed direction.

Follow the common output format. Evidence is
`{"polygons": [{"id": "P1", "twice_area": INTEGER, "boundary": INTEGER,
"interior": INTEGER}, ...]}`. Report all five polygons. The status refers to
your general relation, whose argument belongs in report.md.
