# Ecology Article cross-scale — author metadata handoff v0.1

**Purpose:** This is the only remaining human-input gate before the canonical Ecology Article can be regenerated as an author-complete Main Document.

Do **not** commit completed personal contact metadata to the public repository unless every author explicitly agrees. Copy `submission/ECOLOGY_METADATA_TEMPLATE.json` to an untracked private file and fill that copy.

## Required confirmations

### 1. Author list and order

Confirm the exact publication-order author list. The same names and order must be used in:

- the private metadata JSON;
- the Ecology Main Document title page;
- ScholarOne;
- Supporting Information author line.

Do not add or remove an author only for submission convenience.

### 2. Affiliations

For every author, confirm:

- department / unit;
- institution;
- city;
- state or province if applicable;
- country;
- present address if required.

Map each author to one or more affiliation IDs in the private metadata JSON.

### 3. Corresponding author

Choose exactly one corresponding author and confirm the submission email address.

### 4. Funding

Confirm all funding agencies, grant numbers and required funder wording. If there was no external funding, use an explicit author-approved statement rather than leaving the field unresolved.

Funding information must also be entered in ScholarOne.

### 5. Additional acknowledgments

Confirm any acknowledgments beyond the already frozen public-data-provider and AI-use acknowledgments.

The generated Main Document already acknowledges:

- Palmer Station Antarctica LTER;
- British Antarctic Survey / NERC UK Polar Data Centre;
- Antarctic Penguin Biogeography Project contributors;
- OpenAI ChatGPT (GPT-5.6 Sol) with the frozen disclosure wording.

### 6. Author Contributions

Provide an all-author-approved CRediT-style contribution statement.

### 7. Conflict of Interest

Provide an all-author-approved competing-interests statement. Do not assume “none” without confirmation.

### 8. AI-tool inventory

Confirm whether OpenAI ChatGPT was the only AI tool used beyond spelling/grammar/general editing.

- If yes, set `ai_tool_inventory_confirmed=true` and leave `additional_ai_tools=[]`.
- If not, list every additional tool in the private metadata JSON so the disclosure can be completed.

### 9. Overlap / dual publication

Confirm the final statement for the ScholarOne Dual Publication field.

The repository contains older working manuscript lines, but only one manuscript may be under consideration. If accurate after author confirmation, the statement should explain that older repository drafts were working documents and were not separately submitted.

If any overlapping paper is published, in press, submitted or soon to be submitted, disclose it explicitly and follow ESA’s overlap-file instructions.

### 10. ORCID

Collect ORCID IDs if requested during ScholarOne submission.

## Private metadata workflow

1. Copy:
   `submission/ECOLOGY_METADATA_TEMPLATE.json`
   to an untracked local file, e.g.:
   `private/ecology_cross_scale_metadata.json`.

2. Fill all author-controlled fields.

3. Run the metadata gate:
   `python -m mina.ecosphere_submission_metadata --metadata private/ecology_cross_scale_metadata.json --require-complete`

4. Regenerate the author-complete Main Document:
   `python scripts/build_ecology_cross_scale_submission_docx.py --manuscript submission/MANUSCRIPT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md --bibliography docs/REFERENCES_V6.bib --captions submission/FIGURE_CAPTIONS_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md --metadata private/ecology_cross_scale_metadata.json --require-complete-metadata --out build/Ecology_Article_Cross_Scale_SUBMISSION.docx`

5. Render that author-complete DOCX and perform one final page-by-page QA before upload.

## Fields that are not initial-submission blockers

A permanent archive DOI is not required to open the initial submission. The Open Research Statement currently says the exact accepted analysis/code release will be deposited permanently; update the statement with the DOI when that archive exists.

## Scientific freeze

Completing author metadata does not authorize any new ecological endpoint, threshold, model, regional definition, trait screen, mechanism search or p-value rule.
