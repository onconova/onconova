"""
Count PatientCase rows matching a case-example partial bundle (panel JSON from aitb-dashboard).

The payload shape matches the aitb-dashboard ``caseExample`` object:
camelCase panel keys (e.g. ``neoplasticEntities``) mapping to lists of row dicts
built from Onconova export slices (coded concepts as ``{ "code": "..." }`` where
applicable; genomic variants may include ``proteinHgvs`` as a plain HGVS string;
therapy lines use ``label`` / ``intent`` / ``ordinal``; systemic
therapies use only ``medications[].drug`` codes; radiotherapies include intent,
sessions, line id, and nested dosage / setting codes as emitted by aitb-dashboard).

Panel keys are kept in sync with aitb-dashboard ``casePanelColumns`` /
``BUNDLE_ARRAY_KEYS_ORDER`` (Cancer Characterization, Genomics, Therapy, Profile,
Clinical Observations and every sub-panel ``key`` there).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Iterable

logger = logging.getLogger(__name__)

from django.core.exceptions import FieldDoesNotExist
from django.db import connections, models
from django.db.models import Exists, OuterRef, Q, QuerySet
from django.utils.encoding import force_str

from onconova.core.utils import camel_to_snake
from onconova.oncology import models as orm
from onconova.oncology.models.performance_status import (
    ECOG_INTEPRETATION,
    KARNOFSKY_INTEPRETATION,
)
from onconova.terminology.models import CodedConcept


def _coded_code(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, dict):
        c = value.get("code")
        if c is None:
            return None
        s = str(c).strip()
        return s or None
    return None


def _normalize_bundle(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("caseExample payload must be a JSON object")
    inner = payload.get("caseExample")
    if isinstance(inner, dict):
        return inner
    return payload


def _is_coded_concept_relation_field(model: type[models.Model], field_name: str) -> bool:
    try:
        f = model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return False
    if isinstance(f, models.ForeignKey):
        return bool(
            f.related_model is not None and issubclass(f.related_model, CodedConcept)
        )
    if isinstance(f, models.ManyToManyField):
        rel_model = f.remote_field.model
        return bool(rel_model is not None and issubclass(rel_model, CodedConcept))
    return False


def _iter_parent_linked_children(
    parent: type[models.Model],
) -> Iterable[tuple[str, type[models.Model]]]:
    for cls in parent.__subclasses__():
        if not issubclass(cls, parent):
            continue
        for f in cls._meta.local_fields:
            remote = getattr(f, "remote_field", None)
            if remote is None:
                continue
            # Django 5 stores ``parent_link`` on ``remote_field`` (not the forward field).
            if not getattr(remote, "parent_link", False) and not getattr(
                f, "parent_link", False
            ):
                continue
            if getattr(remote, "model", None) is not parent:
                continue
            rel = remote.related_name
            if rel:
                yield rel, cls
            break


def _vanilla_queryset(model: type[models.Model]) -> QuerySet:
    """Plain QuerySet (no QueryableProperties mixin) for EXISTS subqueries on the outer PatientCase query."""
    return QuerySet(model=model, using=model.objects.db)


def _staging_row_q(row: dict[str, Any]) -> Q | None:
    pairs = [(camel_to_snake(k), _coded_code(v)) for k, v in row.items()]
    pairs = [(sn, c) for sn, c in pairs if c]
    if not pairs:
        return None

    # Dashboard / bundle rows include stagingDomain, date, caseId, etc. Only CodedConcept
    # FK/M2M columns are filter criteria; ignore other keys (do not require every pair to
    # exist on each subclass — that rejected every subclass for real export rows).
    matching_kwarg_lists: list[dict[str, str]] = []
    for rel, cls in _iter_parent_linked_children(orm.Staging):
        kwargs: dict[str, str] = {}
        for snake, code in pairs:
            if not _is_coded_concept_relation_field(cls, snake):
                continue
            kwargs[f"{rel}__{snake}__code"] = code
        if kwargs:
            matching_kwarg_lists.append(kwargs)

    if not matching_kwarg_lists:
        return None

    staging_qs = _vanilla_queryset(orm.Staging)
    exists_parts = [
        Q(Exists(staging_qs.filter(case_id=OuterRef("pk"), **mk)))
        for mk in matching_kwarg_lists
    ]
    combined = exists_parts[0]
    for part in exists_parts[1:]:
        combined |= part
    return combined


def _genomic_signature_row_q(row: dict[str, Any]) -> Q | None:
    pairs = [(camel_to_snake(k), _coded_code(v)) for k, v in row.items()]
    pairs = [(sn, c) for sn, c in pairs if c]
    if not pairs:
        return None

    matching_kwarg_lists: list[dict[str, str]] = []
    for rel, cls in _iter_parent_linked_children(orm.GenomicSignature):
        kwargs: dict[str, str] = {}
        for snake, code in pairs:
            if not _is_coded_concept_relation_field(cls, snake):
                continue
            kwargs[f"{rel}__{snake}__code"] = code
        if kwargs:
            matching_kwarg_lists.append(kwargs)

    if not matching_kwarg_lists:
        return None

    sig_qs = _vanilla_queryset(orm.GenomicSignature)
    exists_parts = [
        Q(Exists(sig_qs.filter(case_id=OuterRef("pk"), **mk)))
        for mk in matching_kwarg_lists
    ]
    combined = exists_parts[0]
    for part in exists_parts[1:]:
        combined |= part
    return combined


def _tumor_board_row_q(row: dict[str, Any]) -> Q | None:
    kwargs: dict[str, Any] = {}
    for json_key, val in row.items():
        code = _coded_code(val)
        if not code:
            continue
        snake = camel_to_snake(json_key)
        if _is_coded_concept_relation_field(orm.TumorBoard, snake):
            kwargs[f"{snake}__code"] = code

    if kwargs:
        return Q(Exists(orm.TumorBoard.objects.filter(case_id=OuterRef("pk"), **kwargs)))

    matching_kwarg_lists: list[dict[str, str]] = []
    for rel, cls in _iter_parent_linked_children(orm.TumorBoard):
        ckwargs: dict[str, str] = {}
        for json_key, val in row.items():
            code = _coded_code(val)
            if not code:
                continue
            snake = camel_to_snake(json_key)
            if not _is_coded_concept_relation_field(cls, snake):
                continue
            ckwargs[f"{rel}__{snake}__code"] = code
        if ckwargs:
            matching_kwarg_lists.append(ckwargs)

    if not matching_kwarg_lists:
        return None

    board_qs = _vanilla_queryset(orm.TumorBoard)
    exists_parts = [
        Q(Exists(board_qs.filter(case_id=OuterRef("pk"), **mk)))
        for mk in matching_kwarg_lists
    ]
    combined = exists_parts[0]
    for part in exists_parts[1:]:
        combined |= part
    return combined


def _neoplastic_row_q(row: dict[str, Any]) -> Q | None:
    kwargs: dict[str, Any] = {"case_id": OuterRef("pk")}
    rel_raw = row.get("relationship")
    rel_code = _coded_code(rel_raw) if isinstance(rel_raw, dict) else _coded_code(rel_raw)
    if rel_code:
        kwargs["relationship"] = rel_code
    topo = _coded_code(row.get("topography"))
    if topo:
        kwargs["topography__code"] = topo
    morph = _coded_code(row.get("morphology"))
    if morph:
        kwargs["morphology__code"] = morph
    tg = _coded_code(row.get("topographyGroup")) or _coded_code(row.get("topography_group"))
    if tg:
        kwargs["topography_group__code"] = tg

    if len(kwargs) == 1:
        return None
    return Q(Exists(orm.NeoplasticEntity.objects.filter(**kwargs)))


def _gene_panel_string_value(val: Any) -> str | None:
    """Resolve gene panel from export JSON (CharField on GenomicVariant, not a CodedConcept FK)."""
    if val is None:
        return None
    c = _coded_code(val)
    if c:
        return c
    if isinstance(val, str):
        s = val.strip()
        return s or None
    if isinstance(val, dict):
        d = val.get("display")
        if d is not None:
            s = str(d).strip()
            if s:
                return s
    return None


def _protein_hgvs_string_value(val: Any) -> str | None:
    """Resolve protein HGVS from export JSON (CharField on GenomicVariant, not a CodedConcept FK)."""
    if val is None:
        return None
    c = _coded_code(val)
    if c:
        return c
    if isinstance(val, str):
        s = val.strip()
        return s or None
    if isinstance(val, dict):
        d = val.get("display")
        if d is not None:
            s = str(d).strip()
            if s:
                return s
    return None


def _cytogenetic_location_filter_value(val: Any) -> str | None:
    """Cytogenetic location is a string in the API; bundles may send {code} only."""
    if val is None:
        return None
    if isinstance(val, str):
        s = val.strip()
        return s or None
    return _coded_code(val)


def _ecog_interpretation_code_to_score(code: str) -> int | None:
    for score, mapped in ECOG_INTEPRETATION.items():
        if mapped == code:
            return score
    return None


def _karnofsky_interpretation_code_to_score(code: str) -> int | None:
    for score, mapped in KARNOFSKY_INTEPRETATION.items():
        if mapped == code:
            return score
    return None


def _performance_status_row_q(row: dict[str, Any]) -> Q | None:
    """
    Build an EXISTS filter for PerformanceStatus rows.

    Export JSON uses ``ecogInterpretation`` / ``karnofskyInterpretation`` coded concepts,
    but the ORM model exposes those as ``SubqueryObjectProperty`` (derived from numeric
    scores), not real ``ForeignKey`` columns — so ``_flat_model_row_q`` never matched them.
    """
    kwargs: dict[str, Any] = {}
    for json_key, val in row.items():
        snake = camel_to_snake(json_key)
        if snake == "ecog_interpretation":
            code = _coded_code(val)
            if code:
                score = _ecog_interpretation_code_to_score(code)
                if score is None:
                    return Q(pk__in=[])
                kwargs["ecog_score"] = score
            continue
        if snake == "karnofsky_interpretation":
            code = _coded_code(val)
            if code:
                score = _karnofsky_interpretation_code_to_score(code)
                if score is None:
                    return Q(pk__in=[])
                kwargs["karnofsky_score"] = score
            continue
        if snake == "ecog_score" and val is not None:
            try:
                kwargs["ecog_score"] = int(val)
            except (TypeError, ValueError):
                pass
            continue
        if snake == "karnofsky_score" and val is not None:
            try:
                kwargs["karnofsky_score"] = int(val)
            except (TypeError, ValueError):
                pass
            continue
        code = _coded_code(val)
        if not code:
            continue
        if _is_coded_concept_relation_field(orm.PerformanceStatus, snake):
            kwargs[f"{snake}__code"] = code
    if not kwargs:
        return None
    return Q(Exists(orm.PerformanceStatus.objects.filter(case_id=OuterRef("pk"), **kwargs)))


def _genomic_variant_row_q(row: dict[str, Any]) -> Q | None:
    """
    Build an EXISTS filter for GenomicVariant rows.

    ``_flat_model_row_q`` only considers CodedConcept FK/M2M columns. GenomicVariant also
    stores ``gene_panel``, ``dna_hgvs``, and ``protein_hgvs`` as plain CharFields,
    ``hgvsVersion`` is API-only (not a DB filter), ``cytogenetic_location`` is a queryable
    ``AnnotationProperty``, and ``genes`` is a CodedConcept M2M requiring chained filters.
    """
    inner = orm.GenomicVariant.objects.filter(case_id=OuterRef("pk"))
    matched = False
    for json_key, val in row.items():
        snake = camel_to_snake(json_key)
        if snake == "gene_panel":
            gp = _gene_panel_string_value(val)
            if gp:
                inner = inner.filter(gene_panel__iexact=gp)
                matched = True
            continue
        if snake == "protein_hgvs":
            ph = _protein_hgvs_string_value(val)
            if ph:
                inner = inner.filter(protein_hgvs__iexact=ph)
                matched = True
            continue
        if snake == "dna_hgvs":
            dh = _protein_hgvs_string_value(val)
            if dh:
                inner = inner.filter(dna_hgvs__iexact=dh)
                matched = True
            continue
        if snake == "hgvs_version":
            # Serialized HGVS nomenclature version (schema default); not a persisted column.
            continue
        if snake == "cytogenetic_location":
            loc = _cytogenetic_location_filter_value(val)
            if loc:
                inner = inner.filter(cytogenetic_location__icontains=loc)
                matched = True
            continue
        if snake == "genes" and isinstance(val, list):
            for item in val:
                if not isinstance(item, dict):
                    continue
                code = _coded_code(item)
                if code:
                    inner = inner.filter(genes__code=code)
                    matched = True
            continue
        code = _coded_code(val)
        if not code:
            continue
        if _is_coded_concept_relation_field(orm.GenomicVariant, snake):
            inner = inner.filter(**{f"{snake}__code": code})
            matched = True
    if not matched:
        return None
    return Q(Exists(inner))


def _therapy_line_intent_value(val: Any) -> str | None:
    """Normalize therapy line intent from export JSON (string or ``{code}``)."""
    if val is None:
        return None
    if isinstance(val, str):
        s = val.strip().lower()
        return s if s in ("curative", "palliative") else None
    if isinstance(val, dict):
        c = _coded_code(val)
        if c is None:
            return None
        s = str(c).strip().lower()
        return s if s in ("curative", "palliative") else None
    return None


def _therapy_line_row_q(row: dict[str, Any]) -> Q | None:
    """
    Build an EXISTS filter for TherapyLine rows.

    Therapy lines are identified by persisted ``label`` (e.g. ``PLoT1``), ``intent``,
    and ``ordinal`` — not CodedConcept FKs, so :func:`_flat_model_row_q` never matched.
    """
    kwargs: dict[str, Any] = {}
    for json_key, val in row.items():
        snake = camel_to_snake(json_key)
        if snake == "label":
            if val is None:
                continue
            s = str(val).strip()
            if s:
                kwargs["label"] = s
            continue
        if snake == "intent":
            intent = _therapy_line_intent_value(val)
            if intent:
                kwargs["intent"] = intent
            continue
        if snake == "ordinal":
            if val is None:
                continue
            try:
                o = int(val)
            except (TypeError, ValueError):
                continue
            if o > 0:
                kwargs["ordinal"] = o
            continue
    if not kwargs:
        return None
    return Q(Exists(orm.TherapyLine.objects.filter(case_id=OuterRef("pk"), **kwargs)))


def _systemic_therapy_row_q(row: dict[str, Any]) -> Q | None:
    """
    Build an EXISTS filter for SystemicTherapy rows.

    aitb-dashboard sends only ``medications[].drug`` as ``{ "code": "..." }``.
    Similarity requires a systemic therapy on the case that includes **every**
    listed drug (AND across medication entries).
    """
    inner = orm.SystemicTherapy.objects.filter(case_id=OuterRef("pk"))
    matched = False
    for json_key, val in row.items():
        snake = camel_to_snake(json_key)
        if snake != "medications" or not isinstance(val, list):
            continue
        for item in val:
            if not isinstance(item, dict):
                continue
            code = _coded_code(item.get("drug"))
            if code:
                inner = inner.filter(medications__drug__code=code)
                matched = True
    if not matched:
        return None
    return Q(Exists(inner))


def _radiotherapy_row_q(row: dict[str, Any]) -> Q | None:
    """
    Build an EXISTS filter for Radiotherapy rows.

    Matches ``intent``, ``sessions``, ``therapyLineId``, ``terminationReason``, and
    nested ``dosages[].irradiatedVolume`` / ``settings[].modality|technique`` codes.
    """
    inner = orm.Radiotherapy.objects.filter(case_id=OuterRef("pk"))
    matched = False
    for json_key, val in row.items():
        snake = camel_to_snake(json_key)
        if snake == "intent":
            intent = _therapy_line_intent_value(val)
            if intent:
                inner = inner.filter(intent=intent)
                matched = True
            continue
        if snake == "sessions" and val is not None:
            try:
                inner = inner.filter(sessions=int(val))
                matched = True
            except (TypeError, ValueError):
                pass
            continue
        if snake == "therapy_line_id" and val is not None:
            s = str(val).strip()
            if s:
                inner = inner.filter(therapy_line_id=s)
                matched = True
            continue
        if snake == "termination_reason":
            code = _coded_code(val)
            if code:
                inner = inner.filter(termination_reason__code=code)
                matched = True
            continue
        if snake == "dosages" and isinstance(val, list):
            for item in val:
                if not isinstance(item, dict):
                    continue
                code = _coded_code(
                    item.get("irradiatedVolume") or item.get("irradiated_volume")
                )
                if code:
                    inner = inner.filter(dosages__irradiated_volume__code=code)
                    matched = True
            continue
        if snake == "settings" and isinstance(val, list):
            for item in val:
                if not isinstance(item, dict):
                    continue
                mc = _coded_code(item.get("modality"))
                if mc:
                    inner = inner.filter(settings__modality__code=mc)
                    matched = True
                tc = _coded_code(item.get("technique"))
                if tc:
                    inner = inner.filter(settings__technique__code=tc)
                    matched = True
            continue
    if not matched:
        return None
    return Q(Exists(inner))


def _flat_model_row_q(model: type[models.Model], row: dict[str, Any]) -> Q | None:
    kwargs: dict[str, str] = {}
    for json_key, val in row.items():
        code = _coded_code(val)
        if not code:
            continue
        snake = camel_to_snake(json_key)
        if _is_coded_concept_relation_field(model, snake):
            kwargs[f"{snake}__code"] = code
    if not kwargs:
        return None
    return Q(Exists(model.objects.filter(case_id=OuterRef("pk"), **kwargs)))


# Flat ORM targets keyed by aitb-dashboard panel ``key`` (see ``onconovaCasePanels``).
_PANEL_FLAT_MODELS: dict[str, type[models.Model]] = {
    "tumorMarkers": orm.TumorMarker,
    "riskAssessments": orm.RiskAssessment,
    "surgeries": orm.Surgery,
    "adverseEvents": orm.AdverseEvent,
    "treatmentResponses": orm.TreatmentResponse,
    "comorbidities": orm.ComorbiditiesAssessment,
    "vitals": orm.Vitals,
    "lifestyles": orm.Lifestyle,
    "familyHistory": orm.FamilyHistory,
}

# Every panel key the dashboard can emit under ``caseExample`` (bundle root); must match
# ``BUNDLE_ARRAY_KEYS_ORDER`` in aitb-dashboard ``PatientCaseView.vue``.
_FUNCTIONAL_AGGREGATION_PANEL_KEYS: frozenset[str] = frozenset(
    {
        # Cancer Characterization
        "neoplasticEntities",
        "stagings",
        "tumorMarkers",
        "riskAssessments",
        # Genomics
        "genomicVariants",
        "genomicSignatures",
        # Therapy
        "therapyLines",
        "systemicTherapies",
        "surgeries",
        "radiotherapies",
        # Profile
        "lifestyles",
        "familyHistory",
        "comorbidities",
        "vitals",
        # Clinical Observations
        "tumorBoards",
        "adverseEvents",
        "treatmentResponses",
        "performanceStatus",
    }
)

_POLYMORPHIC_PANEL_KEYS: frozenset[str] = frozenset(
    {"neoplasticEntities", "stagings", "genomicSignatures", "tumorBoards"}
)

# Panels with a dedicated row handler in ``_panel_row_q`` (not plain ``_flat_model_row_q``).
_SPECIAL_PANEL_ROW_KEYS: frozenset[str] = frozenset(
    {
        "genomicVariants",
        "performanceStatus",
        "therapyLines",
        "systemicTherapies",
        "radiotherapies",
    }
)


def _assert_panel_registry_matches_dashboard() -> None:
    """Invariant: every dashboard panel key maps to a handler (tests / CI)."""
    handled = (
        frozenset(_PANEL_FLAT_MODELS)
        | _POLYMORPHIC_PANEL_KEYS
        | _SPECIAL_PANEL_ROW_KEYS
    )
    if handled != _FUNCTIONAL_AGGREGATION_PANEL_KEYS:
        missing = sorted(_FUNCTIONAL_AGGREGATION_PANEL_KEYS - handled)
        extra = sorted(handled - _FUNCTIONAL_AGGREGATION_PANEL_KEYS)
        raise RuntimeError(
            "match count panel registry drift: "
            f"missing_handlers={missing!r} extra_handlers={extra!r}"
        )


_assert_panel_registry_matches_dashboard()


def _sql_with_params_interpolated_for_log(db_alias: str, sql: str, params: Any) -> str:
    """Return SQL with bound parameters inlined (PostgreSQL only); for logs, not execution."""
    conn = connections[db_alias]
    if conn.vendor != "postgresql":
        return f"{sql}\n-- params (raw, not interpolated on {conn.vendor!r}): {params!r}"
    from django.db.backends.postgresql.psycopg_any import mogrify

    try:
        raw = mogrify(sql, () if params is None else params, conn)
    except Exception as exc:  # pragma: no cover - defensive
        return f"{sql}\n-- params: {params!r}\n-- mogrify failed: {exc!r}"
    return force_str(raw)


def _panel_row_q(panel_key: str, row: dict[str, Any]) -> Q | None:
    if panel_key == "neoplasticEntities":
        return _neoplastic_row_q(row)
    if panel_key == "stagings":
        return _staging_row_q(row)
    if panel_key == "genomicSignatures":
        return _genomic_signature_row_q(row)
    if panel_key == "tumorBoards":
        return _tumor_board_row_q(row)
    if panel_key == "genomicVariants":
        return _genomic_variant_row_q(row)
    if panel_key == "performanceStatus":
        return _performance_status_row_q(row)
    if panel_key == "therapyLines":
        return _therapy_line_row_q(row)
    if panel_key == "systemicTherapies":
        return _systemic_therapy_row_q(row)
    if panel_key == "radiotherapies":
        return _radiotherapy_row_q(row)
    model = _PANEL_FLAT_MODELS.get(panel_key)
    if model:
        return _flat_model_row_q(model, row)
    return None


def _patient_cases_queryset_plain() -> QuerySet:
    """
    PatientCase queryset without QueryablePropertiesManager / QuerySet mixin.

    ``PatientCase.objects`` injects ``QueryablePropertiesQuerySetMixin``, which can
    break ``QuerySet.count()`` / ``as_sql()`` for some EXISTS(OuterRef(...)) filter
    shapes. Use a vanilla ``QuerySet`` for the **outer** PatientCase query only.

    Inner ``Exists(...)`` subqueries must keep ``Model.objects`` so filters on
    ``SubqueryObjectProperty`` / ``AnnotationProperty`` (e.g. neoplastic
    ``topography_group__code``, genomic variant ``cytogenetic_location__icontains``)
    remain valid.
    """
    return QuerySet(model=orm.PatientCase, using=orm.PatientCase.objects.db)


def patient_cases_queryset_for_case_example(payload: Any) -> models.QuerySet:
    """Return the filtered PatientCase queryset for a case example payload."""
    bundle = _normalize_bundle(payload)
    unknown = frozenset(bundle) - _FUNCTIONAL_AGGREGATION_PANEL_KEYS
    if unknown:
        raise ValueError(
            "Unknown exampleCase panel key(s): "
            f"{', '.join(sorted(unknown))}. "
            "Keys must match aitb-dashboard case bundle panels "
            f"({', '.join(sorted(_FUNCTIONAL_AGGREGATION_PANEL_KEYS))})."
        )
    qs = _patient_cases_queryset_plain()
    for panel_key, rows in bundle.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_q = _panel_row_q(panel_key, row)
            if row_q is not None:
                qs = qs.filter(row_q)
    return qs


def interpolated_sql_for_case_example_filter(
    qs: models.QuerySet,
) -> str:
    """Human-readable SQL for the queryset filter (same shape as DEBUG logs)."""
    compiler = qs.query.get_compiler(using=qs.db)
    try:
        sql, params = compiler.as_sql()
        return _sql_with_params_interpolated_for_log(qs.db, sql, params)
    except Exception as exc:  # pragma: no cover - defensive
        return (
            f"-- as_sql failed: {exc!r}\n"
            f"-- fallback queryset representation:\n{str(qs.query)}"
        )


def count_patient_cases_matching_case_example(payload: Any) -> int:
    qs = patient_cases_queryset_for_case_example(payload)
    if logger.isEnabledFor(logging.DEBUG):
        filled = interpolated_sql_for_case_example_filter(qs)
        logger.debug(
            "match count patient count SQL (compiled filter; ORM wraps in COUNT for .count()):\n%s",
            filled,
        )
    n = qs.count()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("match count patient count result: %s", n)
    return n


def parse_case_example_query_param(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e
