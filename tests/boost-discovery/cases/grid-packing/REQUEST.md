# Six separated locations

Choose six distinct points from the integer grid {0,1,2,3,4,5} squared. Maximize
the minimum squared Euclidean distance between any pair. Start by checking the
feasible arrangement (0,0), (0,2), (0,4), (2,0), (2,2), (2,4).

Investigate better arrangements. You can use exhaustive search, geometric
bounds, local search, reformulations, or another approach. Compare your best
result with the supplied baseline and investigate at least one substantive
alternative approach or representation. Save an informative failed attempt or
negative result if one occurs; do not invent one. Explain what your effort has
and has not established about optimality. A useful partial result is acceptable.

Follow the common output format. Evidence is
`{"points": [[x,y], ...], "min_distance_squared": INTEGER}`. Exactly six points
are required. Put search coverage, any bound, experiment records, reproduction
commands, and arguments in report.md. Claims apply to this finite integer grid;
continuous packing or larger grids require additional evidence.
