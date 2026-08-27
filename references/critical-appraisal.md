# Design-matched Critical Appraisal

Appraise validity relevant to the review claim. Do not award one universal
“quality score,” and never use citations, journal impact or author prestige as a
proxy for validity.

## Selection router

Choose and document a recognized instrument or explicit domain set:

- randomized interventions: RoB 2 or domain-equivalent;
- non-randomized interventions: ROBINS-I or domain-equivalent;
- observational exposure/association studies: design-specific JBI/NOS-style
  domains, emphasizing confounding, selection and measurement;
- prediction/model studies: PROBAST-style domains plus calibration/validation;
- diagnostic accuracy: QUADAS-2-style domains;
- qualitative studies: CASP/JBI-style congruity, reflexivity and data adequacy;
- environmental evidence: CEE Critical Appraisal Tool when compatible;
- remote sensing/modeling: use the domain set below because generic clinical
  tools miss spatial leakage, reference-data and validation problems.

## Geography/remote-sensing/modeling domains

Assess each as low/some concerns/high/unclear with a source location and rationale:

1. sampling-frame and spatial coverage representativeness;
2. outcome/exposure/label validity and independence;
3. spatial or temporal leakage between training and validation;
4. scale, zoning, boundary and aggregation sensitivity;
5. treatment of spatial autocorrelation and non-stationarity;
6. missing data, cloud/gap filling and preprocessing transparency;
7. model calibration, external geographic/temporal validation and baseline choice;
8. uncertainty propagation, sensitivity analysis and selective reporting;
9. confounding/endogeneity or causal-identification assumptions where causal
   language is used;
10. reproducibility of data, code, parameters and versioned products.

## Output and synthesis use

Write one row per study/domain to `appraisal/study-appraisal.csv` with
`paper_id,design,tool,domain,judgment,rationale,source_location,reviewer`.
Maintain `appraisal/dependency-map.csv` for shared datasets/samples/models/authors.

Appraisal affects interpretation, not automatic eligibility unless the protocol
pre-specified exclusion. Synthesis must show whether primary conclusions survive
removing high-risk studies and collapsing dependent studies to one evidence
family. “Most studies agree” is invalid when most reuse the same dataset.

