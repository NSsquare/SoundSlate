# SoundSlate test results

How I test: run `python describe_structured.py samples/<file>`, then compare every
number and label in the output with the image myself. I only record what I checked.

## Summary so far

| Image | Type | Runs | Correct | Wrong or missing |
|---|---|---|---|---|
| chart2.png | Stacked bar chart, 15 taxa | 4 | Chart type, axes, groups, patient IDs, legend count; most key values | P012 labeled Moraxella; actual is Fusobacterium (teal vs green) |

## Details

### chart2.png (stacked bar chart, microbial taxa)

- Run 1 (first prompt): summary and groups correct; trend too general, ignored P012; confidence note said "None".
- Run 2 (improved prompt): key values P006, P004, P002 matched my reading; trend named exceptions but P012 only as "a higher level".
- Run 3 and 4 (exceptions and color prompts): P012 listed in key_values but labeled Moraxella both times (wrong).
- Run 4: confidence note now warns about similar colors, but not about P012 specifically.
- Output changes from run to run, even for the same image.
- Output once contradicted itself: trend calls P012 an exception, key_values gives it the Moraxella pattern.
- Run 5 (via /describe endpoint, 200 OK): legend count wrong (said 16, actual 15); P012 not mentioned; P004 omitted from Moraxella-dominated list; P006, P009 values correct; confidence note warns about similar colors.

## Still to test

- A diagram (flowchart or labeled figure)
- Handwritten notes
- A blurry or low-quality image
- A simple chart with printed numbers

## Lessons

- Dense charts with many similar colors are the weak spot.
- Prompt tuning fixed vague trends and missing uncertainty notes, but not the color mix-up.