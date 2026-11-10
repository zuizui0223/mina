# English manuscript and supplement design

## Purpose

Turn the completed Signy diet analysis into two coherent, editable English manuscripts with the existing figures and tables embedded. The central finding remains the local association between sea ice and dietary separation among three sympatric penguins. Gentoo meal components, the Palmer transfer comparison and conditional future scenarios develop that finding without changing its estimand or evidential scope.

## Decisions

- Reuse the Japanese manuscript and supplement at commit `a0b678bad6b8bd57d1f73e687aa6c415416aebb3`, the verified references and the underlying saved numerical outputs. Do not refit models or search for additional significant results.
- Produce `MANUSCRIPT_EN.md`, `SUPPLEMENT_EN.md`, `Signy_diet_manuscript.docx` and `Signy_diet_supplement.docx` in `outputs/diet_niche_english_v1`. The Markdown files are editable source; Word documents contain the complete text, actual figures and readable tables.
- Keep main figures 1–4 and supplementary figures S1–S2. Keep main tables 1–3 and supplementary tables S1–S2; integrate the already reported pair comparison and component values as clearly labelled text or additional tables without silently changing original identifiers.
- Use a plain academic manuscript design: Letter portrait, black headings, readable serif body text, intentional table widths, editable native equations and page numbers. No invented authors, affiliations, funding, permits, conflicts or journal requirements. Author-supplied declarations remain clearly unfilled.
- Target a concise abstract of at most 250 English words and a complete main text. Retain all numerical support and important uncertainty in the main text or supplement.
- Keep scientific notation and response definitions exact: three-species D uses fish plus crustacean mass; the Palmer pair comparison and Gentoo c/m use the four-food-group denominator; p uses valid stomach counts. The empirical identity m = p c does not imply that independently fitted curves multiply.
- Preserve nine climate seasons, the 772-stomach cohort and 73-stomach Gentoo subset, exploratory selection, permutation exchangeability, temporal dependence, sampling-date versus breeding-stage limits, Palmer non-transferability and coefficient-only scenario intervals.
- Preserve all 12 climate conditions, withhold the one unsupported mean condition, retain the BCC near-zero historical-ice issue and the distinction between a response at future mean SIC and mean future annual diet.

## Approaches considered

1. Full English manuscript plus supplement and embedded figures: chosen by the assistant under the user's instruction to continue autonomously; completes a concrete missing research deliverable.
2. Another simultaneous time–diet–land model: not chosen because the Gentoo diet years have no overlap with the available same-camera timing series, and earlier feasible bridges have already been analysed.
3. Figure-only reorganization: useful but leaves the full English text absent, so it is included within the chosen deliverable rather than becoming a separate project.

## Source and editing boundaries

The Japanese scientific text and all existing numerical/figure files are inputs and remain unchanged. Update only their README entry points and the current-status paragraph in the climate-niche synthesis after the English package is ready. The existing manuscript is the reference for scope. The known 14-year Adélie/chinstrap hatching-to-sampling comparison informs the interpretation of sampling dates; it does not add missing Gentoo phenology or a new independent climate test.

Resolve the model-data citation details from official source records when available, keeping precise experiment, member and version information in the supplement. Unresolved citation metadata must remain explicit rather than be invented.

## Verification and delivery

Check source hashes, all tables against saved source values, references and figure identity, abstract length, rendered equations, complete text transfer and local links. Independently review scientific fidelity. Render and visually inspect every page of both Word documents. Reuse the last complete analysis test result for unchanged analysis code; no new software unit tests are warranted for reversible document formatting. Commit the completed package once and publish to the existing Draft PR206 with an expected-head lease and identical-tree verification. The user has already authorized this continuation and branch publication; no repeated permission step is needed.
