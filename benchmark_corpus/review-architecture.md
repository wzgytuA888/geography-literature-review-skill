# Review Architecture — consolidated form patterns

consolidated: 2026-08-26, N=60
Tiers: corpus-consensus = documented in >=30/60 scoreable docs; common >=12/60; variant <12 but multi-doc; outlier single-doc.
Every claim carries doc-ID evidence; frequencies are lower bounds (digests sample ~15-20% of body text).

## Dominant skeleton [corpus-consensus, ~53/60]
- Fixed house arc: Abstract -> framing Introduction -> 3-6 thematically named body sections ->
  terminal forward-looking closing section -> references.
  (B001,B003,B005-B007,B009,B011,B012,B015-B018,B020,B021-B030,B031-B040,B041-B050,B051-B060)
- Body-section headings state content ("Record statistics" style), never generic labels such as
  "Discussion". (B001,B010,B021-B030,B047; recurring across all batches)
- Flat hierarchy: one nesting level at most; depth is carried by run-in mini-headings and Boxes,
  not sub-sub-sections. (B041-B050; 10/10 batch-local)

## Body order is a progression, not a topic list [corpus-consensus]
Five observed ladder types (pick one per review; hybrids declare their mix):
1. Causal/funnel ladder: drivers or mechanisms -> observations -> projections -> impacts ->
   responses/management. (B001,B002,B003,B006,B007,B009,B011,B013,B019,B021,B023,B024,B025,B026,
   B029,B030,B031-B033,B036-B039; ~30/60) [corpus-consensus]
2. Temporal ladder: palaeo/instrumental/projected eras; windows sometimes declared numerically.
   (B011,B015,B018,B020,B053,B058; ~12/60) [common]
3. Spatial scale ladder: site -> region -> globe, or gridpoint -> land/ocean. (B001,B003,B004,B007,
   B016,B019,B042,B047,B051,B060; ~10/60) [variant-to-common]
4. Framework-mirror ladder: headings mirror one named analytical framework slot-for-slot
   (DPSIR-like). (B023; B010 metric taxonomy and B005 cycle baseline are lens variants; ~4/60) [variant]
5. Parallel-class template: identical internal template repeated per class member (per material,
   sector, continent, ecosystem). (B002,B003,B005,B006,B022,B025,B028,B033,B035,B040,B046; ~12/60) [common]

## Primer-before-evidence [common, ~16/60]
An early framework/primer/definitions section equips readers to parse later synthesis sections.
(B001,B003,B005,B010,B011,B017,B018,B024,B028,B052,B053,B058,B060)

## Bridge device [variant, 3/60]
A dedicated bridge subsection converts findings into gaps immediately before the closing outlook.
(B052,B054; mid-paper uncertainty-audit variant B007)

## Closing conventions [corpus-consensus, ~50/60]
- Terminal section is forward-looking, titled "Summary and future (perspectives)" or an Outlook/
  priorities close. (B001,B003,B005-B007,B009,B011,B012,B015-B018,B020-B030,B031-B040,B041-B050,B051-B060)
- Closing restates headline findings point-for-point against the Introduction before pivoting to
  the agenda. (B048 verified; B046,B049 candidate) [variant]
- Closing fulfils the Introduction's promise literally: promised gaps/directions are delivered
  itemized. (B015,B017,B020,B056 plus >=4 more batch-6 docs; ~9/60) [variant]

## Apparatus placement
- Boxes quarantine definitions, method primers, derivations, regional cases, recommendations so
  the main line stays analytic. (B003,B009,B010,B011,B013,B017,B018,B020,B033,B035,B036,B037,
  B041,B042,B045,B047x2,B050x2,B051,B052,B054,B055x2,B057x2,B058,B059; ~30/60) [corpus-consensus]
- Key-points bullet box (3-6 standalone quantified claims) near front: confirmed ~29/60
  (B011-B013,B016-B018,B020,B021-B030,B031,B034-B037,B041,B054,B057,B059,B060); presence varies
  with article year/format — verify venue format at runtime, do not assume. [common]
- Abstract carries concrete findings or numbers, never scope-only announcements. (batch-6 10/10;
  consistent with sampled abstracts elsewhere) [corpus-consensus]

## Anti-dominance note
No single document contributes >30% of this file's consensus claims; skeleton evidence spans all
six batches.
