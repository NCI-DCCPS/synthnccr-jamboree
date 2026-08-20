# synthnccr — synthetic NCCR data foundation for the CCDI Data Jamboree

> **Purpose.** This repository is the working foundation for a project at the NCI
> Office of Data Sharing (ODS) Childhood & AYA Cancer **Data Jamboree**. It generates
> privacy-safe synthetic cohorts from the **published National Childhood Cancer
> Registry (NCCR) Data Platform metadata**, as a starting point the team can extend
> during the event (additional data sources, joint calibration against authorized
> analyses, and validation).

`synthnccr` reads the published NCCR metadata (the permissible-value frequencies NCI
publishes as machine-readable linked data), samples each variable from its published
marginal distribution, and repairs clinically incoherent records with a declarative
consistency-rules engine. Because the default path consumes only **aggregate published
frequencies** and no individual-level records, the synthetic output is privacy-safe by
construction: there is no training population to re-identify.

## Jamboree scope

- **Starting point (in this repo):** metadata-driven marginal generation + clinical
  consistency rules + a marginal-fidelity scorecard, working against the real
  published NCCR metadata.
- **To explore during the event:** joint (cross-variable) calibration using authorized
  aggregate analyses of real NCCR data, an illustrative linked-trajectory demo, and a
  validation framework spanning statistical fidelity, clinical plausibility, and
  disclosure risk.

## Install

```bash
pip install -e ".[rdf]"     # includes rdflib, needed to read the NCCR metadata
```

Core generation depends only on numpy, pandas, and pyarrow (Python 3.9+). The `[rdf]`
extra adds `rdflib` for loading the published NCCR RDF/Turtle metadata.

## Quickstart

The NCCR metadata is published at <https://github.com/NCI-DCCPS/nccr-metadata>. Use
`remote` to fetch it, or pass a local `.ttl` file.

```bash
# 1. List the NCCR datasources (with real record counts)
synthnccr sources remote

# 2. Inspect the variables that have published frequencies for a source
synthnccr profile remote --source CTC

# 3. Generate a synthetic registry cohort + clinical rules, then score it
synthnccr generate remote --source CTC \
    -n 20000 \
    --rules examples/ctc_consistency_rules.json \
    --seed 42 \
    --out out/ctc.parquet \
    --evaluate

# 4. Score an existing cohort against the published marginals
synthnccr evaluate remote --source CTC out/ctc.parquet
```

Working offline? Download `nccr_instances.ttl` once and pass its path in place of
`remote` (much faster than fetching on every run).

Available sources: `CTC` (registry), `ABM`, `CCDI`, `COG`, `MCD`, `MCE`, `MCP`,
`PHARM`, `RO`. Add `--value-mode code` to use raw code notations instead of labels.

## Why marginals are not enough (stated up front)

Sampling every variable independently reproduces each variable's distribution
perfectly but destroys the relationships *between* variables — the joint distribution
cannot be recovered from marginals alone. Two mechanisms address this:

1. **Consistency rules** patch the most important, well-known relationships (e.g.
   Gleason score does not apply to female patients; retinoblastoma occurs in early
   childhood).
2. **Joint calibration** learns cross-variable structure from an individual-level
   proxy (e.g. SEER research data, or authorized aggregate analyses of real NCCR
   data) and uses iterative proportional fitting (raking) to make its margins match
   the published NCCR marginals, while preserving association.

## End-to-end demo

`examples/demo_ctc.py` runs the whole story in one pass — load metadata, generate,
show the incoherence of naive sampling, apply rules, show it fixed, report fidelity
and privacy, and export:

```bash
python examples/demo_ctc.py --metadata nccr_instances.ttl -n 20000
```

## Python API

```python
from synthnccr import generate, marginal_fidelity, overall_score
from synthnccr.constraints import RuleSet
from synthnccr.nccr_rdf import load_graph, build_dictionary

graph = load_graph(["nccr_instances.ttl"])   # or default: the published URL
d = build_dictionary(graph, "CTC")           # a DataDictionary for one source

rules = RuleSet.from_json("examples/ctc_consistency_rules.json")
result = generate(d, n=20000, rng=42, ruleset=rules)

print(result.data.head())
print(result.repairs)                         # per-rule repair counts
print(overall_score(marginal_fidelity(d, result.data)))
```

## Consistency rules format

Declarative JSON. The `allowed_values` rule says: when `trigger_col` holds one of
`trigger_values`, `target_col` must be one of `allowed_values` (violations are
repaired by resampling). See `examples/ctc_consistency_rules.json`.

```json
{
  "max_iterations": 5,
  "constraints": [
    {
      "type": "allowed_values",
      "name": "retinoblastoma_is_early_childhood",
      "trigger_col": "icccMajor",
      "trigger_values": ["V. Retinoblastoma"],
      "target_col": "ageRecode19Groups",
      "allowed_values": ["00 years", "01-04 years", "05-09 years"],
      "description": "Retinoblastoma occurs almost exclusively in early childhood."
    }
  ]
}
```

## Privacy posture

- **Metadata-only generation** (the default): derived solely from published aggregate
  frequencies, no individual records — privacy-safe by construction.
- **Joint-calibrated generation**: once an individual-level source is used, outputs are
  derived from disclosure-controlled inputs and should pass a privacy evaluation suite
  (nearest-neighbor distance, membership inference) before any release.

## License

Apache-2.0. See [LICENSE](LICENSE). Synthetic output contains **no real patient
data**; the tool reads only published aggregate metadata.
