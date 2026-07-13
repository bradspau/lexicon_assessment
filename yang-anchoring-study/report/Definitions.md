# Semantic Definitions: Intensional, Extensional, and Circular‑Tautological

## ISO 704: The Source Standard

### What It Is
ISO 704, *Terminology work, Principles and methods*, is the international standard that defines what counts as a properly-formed definition in technical terminology work. It is the formal basis for the intensional/extensional/circular-tautological distinctions below, not an invention specific to this document, professional terminologists, standards bodies, and ontology engineers use it as the baseline for judging whether a glossary entry is doing real definitional work.

### The Core Requirement: Genus + Differentia
ISO 704's central rule is that a proper (intensional) definition must state:
1. the **genus**, the broader category the concept belongs to, and
2. the **differentia**, what distinguishes it from other members of that category.

"A prime number is a number [genus] divisible only by 1 and itself [differentia]." Drop either half and the definition stops doing its job: no genus and there is no category to reason within; no differentia and the concept cannot be told apart from its siblings.

### Why Use an External Standard Rather Than an Ad Hoc Rubric
A homegrown checklist (is this description longer than five words, does it contain a verb) is easy to game and hard to defend. ISO 704 gives a rubric with actual epistemic weight behind it: a definition graded against it either does or does not meet a standard that terminology professionals are independently accountable to. That matters most when the finding is negative, "49% of these descriptions are tautological" is a much stronger claim when "tautological" is a term of art from an international standard than when it is a private judgment call.

---

## Intensional

### Definition
An intensional definition describes a concept by its **meaning**, **rules**, or **criteria** — the properties that make something what it is.

### Key Characteristics
- Specifies necessary and sufficient conditions.
- Supports inference, reasoning, and generalization.
- Stable across contexts and implementations.
- Enables agents to classify new instances without enumerating them.

### Example
A **prime number** is a number divisible only by 1 and itself.

### Why It Matters (Ontology & A2A Context)
Intensional definitions are the backbone of semantic interoperability.  
They allow:
- agents to reason safely,
- ontologies to infer new facts,
- YANG vocabularies to constrain meaning,
- A2A protocols to share conceptual definitions rather than brittle lists.

Without intensional meaning, agents cannot align on concepts or perform reliable reasoning.

---

## Extensional

### Definition
An extensional definition describes a concept by **listing all of its members** or examples.

### Key Characteristics
- Concrete and example‑based.
- Useful for small, closed sets.
- Does not explain underlying meaning.
- Cannot generalize to new or unseen instances.

### Example
Prime numbers under 10 are **{2, 3, 5, 7}**.

### Why It Matters (Ontology & A2A Context)
Extensional definitions are brittle in dynamic domains like telecoms or multi‑agent systems.  
They:
- cannot support inference,
- cannot scale,
- break when new instances appear,
- fail to provide shared conceptual grounding.

Agents relying only on extensional meaning will misclassify, misalign, or fail to interoperate.

---

## Circular‑Tautological

### Definition
A circular‑tautological definition is **self‑referential** and **non‑informative**.  
It explains a term using the term itself or repeats the same idea without adding meaning.

### Key Characteristics
- Circular: definition depends on itself.
- Tautological: true only because it repeats the same concept.
- Cannot classify new instances.
- Cannot be falsified or operationalized.
- Provides no intensional criteria.

### Example
A **router** routes.

### Why It Matters (Ontology & A2A Context)
Circular‑tautological definitions are dangerous in semantic systems because they:
- block reasoning,
- hide semantic gaps,
- undermine ontology engineering,
- produce brittle YANG schemas,
- cause agent hallucination or unsafe behavior in A2A protocols.

They create the illusion of meaning without providing any operational semantics.

---

## Empty / Boilerplate

### Definition
An empty or boilerplate description contains no definitional content at all, either because the field is genuinely blank, or because it holds placeholder text that was never replaced with real content.

### Key Characteristics
- Present in form (the field exists, may even be a non-empty string) but absent in substance.
- Often a generation artifact, auto-populated by tooling and never edited by a human.
- Impossible to distinguish from a template failure without checking the source.

### Example
The literal string `"none"` used as a description value, confirmed as real, unedited source text rather than a data-extraction bug.

### Why It Matters (Ontology & A2A Context)
This is the one failure mode intensional/extensional/circular-tautological doesn't capture on its own: a tautological definition at least *references* the concept ("a router routes"). Boilerplate doesn't even do that, it's a placeholder that was never filled in. An agent parsing this gets nothing to reason over, and a naive "is the field non-empty" check will count it as present, hiding the problem from anyone not specifically looking for it.

