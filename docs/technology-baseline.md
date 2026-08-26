# Technology Baseline (Phase 0–1 evidence)

> v2 update: runtime discovery now prioritizes the official Semantic Scholar
> Graph API and OpenAlex Works API. Crossref is metadata validation/enrichment.
> The Google Scholar provider analysis below is retained as v1 historical context;
> Google Scholar is now optional manual supplementation and is never scraped.

Checked: 2026-08-26 via live web fetch. Items marked NOT VERIFIED could not be
confirmed from this network; they are treated as assumptions, not facts.

## 1. Book-to-Skill

| Field | Value |
| --- | --- |
| Official repo | https://github.com/virgiliojr94/book-to-skill |
| Version/commit | default branch `master`, last push 2026-08-26, 163 commits; no tagged release found |
| License | MIT (converter only; not output documents) |
| Core capability | Turns books/document corpora into Agent Skills (SKILL.md + chapters + glossary/patterns/cheatsheet); modes: full conversion, analyze-only, generate-from-analysis, **update/fold-in**; Docling-based extraction; RLM-style corpus querying for >50k-token sources; cost preflight; optional GitHub publish (private by default) |
| Stability | Very active (~25.6k stars) |
| Why selected | Methodology source: distill *structure/procedure/decision rules*, progressive disclosure, incremental fold-in — all adopted here |
| Mandatory? | Methodology only; no runtime dependency on its code |
| Limitations | Scanned PDFs need OCR first; quality depends on correct book-type choice |

## 2. Agent Skills open standard

| Field | Value |
| --- | --- |
| Spec | https://agentskills.io (+ /specification, /llms.txt); repo github.com/agentskills/agentskills with `skills-ref validate` CLI |
| Frontmatter | required `name` (1–64 chars, lowercase a-z0-9/hyphens, **must match parent directory name**), `description` ≤1024 chars; optional `license`, `compatibility` ≤500 chars, `metadata` map, experimental `allowed-tools` |
| Layout | SKILL.md required; conventions: scripts/, references/, assets/; relative refs one level deep |
| Progressive disclosure | L1 metadata ~100 tokens → L2 SKILL.md <500 lines/<5k tokens → L3 resources on demand |
| Adoption | Claude Code, Codex, Gemini CLI, Copilot, Cursor, Goose, OpenCode et al. |
| Compliance notes | This skill: folder `geography-literature-review-skill`, name matches; description 7xx chars; body ≪500 lines; heavy content in L3 files |

## 3. Multi-agent research practice (Anthropic engineering)

Source: anthropic.com/engineering/built-multi-agent-research-system (2025-06-13,
verified). Lead orchestrator + 3–5 parallel subagents; subagents as context
filters returning references, writing artifacts to disk; externalize plan/state
early (context truncation risk); evals: LLM-as-judge vs rubric, judge end-states
for state-mutating agents, start with ~20 real queries. Applied to:
Orchestrator + Scouts A–E parallelism; runs/<id>/ artifact discipline; evals E01–E17.

## 4. Google Scholar-compatible providers

Google Scholar has **no official public API** (confirmed). Verified providers:

| Provider | Endpoint | Result id field | Results array | Year filter | Notes |
| --- | --- | --- | --- | --- | --- |
| SerpAPI | serpapi.com/search?engine=google_scholar | `result_id` | organic_results | as_ylo/as_yhi | num≤20, start offset; cited_by.total+cites_id; versions.cluster_id; engine=google_scholar_cite for citation formats (links expire fast); free 250/mo |
| SearchApi | searchapi.io/api/v1/search | `data_cid` | organic_results | as_ylo/as_yhi | page param instead of start |
| SerpDog | api.serpdog.io/scholar | `id` | scholar_results | year params | page=0,10,20…; citations string "Cited by N" |

Cross-cutting: no dedicated DOI/pub_year fields anywhere → adapter regex-parses
year & DOI from publication_info.summary/snippet (implemented). Related-articles:
only a link, emulate via query variants. ScraperAPI/HasData Scholar endpoints:
NOT FOUND this session.

Historical v1 policy: a configured Scholar gateway was mandatory. In v2 this has
been superseded by `docs/academic-api-setup.md` and the multi-API client layer.

## 5. Zotero

| Capability | Status 2026-08 | Use in skill |
| --- | --- | --- |
| Web API v3 | Production-grade; api.zotero.org; key+user id; limit≤100, honor Backoff headers; bib mode ≤150 items | primary remote backend (`scripts/zotero_adapter.py`) |
| Local server | localhost:23119/api, user id 0; needs "allow other applications"; reads unauthenticated; Zotero 7+ (writes Zotero 10+) | preferred local backend |
| Better BibTeX | JSON-RPC at localhost:23119/better-bibtex/json-rpc; item.search/item.export/citationkey/collections; pull exports .biblatex/.csljson | citekeys + BibTeX export |
| MCP servers | 54yyyu/zotero-mcp (~4.8k★) etc. | opportunistic; not required |
| Live Word fields | NO reliable public API (native plugins only; format undocumented) | fallback = pandoc --citeproc static docx + explicit capability limitation |

## 6. Figures rendering

- @mermaid-js/mermaid-cli v11.16.0 (Node ≥18.19): Puppeteer now a PEER dependency —
  supply own Chrome via puppeteer-config executablePath, or use Kroki (kroki.io)
  POST /{type} server-side render (MIT, self-hostable). Skill keeps .mmd sources
  as ground truth; SVG/PNG rendered when toolchain available; DRAFT watermark until validated.

## 7. Long-running state

No official cross-host "state.json" convention exists (NOT FOUND); de facto
practice = durable file artifacts per stage + session transcripts. Therefore:
runs/<run-id>/state.json + per-stage CSV/JSONL/md artifacts ARE the checkpoint
format; resume validates artifacts before continuing (plan-validate-execute).

## Compatibility risks

- Provider schema drift → normalization layer + preflight schema probe.
- Zotero local API off by default → capability detection + DOI/Crossref fallback.
- mermaid-cli browser requirement → .mmd-first policy, Kroki fallback.
- agentskills spec evolution → frontmatter kept minimal & standard.
