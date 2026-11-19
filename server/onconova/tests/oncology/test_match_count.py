import json

from django.test import Client, TestCase

import onconova.terminology.models as terminology
from onconova.oncology.match_count import (
    _FUNCTIONAL_AGGREGATION_PANEL_KEYS,
    count_patient_cases_matching_case_example,
)
from onconova.oncology.models.radiotherapy import RadiotherapyIntentChoices
from onconova.oncology.models.systemic_therapy import SystemicTherapyIntentChoices
from onconova.oncology.models.therapy_line import TherapyLineIntentChoices
from onconova.tests.factories import (
    ECOGPerformanceStatusFactory,
    GenomicVariantFactory,
    PrimaryNeoplasticEntityFactory,
    RadiotherapyFactory,
    SystemicTherapyFactory,
    TNMStagingFactory,
    TherapyLineFactory,
    UserFactory,
)


class TestFunctionalAggregatedDataCount(TestCase):
    def test_panel_keys_cover_aitb_dashboard_panels(self):
        """Keeps server in sync with aitb-dashboard ``casePanelColumns`` / ``BUNDLE_ARRAY_KEYS_ORDER``."""
        expected = frozenset(
            {
                "neoplasticEntities",
                "stagings",
                "tumorMarkers",
                "riskAssessments",
                "genomicVariants",
                "genomicSignatures",
                "therapyLines",
                "systemicTherapies",
                "surgeries",
                "radiotherapies",
                "adverseEvents",
                "treatmentResponses",
                "performanceStatus",
                "comorbidities",
                "vitals",
                "lifestyles",
                "familyHistory",
                "tumorBoards",
            }
        )
        self.assertEqual(_FUNCTIONAL_AGGREGATION_PANEL_KEYS, expected)

    def test_empty_bundle_counts_all_cases(self):
        PrimaryNeoplasticEntityFactory.create()
        PrimaryNeoplasticEntityFactory.create()
        n = count_patient_cases_matching_case_example({})
        self.assertEqual(n, 2)

    def test_case_example_wrapper_is_normalized(self):
        PrimaryNeoplasticEntityFactory.create()
        PrimaryNeoplasticEntityFactory.create()
        n = count_patient_cases_matching_case_example({"caseExample": {}})
        self.assertEqual(n, 2)

    def test_unknown_panel_key_raises(self):
        with self.assertRaises(ValueError) as ctx:
            count_patient_cases_matching_case_example(
                {"notAPanel": [{"x": {"code": "1"}}]}
            )
        self.assertIn("notAPanel", str(ctx.exception))

    def test_neoplastic_morphology_and_relationship(self):
        sys_uri = "http://test.example/terminology/functional-agg-count-neoplastic"
        m1, _ = terminology.CancerMorphology.objects.get_or_create(
            code="fat-neo-morph-1",
            system=sys_uri,
            defaults={"display": "caseExample test morphology 1"},
        )
        m2, _ = terminology.CancerMorphology.objects.get_or_create(
            code="fat-neo-morph-2",
            system=sys_uri,
            defaults={"display": "caseExample test morphology 2"},
        )
        entity = PrimaryNeoplasticEntityFactory.create(morphology=m1)
        PrimaryNeoplasticEntityFactory.create(morphology=m2)

        payload = {
            "neoplasticEntities": [
                {
                    "relationship": {"code": "primary"},
                    "morphology": {"code": m1.code},
                }
            ]
        }
        n = count_patient_cases_matching_case_example(payload)
        self.assertEqual(n, 1)
        self.assertEqual(entity.case_id, entity.case.id)

    def test_performance_status_ecog_interpretation_in_sql_and_count(self):
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        ps_ecog1 = ECOGPerformanceStatusFactory.create(ecog_score=1)
        ECOGPerformanceStatusFactory.create(ecog_score=3)
        payload = {
            "performanceStatus": [
                {"ecogInterpretation": {"code": "LA9623-5"}},
            ],
        }
        n = count_patient_cases_matching_case_example(payload)
        self.assertEqual(n, 1)
        self.assertEqual(ps_ecog1.case_id, ps_ecog1.case.id)

        pqs = patient_cases_queryset_for_case_example(payload)
        sql = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_performancestatus", sql)
        self.assertIn("ecog_score", sql)

    def test_validate_endpoint_post_json_body(self):
        user = UserFactory.create(access_level=4)
        user.set_password("test-pass-123")
        user.save()
        client = Client()
        auth = client.post(
            "/api/v1/auth/session",
            data={"username": user.username, "password": "test-pass-123"},
            content_type="application/json",
            secure=True,
        )
        self.assertEqual(auth.status_code, 200)
        token = auth.json()["sessionToken"]
        headers = {"X-Session-Token": str(token)}

        body = {"caseExample": {"neoplasticEntities": []}}
        r = Client(headers=headers).post(
            "/api/v1/patient-cases/match-count",
            data=json.dumps(body),
            content_type="application/json",
            secure=True,
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("patientCaseCount", data)
        self.assertIn("patientCountSql", data)
        self.assertIsInstance(data["patientCountSql"], str)
        self.assertGreater(len(data["patientCountSql"]), 0)

        r_string_form = Client(headers=headers).post(
            "/api/v1/patient-cases/match-count",
            data=json.dumps(
                {
                    "caseExample": json.dumps({"neoplasticEntities": []})
                }
            ),
            content_type="application/json",
            secure=True,
        )
        self.assertEqual(r_string_form.status_code, 200)

        r2 = Client(headers=headers).post(
            "/api/v1/patient-cases/match-count",
            data=json.dumps({}),
            content_type="application/json",
            secure=True,
        )
        self.assertEqual(r2.status_code, 422)

    def test_tumor_marker_row_compiles_sql_and_counts(self):
        """Tumor marker functional rows use EXISTS(analyte__code); queryset must compile."""
        from onconova.oncology import models as orm
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        payload = {
            "caseExample": {
                "tumorMarkers": [
                    {
                        "analyte": {"code": "LP28643-2"},
                        "massConcentration": {"value": 1.5, "unit": "ng__ml"},
                    }
                ]
            }
        }
        pqs = patient_cases_queryset_for_case_example(payload)
        compiler = pqs.query.get_compiler(using=pqs.db)
        sql, params = compiler.as_sql()
        lowered = sql.lower()
        self.assertIn("oncology_tumormarker", lowered)
        self.assertIn("analyte", lowered)

        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_tumormarker", full)

        n = pqs.count()
        self.assertEqual(n, orm.PatientCase.objects.count())

    def test_therapy_line_row_filters_by_label_intent_ordinal(self):
        """TherapyLine has no CodedConcept FKs; similarity must filter on label/intent/ordinal."""
        from onconova.oncology.match_count import (
            patient_cases_queryset_for_case_example,
        )

        tl = TherapyLineFactory.create(
            intent=TherapyLineIntentChoices.PALLIATIVE, ordinal=2
        )
        tl.refresh_from_db()
        label = tl.label

        payload = {
            "caseExample": {
                "therapyLines": [
                    {"label": label, "intent": "palliative", "ordinal": 2},
                ],
            },
        }
        pqs = patient_cases_queryset_for_case_example(payload)
        ids = set(pqs.values_list("pk", flat=True))
        self.assertIn(tl.case_id, ids)

        other = TherapyLineFactory.create(
            intent=TherapyLineIntentChoices.CURATIVE, ordinal=1
        )
        other.refresh_from_db()
        payload_other = {
            "caseExample": {
                "therapyLines": [{"label": other.label}],
            },
        }
        pqs_other = patient_cases_queryset_for_case_example(payload_other)
        self.assertIn(other.case_id, set(pqs_other.values_list("pk", flat=True)))
        self.assertNotIn(tl.case_id, set(pqs_other.values_list("pk", flat=True)))

    def test_systemic_therapy_row_matches_medication_drug_codes_only(self):
        from onconova.oncology.match_count import (
            patient_cases_queryset_for_case_example,
        )

        st = SystemicTherapyFactory.create(intent=SystemicTherapyIntentChoices.CURATIVE)
        med = st.medications.first()
        self.assertIsNotNone(med)
        drug_code = med.drug.code

        pqs = patient_cases_queryset_for_case_example(
            {
                "caseExample": {
                    "systemicTherapies": [
                        {"medications": [{"drug": {"code": drug_code}}]},
                    ],
                },
            }
        )
        self.assertIn(st.case_id, set(pqs.values_list("pk", flat=True)))

        pqs_other = patient_cases_queryset_for_case_example(
            {
                "caseExample": {
                    "systemicTherapies": [
                        {
                            "medications": [
                                {"drug": {"code": "__nonexistent_similarity_drug__"}}
                            ],
                        }
                    ],
                },
            }
        )
        self.assertNotIn(st.case_id, set(pqs_other.values_list("pk", flat=True)))

    def test_radiotherapy_row_matches_intent_and_setting_modality(self):
        from onconova.oncology.match_count import (
            patient_cases_queryset_for_case_example,
        )

        rt = RadiotherapyFactory.create(intent=RadiotherapyIntentChoices.CURATIVE)
        setting = rt.settings.first()
        self.assertIsNotNone(setting)
        mod_code = setting.modality.code

        pqs = patient_cases_queryset_for_case_example(
            {
                "caseExample": {
                    "radiotherapies": [
                        {
                            "intent": "curative",
                            "sessions": rt.sessions,
                            "therapyLineId": str(rt.therapy_line_id),
                            "settings": [{"modality": {"code": mod_code}}],
                        }
                    ],
                },
            }
        )
        self.assertIn(rt.case_id, set(pqs.values_list("pk", flat=True)))

    def test_staging_tnm_row_compiles_sql_and_counts(self):
        """Staging EXISTS uses plain QuerySets; TNM ``stage`` code must compile and count."""
        from onconova.oncology import models as orm
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        staging = TNMStagingFactory.create()
        stage_code = staging.stage.code

        payload = {
            "caseExample": {
                "stagings": [{"stage": {"code": stage_code}}],
            }
        }
        pqs = patient_cases_queryset_for_case_example(payload)
        compiler = pqs.query.get_compiler(using=pqs.db)
        sql, _params = compiler.as_sql()
        lowered = sql.lower()
        self.assertIn("oncology_staging", lowered)

        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_staging", full)

        n = pqs.count()
        self.assertGreaterEqual(n, 1)
        self.assertIn(staging.case_id, pqs.values_list("pk", flat=True))

    def test_staging_dashboard_export_row_with_metadata_compiles(self):
        """Export-shaped rows include stagingDomain, date, caseId — must not break ORM SQL."""
        from onconova.oncology import models as orm
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        staging = TNMStagingFactory.create()
        stage_code = staging.stage.code
        t_code = staging.primary_tumor.code

        payload = {
            "caseExample": {
                "stagings": [
                    {
                        "stagingDomain": "tnm",
                        "caseId": str(staging.case_id),
                        "date": str(staging.date),
                        "stage": {"code": stage_code},
                        "primaryTumor": {"code": t_code},
                    }
                ],
            }
        }
        pqs = patient_cases_queryset_for_case_example(payload)
        compiler = pqs.query.get_compiler(using=pqs.db)
        sql, _params = compiler.as_sql()
        self.assertIn("oncology_staging", sql.lower())

        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_staging", full)

        n = pqs.count()
        self.assertGreaterEqual(n, 1)
        self.assertIn(staging.case_id, pqs.values_list("pk", flat=True))

    def test_genomic_variant_row_q_includes_gene_panel_in_sql(self):
        from onconova.oncology import models as orm
        from onconova.oncology.match_count import (
            _genomic_variant_row_q,
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        q = _genomic_variant_row_q({"genePanel": {"code": "MSK-IMPACT-CNA"}})
        self.assertIsNotNone(q)
        qs = orm.PatientCase.objects.all().filter(q)
        compiler = qs.query.get_compiler(using=qs.db)
        sql, _params = compiler.as_sql()
        lowered = sql.lower()
        self.assertIn("oncology_genomicvariant", lowered)
        self.assertIn("gene_panel", lowered)

        payload = {
            "genomicVariants": [
                {
                    "genePanel": {"code": "MSK-IMPACT-CNA"},
                    "cytogeneticLocation": {"code": "13q14.2"},
                }
            ]
        }
        pqs = patient_cases_queryset_for_case_example(payload)
        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_genomicvariant", full)

    def test_genomic_variant_protein_hgvs_only_filters_cases(self):
        """Functional-agg rows with only ``proteinHgvs`` must constrain EXISTS on ``protein_hgvs``."""
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        hgvs = "NP_003997.1:p.Trp24Cys"
        gv_match = GenomicVariantFactory.create(protein_hgvs=hgvs)
        GenomicVariantFactory.create(protein_hgvs="NP_003997.1:p.Trp24Ter")

        payload = {"caseExample": {"genomicVariants": [{"proteinHgvs": hgvs}]}}
        pqs = patient_cases_queryset_for_case_example(payload)
        ids = set(pqs.values_list("pk", flat=True))
        self.assertEqual(ids, {gv_match.case_id})

        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_genomicvariant", full)
        self.assertIn("protein_hgvs", full)

        n = pqs.count()
        self.assertEqual(n, 1)

    def test_genomic_variant_genes_array_filters_cases(self):
        import onconova.terminology.models as terminology
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        sys_uri = "http://test.example/terminology/sim-count-gene"
        g1, _ = terminology.Gene.objects.get_or_create(
            code="SIM-GENE-A",
            system=sys_uri,
            defaults={"display": "Sim gene A"},
        )
        g2, _ = terminology.Gene.objects.get_or_create(
            code="SIM-GENE-B",
            system=sys_uri,
            defaults={"display": "Sim gene B"},
        )
        gv_match = GenomicVariantFactory.create()
        gv_match.genes.set([g1])
        gv_other = GenomicVariantFactory.create()
        gv_other.genes.set([g2])

        payload = {
            "caseExample": {
                "genomicVariants": [{"genes": [{"code": g1.code}]}],
            }
        }
        pqs = patient_cases_queryset_for_case_example(payload)
        ids = set(pqs.values_list("pk", flat=True))
        self.assertEqual(ids, {gv_match.case_id})

        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_genomicvariant", full)

        self.assertEqual(pqs.count(), 1)

    def test_genomic_variant_dna_hgvs_filters_cases(self):
        from onconova.oncology.match_count import (
            interpolated_sql_for_case_example_filter,
            patient_cases_queryset_for_case_example,
        )

        dna = "NM_000123.1:c.100A>G"
        gv_match = GenomicVariantFactory.create(dna_hgvs=dna)
        GenomicVariantFactory.create(dna_hgvs="NM_000123.1:c.200T>C")

        payload = {"caseExample": {"genomicVariants": [{"dnaHgvs": dna}]}}
        pqs = patient_cases_queryset_for_case_example(payload)
        ids = set(pqs.values_list("pk", flat=True))
        self.assertEqual(ids, {gv_match.case_id})

        full = interpolated_sql_for_case_example_filter(pqs).lower()
        self.assertIn("oncology_genomicvariant", full)
        self.assertIn("dna_hgvs", full)

        self.assertEqual(pqs.count(), 1)
