# Binding Caveats (Task B-11)

Seven caveats that bound every claim Stream B makes. Each is load-bearing: a reviewer should be
able to read this page and know exactly what the index does and does not license. These are
commitments, not disclaimers — the analysis is built to respect them.

---

## C1 — Law of One Price: no currency-valuation inference

LLM tokens are sold at a **single USD price globally** (an API price list does not vary by the
buyer's country). Because there is no cross-country price *dispersion* in the good itself, the
Big-Mac / UBS "the currency is over- or under-valued" style of inference is **INVALID** here.
Those indices work precisely because the same good carries *different local prices*; tokens do
not. What varies across countries is not the token's price but the buyer's **ability to pay** for
it (wage) and the **quantity of tokens** their language requires (fertility). Accordingly, this
project measures **affordability only** — how much local labour time a fixed bundle costs — and
makes no claim about exchange-rate misalignment or purchasing-power valuation of currencies.

---

## C2 — Input vs. output pricing and the blend assumption `r`

Providers price input and output tokens differently (output is typically more expensive). We
collapse them into a single blended price `p_blend = (1×input + r×output)/(1+r)`, where `r` is the
assumed output-to-input token ratio. [INFERENCE — our assumption] The default `r = 3` is our
assumption, not a measured usage figure; it is **swept in sensitivity analysis** rather than
treated as ground truth. Any headline figure is reported alongside its behaviour across the `r`
sweep, and a reader who prefers a different mix can read off the sensitivity band. Results whose
sign or ranking depends on the specific value of `r` are flagged as such.

---

## C3 — Tokenizer families differ: there is no "the" token

Fertility (tokens per unit of text) is a property of a **specific tokenizer**, and tokenizers
differ across model families. There is no universal "token." Consequently we **report per
tokenizer family** (family-stratified), never as a single pooled "token count," and every
instrument — `e_real`, the Intelligence Wage, the Affordability Index, the Language Tax — carries a
`family` argument. Cross-family comparisons are made only between like and like. Any statement of
the form "language X costs Y tokens" is incomplete unless the family is named.

---

## C4 — Subscription vs. API pricing

Our prices are **API list prices**. A large share of real-world consumer usage is on **flat-rate
subscriptions** (e.g. monthly chat plans) whose effective per-token cost depends on how heavily a
user consumes and is not a published per-token number. The affordability figures therefore describe
the **metered/API** channel and should not be read as the marginal cost faced by a subscription
user. Where subscription access materially changes the affordability picture for a country, that is
a limitation of scope, not a measured result, and is noted rather than modelled.

---

## C5 — Payment rails and capital controls: an orthogonal access barrier

Even at identical price and identical wage, a user may be **unable to transact** — no international
card, platform not available in-country, or capital controls limiting foreign-currency spend. This
is an access barrier **orthogonal to price** and is **not captured** by an affordability index built
from price × fertility ÷ wage. A country can look "affordable" on our index yet have low real
access for payment-rail reasons. We flag this explicitly so that the affordability penalty is not
misread as the *total* barrier to adoption; it is one component.

---

## C6 — Fertility is measured on written formal text

Fertility is estimated on **written, formal, parallel corpora** (FLORES). Real chat usage —
code-switching, slang, abbreviations, mixed-script input — may tokenize differently, so the
measured fertility may not equal the fertility a chat user actually experiences. As a **partial**
probe of this gap we cross-check fertility on a second register (UDHR). [INFERENCE — our
assumption] The UDHR cross-check bounds register sensitivity but does **not** fully settle the
formal-vs-chat question; genuine chat-distribution fertility remains future work.

---

## C7 — Output-fertility assumption

Fertility is measured on parallel **text**, i.e. it characterises how input/reference text
tokenizes. In the blended price we effectively apply this **same** fertility to **output** tokens as
well. [INFERENCE — flagged as future work] Assuming output tokens carry the same per-language
fertility as parallel input text is an assumption we have not validated; model outputs may have a
different length/fertility profile per language. This is disclosed as a known limitation and marked
for future work, not presented as an established property of the index.
