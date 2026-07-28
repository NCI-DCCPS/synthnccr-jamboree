"""synthnccr - privacy-safe synthetic cancer registry cohorts from published marginals.

Phase 0 generates synthetic cohorts by sampling each variable independently from
its published marginal (permissible-value frequencies) and then repairing
clinically incoherent records with a consistency-rules engine.

Because Phase 0 consumes only published *aggregate* frequencies (no individual
records), the synthetic output is privacy-safe by construction: there is no
training set of real people to leak.

Later phases add joint-structure modeling (learned from a public individual-level
proxy such as SEER) calibrated to these marginals, which is what makes the
multivariate structure realistic.
"""

from .dictionary import DataDictionary, VariableMarginal
from .constraints import Constraint, AllowedValuesConstraint, RuleSet
from .generate import generate, GenerationResult
from .evaluate import marginal_fidelity, overall_score, PROVENANCE_STATEMENT
from .calibrate import (
    JointDistribution,
    CalibrationResult,
    raking_ipf,
    calibrate_to_dictionary,
    targets_from_dictionary,
    generate_calibrated,
)

__version__ = "0.0.1"


def load_nccr_dictionary(*args, **kwargs):
    """Lazy wrapper around :func:`synthnccr.nccr_rdf.load_nccr_dictionary`.

    Imported lazily so the core package does not require the optional ``rdflib``
    dependency unless the real NCCR RDF metadata is actually loaded.
    """
    from .nccr_rdf import load_nccr_dictionary as _impl

    return _impl(*args, **kwargs)


__all__ = [
    "DataDictionary",
    "VariableMarginal",
    "Constraint",
    "AllowedValuesConstraint",
    "RuleSet",
    "generate",
    "GenerationResult",
    "marginal_fidelity",
    "overall_score",
    "PROVENANCE_STATEMENT",
    "load_nccr_dictionary",
    "JointDistribution",
    "CalibrationResult",
    "raking_ipf",
    "calibrate_to_dictionary",
    "targets_from_dictionary",
    "generate_calibrated",
    "__version__",
]
