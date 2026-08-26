# Workflow: Figure Planning & Generation

1. **Plan** — Figure Agent writes `figures/figure-plan.md` from outline+argument
   map+matrix+benchmark figure-patterns (role/propositions/data/tool per figure).
2. **Ground** — quantitative figures first export real numbers to
   `figures/data/*.csv` WITH provenance columns; conceptual figures map nodes to
   proposition ids. No grounding ⇒ downgrade the plan entry, don't draw.
3. **Build** — generate sources: Fig01.mmd / fig03.py etc.; render to .svg/.png
   when mmdc/Kroki/matplotlib available (see references/figure-design.md);
   watermark every artifact DRAFT SCIENTIFIC FIGURE until validated.
4. **Validate** — Reviewer checks necessity/clarity/factual support; Auditor checks
   data provenance row-by-row; failures return to step 3.
5. **Integrate** — ensure ≥1 paragraph references each figure consistently;
   captions carry takeaway+provenance; remove watermarks after pass.
6. Record tool availability limits in run summary (e.g., ".mmd shipped, rendering
   unavailable") instead of faking images.
