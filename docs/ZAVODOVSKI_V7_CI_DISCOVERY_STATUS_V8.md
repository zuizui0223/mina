# V8 — CI visibility audit (2026-10-13)

GitHub connector commit-run query for V7 commit 4c7179636a02391c2913c17651658b2959091f38 returned prior Zavodovski synthetic QA success (#38349835392), but no archive-documentation workflow. This endpoint reports only PR-associated runs, first page. Absence does NOT prove the new push workflow failed or never ran.

The V7 workflow exists on the PR branch, with push path filters and workflow_dispatch. The next evidence is the direct workflow run page and its JSON artifact; neither has been checked yet. Do not claim a CSV URL or actual polygon provenance has been obtained.

Zero original BAS polygon rows read. No new biological outcome. Ecology PR189 unchanged.
