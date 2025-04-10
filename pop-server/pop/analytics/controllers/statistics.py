from typing import List

from django.db.models import F

from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra import api_controller, ControllerBase, route

from pop.oncology import models as oncological_models
from pop.analytics.schemas.statistics import EntityStatisticsSchema, DataPlatformStatisticsSchema, CasesPerMonthSchema
from pop.analytics.aggregates import Median


@api_controller(
    "/dashboard", 
    auth=[JWTAuth()], 
    tags=["Dashboard"]
)
class DashboardController(ControllerBase):

    @staticmethod
    def get_primary_sites():
        primary_entities = list(oncological_models.NeoplasticEntity.objects.filter(
                relationship=oncological_models.NeoplasticEntityRelationship.PRIMARY
        ).filter(topography__parent__isnull=False).values('topography__parent__code','topography__parent__display').distinct()) + \
        list(oncological_models.NeoplasticEntity.objects.filter(
                relationship=oncological_models.NeoplasticEntityRelationship.PRIMARY
        ).filter(topography__parent__isnull=True).values('topography__code','topography__display').distinct())

        primary_entities = set([(
            entity.get('topography__code') or entity.get('topography__parent__code'), 
            entity.get('topography__display') or entity.get('topography__parent__display')
        ) for entity in primary_entities])
        return primary_entities

    @route.get(
        path='/stats', 
        response={
            200: DataPlatformStatisticsSchema
        },
        operation_id='getFullCohortStatistics',
    )
    def get_full_cohort_statistics(self):
        return DataPlatformStatisticsSchema(
            cases = oncological_models.PatientCase.objects.count(),
            primarySites = len(self.get_primary_sites()),
            entries = sum([model.objects.count() for model in oncological_models.MODELS]),
            mutations = oncological_models.GenomicVariant.objects.count(),
            clinicalCenters = oncological_models.PatientCase.objects.distinct('clinical_center').count(),
            contributors = oncological_models.PatientCase.objects.select_properties('created_by').distinct('created_by').count(),
            projects = 0,
        )
    
    @route.get(
        path='/primary-site-stats', 
        response={
            200: List[EntityStatisticsSchema]
        },
        operation_id='getPrimarySiteStatistics',
    )
    def get_primary_site_statistics(self):
        primary_entities = self.get_primary_sites()
        statistics = []
        for (entity_code,entity_display) in primary_entities:
            entity_cohort = oncological_models.PatientCase.objects.filter(neoplastic_entities__topography__code__contains=entity_code).filter(neoplastic_entities__relationship=oncological_models.NeoplasticEntityRelationship.PRIMARY)
            statistics.append(EntityStatisticsSchema(
                population = entity_cohort.count(),                
                dataCompletionMedian = entity_cohort.aggregate(Median('data_completion_rate')).get('data_completion_rate__median'),
                topographyCode=entity_code,
                topographyGroup=entity_display,
                contributors=list(entity_cohort.select_properties('created_by').values_list('created_by', flat=True)) 
            ))
        statistics.sort(key=lambda x: x.population, reverse=True)
        return statistics
    
    @route.get(
        path='/cases-over-time', 
        response={
            200: List[CasesPerMonthSchema]
        },
        operation_id='getCasesOverTime',
    )
    def get_cases_over_time(self):
        from django.db.models.functions import TruncMonth
        from django.db.models import Count, Window
        from pop.oncology.models import PatientCase
        return PatientCase.objects.select_properties('created_at').annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                cumulativeCount=Window(expression=Count('id'), order_by=F('month').asc())
            ).order_by('month')
