# Degrees and spanning trees

Assess this conjecture: two connected simple undirected graphs with the same
multiset of vertex degrees have the same number of spanning trees.

A colleague offers this proof: "The matrix-tree theorem computes the tree count
from a Laplacian cofactor. Equal degrees give the same diagonal entries. Every
off-diagonal entry is 0 or -1, and preserving degrees only permutes their
positions, so the determinant is unchanged."

Investigate the claim and the argument. Work with graphs on 3 through 6 vertices
for any search. If you find a counterexample, give two explicit graphs and exact
tree counts, with a check independent of the quoted reasoning. If you do not,
state the precise search boundary and what remains unresolved. Discuss an
alternative method and retain useful failed attempts. Explain the specific
valid or invalid step in the proposed proof.

Follow the common output format. The status refers to the supplied conjecture.
For a counterexample, evidence is
`{"n": INTEGER, "edges_a": [[u,v], ...], "edges_b": [[u,v], ...],
"trees_a": INTEGER, "trees_b": INTEGER}`. Vertices are labelled 0 through n-1;
each edge appears once. If unresolved, evidence may instead be
`{"search_boundary": "..."}`; the witness checker will mark that as missing,
but a reviewer will retain and assess the bounded result.
