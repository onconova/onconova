from django.db import models
from django.db.models import Q, Min, Max, Func, Case, When, Value, F, Subquery, OuterRef
from django.db.models.functions import Concat, Left, Greatest, Least, Lower, Upper, Now, Cast

from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager

import django.contrib.postgres.fields as postgres
from django.utils.translation import gettext_lazy as _
from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase, TreatmentResponse
import pop.terminology.models as terminology


class TherapyLine(BaseModel):
 
    objects = QueryablePropertiesManager()
    
    class TreatmentIntent(models.TextChoices):
        CURATIVE = 'curative'
        PALLIATIVE = 'palliative'
        
    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient to whom this therapy line is associated"),
        to = PatientCase,
        related_name = 'therapy_lines',
        on_delete = models.CASCADE,
    )
    ordinal = models.PositiveIntegerField(
        verbose_name=_('Line ordinal number'),
        help_text=_("Number indicating the sequence in which this block of treatments were administered to the patient"),
    )
    intent = models.CharField(
        verbose_name = _('Intent'),
        help_text = _("Treatment intent of the system therapy"),
        choices = TreatmentIntent,
        max_length=30,
    )
    progression_date = models.DateField(
        verbose_name = _('Begin of progression'),
        help_text = _("Date at which progression was first detected, if applicable"),
        null=True, blank=True,        
    )
    label = models.GeneratedField(
        expression=Concat(Upper(Left("intent", 1)), models.Value('LoT'), 'ordinal', output_field=models.CharField),
        db_persist=True,
        output_field=models.CharField(),
    )
    period = AnnotationProperty(
        verbose_name = _('Time period'),
        annotation = Func(
            Least(
                Min(Lower('systemic_therapies__period')), 
                Min(Lower('radiotherapies__period')), 
                Min('surgeries__date'), 
                output_field=models.DateField()
            ),
            Greatest(
                Max(Upper('systemic_therapies__period')), 
                Max(Upper('radiotherapies__period')),
                Max('surgeries__date'), 
                output_field=models.DateField()
            ),
            models.Value('[]'),function='daterange', output_field=postgres.DateRangeField()
        )
    )
    progression_free_survival = AnnotationProperty(
        verbose_name = _('Progression free survival in days'),
        annotation = Case(
            When(Q(period__isnull=True), then=None),
            default=Func(
                Func(
                    Case(
                        When(progression_date__isnull=False, then=F('progression_date')),
                        default=Case(When(case__date_of_death__isnull=False, then=F('case__date_of_death')), default=Func(function='NOW')),
                        output_field=models.DateField()
                    ),
                    Func(F('period'), function='lower', output_field=models.DateField()),                    
                    function='AGE'
                ),
                function='EXTRACT',
                template="EXTRACT(EPOCH FROM %(expressions)s)",
                output_field=models.IntegerField()
            ) / Value(3600*24*30.436875),
        )
    )
    
    @property
    def description(self):
        return f'{self.label}'

    @staticmethod
    def assign_therapy_lines(case):
        # Codes required to query the database 
        PD = 'LA28370-7'
        TREATMENT_NOT_TOLERATED = terminology.TreatmentTerminationReason.objects.filter(code='407563006').first()

        def is_anti_hormonal(SACT):
            if not SACT:
                return False 
            return ['(Anti)hormonal'] == list(set([drug.drugDomain for drug in SACT.drugs if drug.drugDomain ]))

        def overlap(period1, period2):
            return period1.upper >= period2.lower and period2.upper >= period1.lower

        # Delete all existing therapy lines to assign them anew
        case.therapy_lines.all().delete()
        # Get all systemic_therapies for the given case
        systemic_therapies = case.systemic_therapies.order_by('period')
        # Group SACTs whose treatment periods overlap
        overlaping_systemic_therapies = []
        for current_therapy in systemic_therapies:
            for existing_group in overlaping_systemic_therapies:
                # Check conditions to see if current therapy should be added to an existing group of overlapping therapies
                if (
                    overlap(existing_group[-1].period, current_therapy.period) > 1  # 1. Their time-periods overlap
                    and not is_anti_hormonal(existing_group[-1])                    # 2. Exclusion rule for anti-hormonal treatments
                    and existing_group[-1].intent == current_therapy.intent         # 3. The treatment intent is the same as the last therapy
                    and existing_group[-1].role == current_therapy.role             # 4. The therapeutic role is the same as the last therapy
                    ):
                    existing_group.append(current_therapy)
                    break
            else:
                overlaping_systemic_therapies.append([current_therapy])
                
        # Initialize a counter of therapy lines
        line_counter = {'curative': 0, 'palliative': 0}
        for systemic_therapies in overlaping_systemic_therapies:
            # Get the previous (non-complimentary) SACT if exists
            previous_SACT = case.systemic_therapies.exclude(is_adjunctive=True).filter(period__startswith__lt=systemic_therapies[0].period.lower)
            previous_SACT = previous_SACT.latest('period__startswith') if previous_SACT.exists() else None
            
            # Determine the intent of the therapy line (PLoT/CLoT)
            line_intent = systemic_therapies[0].intent or ('palliative' if case.neoplastic_entities.filter(relationship='metastatic').exists() else 'curative')
            
            # Auxiliary functions to assign SACT to a therapy line 
            def assign_therapy_to_previous_line():
                previous_therapy_line = case.therapy_lines.get(intent=line_intent, ordinal=line_counter[line_intent])
                for systemic_therapy in systemic_therapies:
                    systemic_therapy.therapy_line = previous_therapy_line
                    systemic_therapy.save()
                                    
            def assign_therapy_to_new_line():
                line_counter[line_intent] += 1 
                new_therapy_line = TherapyLine.objects.create(
                    case=case,
                    intent=line_intent,
                    ordinal=line_counter[line_intent],
                )    
                for systemic_therapy in systemic_therapies:
                    systemic_therapy.therapy_line = new_therapy_line
                    systemic_therapy.save()

            # If there are no lines of this type create the first one for this SACT
            if line_counter[line_intent]==0:
                assign_therapy_to_new_line()    
                continue
            
            # Check if the SACT is complimentary to another SACT (e.g. maintenance, additive, adjuvant, etc.)
            if systemic_therapies[0].is_adjunctive:
                assign_therapy_to_previous_line()
                continue
            
            # If there is a progressive disease (PD) since previous SACT, assign new therapy line
            if previous_SACT and case.treatment_responses.filter(recist__code=PD).filter(date__range=[previous_SACT.period.lower, systemic_therapies[0].period.lower]).exists() and not is_anti_hormonal(previous_SACT):
                assign_therapy_to_new_line()
                continue
                
            # If SACT was not tolerated by the patient... 
            if previous_SACT and previous_SACT.termination_reason == TREATMENT_NOT_TOLERATED:
                previous_SACT_drugs_class = '/'.join(set([drug.therapyCategory if drug.therapyCategory else drug.parent if drug.parent else 'Unknown' for drug in previous_SACT.drugs]))
                SACT_drugs_class = '/'.join(set([drug.therapyCategory if drug.therapyCategory else drug.parent  if drug.parent else 'Unknown' for therapy in systemic_therapies for drug in therapy.drugs]))        
                # ... assign a new therapy line only if the drugs used in the SACT are of a different class as the previous SACT
                if SACT_drugs_class == previous_SACT_drugs_class or is_anti_hormonal(previous_SACT):
                    assign_therapy_to_previous_line()
                    continue
                else:
                    assign_therapy_to_new_line()
                    continue

            # If the SACT use one or more new drugs than the previous SACT, assign a new line
            if (not previous_SACT or any([drug not in previous_SACT.drugs for SACT in systemic_therapies for drug in SACT.drugs])) and not is_anti_hormonal(previous_SACT):        
                assign_therapy_to_new_line()
                continue
            # If there are no reasons to assign to a new line, assign the SACT to the previous line 
            assign_therapy_to_previous_line()
        
        # Now that all therapy lines have been created, get all radiotherapies for the given case
        for radiotherapy in  case.radiotherapies.order_by('period__startswith'):
            therapy_line = case.therapy_lines.filter(intent=radiotherapy.intent).filter(period__overlap=radiotherapy.period).order_by('period').first()
            if therapy_line:
                radiotherapy.therapy_line = therapy_line
                radiotherapy.save()

        # Repeat for all surgeries of the given case
        for surgery in  case.surgeries.order_by('date'):
            therapy_line = case.therapy_lines.filter(intent=surgery.intent).filter(period__startswith__lte=surgery.date, period__endswith__gte=surgery.date).order_by('period').first()
            if therapy_line:
                surgery.therapy_line = therapy_line
                surgery.save()

        for therapy_line in case.therapy_lines.all():
            progression = TreatmentResponse.objects.filter(
                    case=case,
                    recist__code=PD,
                    date__gte=therapy_line.period.lower,
            )
            if progression.exists():
                therapy_line.progression_date = progression.earliest('date').date
            else:
                therapy_line.progression_date = None
            therapy_line.save()
                    