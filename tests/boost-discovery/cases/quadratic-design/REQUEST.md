# A small measurement design

Six measurements will fit y = a + b*x + c*x^2 with independent equal-variance
errors. Choose each x from {-3,-2,-1,0,1,2,3}; repeated x values are allowed and
count as separate measurements. For row v(x)=(1,x,x^2), define
M = sum v(x) v(x)^T over the six measurements. Maximize det(M).

Check the baseline design [-3,-2,-1,1,2,3]. Explore improvements, explain why
your choices help, and investigate at least one substantive alternative
representation or search strategy. Retain informative failed or negative
experiments when they occur. State whether the result is merely a candidate,
an optimum on this finite domain, or a conclusion with a wider justified scope.
Report the actual search coverage and cost. A useful partial result is acceptable.

Follow the common output format. Evidence is
`{"xs": [INTEGER, ...], "determinant": INTEGER}` with exactly six entries.
Include reproducible local computation and your argument in report.md.
