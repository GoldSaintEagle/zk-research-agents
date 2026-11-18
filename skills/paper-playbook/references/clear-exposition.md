# Clear explanations and accurate contribution emphasis

Apply this guidance throughout a paper, including abstracts, captions and
appendices. It controls exposition, not the mathematical scope of a result.

## One main question per sentence

Give each sentence one main explanatory task. Separate distinct problems,
reductions, implementation obstacles and conclusions when each needs background.
A short, obvious consequence or closely related pair can remain in one sentence;
there is no word limit or ban on compound sentences. A semicolon does not supply
a missing explanation.

Name the concrete operation before its difficulty. For example, say which random
linear combination of commitments is checked before discussing its certificate.
Call the coefficients random or challenge-derived only when the protocol makes
them so. Distinguish those combination coefficients from certificate-polynomial
coefficients. Do not compress the original group equation, its algebraic reduction,
and a later base-field/scalar-field implementation issue into one unexplained clause.

An abstract needs the essential connecting step, not every equation. A technical
overview or construction supplies the actual intermediate objects and validity
conditions. If the reduction cannot be explained clearly within the space, omit
secondary implementation detail rather than deleting the link that explains it.

## Follow the objects through the argument

Write the substantive chain as A → operation → B → consequence or remaining
obstacle → C. Each unit should use an object or result just introduced, explain
what changes, and supply what the next unit needs. Explain a new obstacle as a
consequence of the current method before proposing another technique. For a
genuinely independent branch, signal the change of question and its relevance.
Do not manufacture a causal connection simply to make the prose flow.

Phrases such as “we reduce this to polynomial checks” need an intervening reason:
what encodes the original relation, which equations are checked, and what makes
that encoding valid? How much detail is needed depends on the section. First-use
definitions and clear antecedents matter more than repeating “therefore”.

### Public-source illustration: elliptic-curve group equations

This illustrates exposition using the principal-divisor route in Eagen,
*Zero Knowledge Proofs of Elliptic Curve Inner Products from Principal Divisors
and Weil Reciprocity*, [§§2–3](https://eprint.iacr.org/2022/596.pdf). It is not a
mandatory construction or a new contribution attributed to another manuscript.

An explanatory order is:

1. Identify the commitment equation and the group arithmetic required to check it.
2. Explain how the **actual** method reduces the weighted equation to point lists
   whose group sums must vanish; give the decomposition in the overview if needed.
3. Explain the representation: such a list corresponds to a curve function with
   the listed zeros, including multiplicities, and the prescribed pole at infinity.
   On a curve y²=g(x), write that function as A(x)+yB(x); the curve equation explains
   this form. Degree/pole and other admissibility conditions remain necessary.
4. Explain which polynomial identities certify the representation. A norm identity
   alone can lose the choice between a point and its negative; do not silently
   replace the complete check by that identity alone.
5. Only then introduce an implementation issue, if relevant: checking these
   base-field identities inside a scalar-field recursive circuit incurs nonnative
   arithmetic and requires binding the same coefficient data.

For an abstract, a compact bridge can say that the method represents zero-sum
point lists by curve functions and checks polynomial identities for those
functions. The overview explains the reduction and the construction states its
exact conditions. Do not copy private manuscript sentences into this toolkit.

## Separate a new result from standard protocol steps

Classify ingredients in working notes as reused, adapted or new. Contributions
name the supported new property, theorem or improvement relative to prior work.
Routine commitments, committing before a challenge, Fiat–Shamir, standard
serialization and ordinary use of sumcheck are not contributions merely because
the construction uses them. Keep them out of contribution bullets and avoid
giving them headline space in abstracts or introductions.

If an auxiliary relation or combination of standard tools is genuinely new,
identify the precise changed relation/property and its proved benefit. Do not
attribute that novelty to the generic commit-then-challenge order. Necessary
standard steps still appear in the executable construction and proof interface;
de-emphasizing a step does not mean removing its checks or costs.

Where an interactive presentation is appropriate, describe that protocol first.
When justified, a short subsequent sentence can state that Fiat–Shamir makes it
noninteractive, with the model and a pointer to the supporting security analysis.
Give exact transcript absorption, statement binding, domains and encoding once
in the protocol specification or referenced appendix, rather than repeatedly
selling their chronology as a technique.

The short compilation sentence does not establish security by itself. Preserve
compiler preconditions and material extra assumptions; an ideal-random-oracle
argument does not automatically prove a fixed-hash recursive circuit secure.
If these obligations are unproved, describe the transformation and its conditional
status accurately. A genuinely new Fiat–Shamir theorem or nonstandard challenge
schedule may be a contribution, but only its demonstrated delta merits emphasis.

## Editing check

- Can the reader name the operation before encountering its cost or certificate?
- Does each non-obvious reduction expose the intermediate object and its role?
- Does each sentence mainly answer one question, with prerequisites already given?
- Does the next issue follow from the current result, or have an explicit bridge?
- Do contribution statements identify new results rather than standard steps?
- After compression, are protocol order, checks, costs and security premises intact?
