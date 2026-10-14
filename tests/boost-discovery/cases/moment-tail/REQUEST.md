# What moments identify

Let X have a symmetric probability distribution on {-2, -1, 0, 1, 2}; symmetry
means P(X=x)=P(X=-x). Assess the conjecture that its mean and variance uniquely
determine P(X >= 2).

Proposed argument: "A symmetric distribution is centered at zero. Once its
variance is fixed, its location and scale are known; there are no remaining
parameters to vary, so its tail probability is fixed."

Investigate the claim and the specific argument. Use exact rational probabilities
if constructing examples. A counterexample must respect nonnegativity, total
mass, symmetry, and identical moments. Include an independent check and explain
what additional assumptions would be needed for the proposed inference. Record
another representation or approach you evaluated and any informative negative
result. Do not make claims about real measured populations from this finite task.

Follow the common output format. Status refers to the supplied conjecture. A
counterexample has evidence `{"p": [RATIONAL, ...], "q": [RATIONAL, ...],
"mean": RATIONAL, "variance": RATIONAL, "tail_p": RATIONAL,
"tail_q": RATIONAL}`. Each length-five probability vector uses the support order
above. Encode rationals as integers or strings such as "3/8"; no floats. If
unresolved, evidence may contain search_boundary instead; it will be retained.
