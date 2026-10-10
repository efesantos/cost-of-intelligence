# Prior-Art Log (Task B-13)

Final prior-art pass before submission. Purpose: confirm that none of the Stream B novelty claims
(a)–(d) in `novelty.md` have been published, and to catch any new citations of the anchor paper.

**Overall status: RUN on 2026-10-10.** The searches were run with an AI research assistant using web
search and arXiv-restricted search. Google Scholar refused automated access and Semantic Scholar
returned errors, so OpenAlex and arXiv stood in for them. **One manual step remains:** the Google
Scholar "Cited by" check for the anchor paper.

## How to use

For each row: run the query on the named source, record the date, summarise the outcome (what was
found / not found), and record the action (e.g. "no conflict — claim stands", "downgrade claim (c)
to 'we extend'", "add citation X"). Add new rows for any follow-on queries the search suggests.

## Log

| date | query | source | outcome | action |
|------|-------|--------|---------|--------|
| 2026-10-10 | `token affordability index` | web search; arXiv-only search | Token *price* indices only (Silicon Data, BenchLM, others) and unrelated "token efficiency" work. No work-minutes or wage-based token index. | no conflict — claim (a) stands |
| 2026-10-10 | `LLM cost wages developing countries` | web search; arXiv-only search | Sathish et al. 2024, LLeMpower (arXiv:2404.09356): a $20/month subscription against income by country. No tokens or fertility. | add citation (claim a) |
| 2026-10-10 | `tokenizer premium adoption` | web search; arXiv-only search | Token-count studies only (e.g. Ovcharov 2026, arXiv:2605.24718), none with an adoption link. | add Ovcharov (claim d) |
| 2026-10-10 | `citations of 2606.24460 since Jul 2026` | OpenAlex (record W7165759401, cited-by count 0); Hugging Face Papers; reference lists of six later papers; web search | No citing work found. Google Scholar not reachable. | none; **re-run Scholar "Cited by" by hand** |
| 2026-10-10 | `language tax LLM pricing low-income countries` | web search | Solatorio et al. 2024 (arXiv:2410.10665): FLORES-200 plus World Bank income groups; per-language cost premium, no per-country index or wages. | add citation (claims a, d) |
| 2026-10-10 | `do all languages cost the same` (follow-up from the anchor's references) | ACL Anthology; arXiv | Ahia et al. 2023 (EMNLP; arXiv:2305.13707): API cost by language, with the Human Development Index as an affordability proxy. | add citation (claims a, d) |
| 2026-10-10 | `tokenization disparity adoption AI usage by country`; `language AI adoption country regression GDP per capita` | web search (standard and extended) | Misra et al. 2025 (arXiv:2511.02752): low-resource-language countries have about 20% lower AI-user share after socio-economic controls. Daepp & Slaughter 2026 (arXiv:2605.30685): usage patterns by country income and language. Neither has a tokenizer, price or wage measure. | add Misra; narrow claim (c) to "we extend Misra et al." |
| 2026-10-10 | `AI affordability share of income GNI per capita` | web search | ITU, *The affordability of ICT services 2024* (2025): price ÷ monthly GNI per capita. Our Tier-2 work-minutes = 104 × this ratio. | add citation (claim a, method lineage) |
| 2026-10-10 | `"intelligence wage"`; `"real tokens per dollar"`; `"intelligence exchange rate"` | web search | Blog posts about an LLM's own "hourly rate", a different concept. Ashenfelter 2012 ("Big Macs per hour") is the real-wage lineage. | no conflict — claim (b) stands; cite Ashenfelter |
| 2026-10-10 | `Portuguese tokenization cost LLM Brazil Angola Mozambique`; `Spanish Portuguese tokenizer tax Latin America affordability` | web search; arXiv-only search | Portuguese tokenizer papers and cost ledgers; nothing on Lusophone *affordability*. | affordability cut (d) stands; fertility part downgraded |

## Sign-off

- [x] All four pre-filled queries run and outcomes recorded (2026-10-10).
- [x] Follow-on queries suggested by results added and run.
- [x] Each novelty claim (a)–(d) in `novelty.md` reconciled: (a) and (b) kept; (c) narrowed with a
      citation added; (d) narrowed, variant-level claim withdrawn.
- [x] Novelty tags in `novelty.md` updated from "[INFERENCE until final prior-art check B-13]" to
      final wording.
- [ ] Google Scholar "Cited by" check for arXiv:2606.24460 run by hand.
- [ ] Signed / dated by Elmer before submission: `{{date}}`.