---

## Combined Insight

- **Intensional** definitions provide meaning and enable reasoning.  
- **Extensional** definitions list examples but cannot generalize.  
- **Circular‑tautological** definitions provide no meaning at all.  
- **Empty/boilerplate** definitions provide no content at all, present in form only.  

For ontologies, YANG vocabularies, and A2A protocols, **intensional definitions are mandatory** for safe, interoperable agent communication. All four categories above are ISO 704's formal vocabulary for saying so, not an ad hoc scheme invented for this document.

---

## Applied: What This Looked Like in Practice

These distinctions were used to grade a real sample of network-configuration data-model descriptions (YANG, from IETF and ONF TAPI), 150 nodes across two vocabularies, scored against the ISO 704 rubric plus the Empty/Boilerplate category above.

**Result: only ~44 to 45% of descriptions in either corpus were genuinely intensional.** The two corpora failed in different, corpus-specific ways:
- **IETF's failure mode was tautology.** ~49% of its descriptions just restated the node's own name, present in form, absent in substance. Critically, IETF had **0% empty fields**, so a simple "is it blank" check would have missed almost half the actual problem.
- **TAPI's failure mode was literal boilerplate.** ~23% of its descriptions were the unedited string `"none"`, a leftover from automated code generation, never replaced with real content.

This is the concrete version of the abstract point above: neither corpus's problem was visible from field presence alone. It took a standard with a real definition of *definitional* to surface it. See `report/FINDINGS.md` §1 for the full audit.

---

## Gold Standard

### Definition
A gold standard is a hand-verified set of correct answers used to measure whether a system's outputs are accurate. It is not a definition of a concept itself, it is the accepted ground truth a model's predictions are graded against, the mechanism by which claims about definitional quality get tested rather than merely asserted.

### Key Characteristics
- Built by an expert from primary sources, independently of the system being tested.
- Serves as the sole basis for scoring accuracy, precision, and recall, an accuracy number is only as meaningful as the answer key behind it.
- Can itself contain errors, and should be revisited when a system's disagreement with it is unusually consistent or well-evidenced, rather than assumed infallible.
- Distinct from a "silver standard" (labels generated automatically, or with lower confidence, rather than hand-verified against source material).

### Example
A row stating that the YANG node at `.../node/termination-point` corresponds to lexicon entry `LEX-002` ("link-termination-point"), hand-labelled by reading the actual IETF specification for that node, before any AI ever attempted to classify it.

### Why It Matters (Ontology & A2A Context)
Without an independently-established gold standard, there is no way to distinguish a system that reasons well from one that merely sounds confident, every accuracy claim needs something external to be measured against. But a gold standard is only as trustworthy as the process that built it: if a label is wrong, a system that disagrees with it is being penalized for being right, not rewarded for reasoning correctly. Treating a gold standard as immune to revision, rather than as a working hypothesis subject to the same scrutiny as the system under test, risks mistaking a labelling error for a reasoning failure, and drawing the wrong conclusion from a correct result.

---

## Definitional Anchoring (Grounding)

### Definition
Definitional anchoring is the use of a shared, external reference (a lexicon or ontology) as a common point that different, independently-named components can each be mapped onto, so that two items with completely different labels can be recognised as the same underlying concept.

### Key Characteristics
- The reference itself belongs to neither source vocabulary, it sits outside both, as neutral common ground.
- Grounding is achieved only when a component is correctly mapped to the reference by meaning, not when it merely carries a label.
- Requires reading and reasoning over meaning, not matching surface vocabulary, a synonym lookup can simulate grounding for cases its author already anticipated, but does not perform it.
- Enables genuine interoperability: once two differently-named things are anchored to the same reference entry, a system can treat them as identical for reasoning purposes.

### Example
IETF's `termination-point` and TAPI's `NodeEdgePoint` share no vocabulary at all, but both correctly anchor to the same lexicon entry ("link-termination-point") once their actual descriptions, "a termination point can terminate a link" and "the NEPs belonging to / owned by this Node", are read and understood rather than pattern-matched.

### Why It Matters (Ontology & A2A Context)
Grounding is the prerequisite for any system that needs to reason across standards, vendors, or agents that do not share a vocabulary. A lexicon or ontology only provides commonality if something is actually anchoring components to it by meaning, a name-matching shortcut can only ground the specific name pairs its author already knew about in advance, and fails silently on any naming convention it has not seen. Genuine anchoring, achieved by reading a component's real definition and reasoning about what it means, generalises to naming conventions never seen before, which is what makes it valuable for A2A protocols and ontology engineering rather than a one-off mapping table.
