
import numpy as np 
from collections import Counter
from django.db.models import F, Subquery, OuterRef
from pop.research.models.cohort import Cohort
from pop.oncology.models import TherapyLine, SystemicTherapy
from statistics import NormalDist


def calculate_Kappler_Maier_survival_curve(survival_months, confidence_level=0.95):
    """
    Perform Kappler-Maier analysis to estimate survival probabilities and 95% confidence intervals.

    Parameters
    ----------
    survival_months : array_like
        Array containing the number of months survived for each patient.

    Returns
    -------
    survival_axis : ndarray
        Array of months survived, serving as the x-axis.
    est_survival_prob : ndarray
        Estimated survival probabilities corresponding to the survival axis.
    ci95 : dict
        Dictionary containing the upper and lower bounds of 95% confidence intervals
        for the estimated survival probabilities. The keys are 'upper' and 'lower'.

    Notes
    -----
    Uses the analytical Kaplan-Meier estimator [1] and computes the asymptotic 95% confidence intervals [2]
    using the log-log approach [3]. 

    References
    ----------
    [1] https://en.wikipedia.org/wiki/Kapla-Meier_estimator 
    [2] Fisher, Ronald (1925), Statistical Methods for Research Workers, Table 1
    [3] Borgan, Liestøl (1990). Scandinavian Journal of Statistics 17, 35-41
    """        
    # Ensure array
    survival_months = np.array(survival_months)
    # Remove None values
    survival_months = survival_months[survival_months != np.array(None)].astype(float)
    # Check that there are values in the array left    
    if len(survival_months)==0:
        raise ValueError('The input argument cannot be empty or None')

    # Round months to integers
    survival_months = np.round(survival_months,0)

    # Generate the axis of survived months
    survival_axis = np.arange(0, np.max(survival_months) + 1)
    
    # Determine the number of alive patients along the axis
    alive = np.array([sum(survival_months >= months_survived) for months_survived in survival_axis])
    
    # Determine the number of death events along the axis
    events = np.array([sum(survival_months == months_survived) for months_survived in survival_axis])
    
    # Truncate the axis regions where nothing more happens
    valid = alive > 0    
    survival_axis = survival_axis[valid]
    events = events[valid]
    alive = alive[valid]

    # Evaluate the KM survival probability estimator
    est_survival_prob = np.cumprod(1 - events / alive)

    # Evaluate its standard deviation
    std = np.sqrt(np.cumsum(events / (alive * (alive - events))) / np.log(est_survival_prob)**2)
    std[np.isnan(std)] = 0
    
    # Set the normal inverse CDF value for 95% confidence [2]
    z = NormalDist().inv_cdf(1 - (1 - confidence_level) / 2)
    
    # Compute the 95%-confidence intervals 
    confidence_bands = {
        "lower": (est_survival_prob**np.exp(+z*std)).tolist(), 
        "upper": (est_survival_prob**np.exp(-z*std)).tolist(),
    } 
    return survival_axis.tolist(), est_survival_prob.tolist(), confidence_bands


def get_progression_free_survival_for_therapy_line(cohort: Cohort, exclude_filters={}, **include_filters,):
    return list(cohort.cases.annotate(progression_free_survival=
            Subquery(
                TherapyLine.objects.filter(
                        case_id=OuterRef('id'), 
                         **include_filters
                ).exclude(**exclude_filters).annotate(
                    progression_free_survival=F('progression_free_survival')
                ).values_list('progression_free_survival', flat=True)[:1]
            ) 
        ).filter(progression_free_survival__isnull=False).values_list('progression_free_survival', flat=True))


def calculate_pfs_by_combination_therapy(cohort: Cohort, therapyLine: str):
    drug_combinations = cohort.cases.annotate(drug_combination=Subquery(
            SystemicTherapy.objects.filter(case_id=OuterRef('id'), therapy_line__label=therapyLine).annotate(
                drug_combination=F('drug_combination')
            ).values_list('drug_combination', flat=True)[:1]
        )).filter(drug_combination__isnull=False).values_list('drug_combination', flat=True)
    
    survival_per_combination = {combo[0]: None for combo in Counter(drug_combinations).most_common(4)}
    for combination in survival_per_combination.keys():
        survival_per_combination[combination] = get_progression_free_survival_for_therapy_line(cohort,
            label=therapyLine,
            systemic_therapies__drug_combination=combination,
        )
    survival_per_combination['Others'] = get_progression_free_survival_for_therapy_line(cohort,
        label=therapyLine,
        exclude_filters=dict(systemic_therapies__drug_combination__in=list(survival_per_combination.keys()))
    )
    return survival_per_combination


def calculate_pfs_by_therapy_classification(cohort: Cohort, therapyLine: str):

    def _parse_category_name(value):
        def pop_from_list(list, value):
            try: 
                index = list.index(value)
            except ValueError:
                return None 
            list.remove(value)
            return value        
        categories = value.split(',')
        if 'chemotherapy' in categories and 'immunotherapy' in categories:
            categories.remove('chemotherapy')
            categories.remove('immunotherapy')
            categories.insert('chemoimmunotherapy',0)
        radiotherapy = pop_from_list(categories, 'radiotherapy')
        if radiotherapy and len(categories)==1:
            return f'Radio{categories[0]}'
        else:
            return ' & '.join(categories).title()


        


    therapy_classifications = TherapyLine.objects.filter(case__in=cohort.cases.all()).filter(label=therapyLine).annotate(therapy_classification=F('therapy_classification')).values_list('therapy_classification', flat=True)
    
    most_common = [category[0] for category in  Counter(therapy_classifications).most_common(4)]
    survival_per_classification = {_parse_category_name(category): None for category in most_common}
    for classification in most_common:
        survival_per_classification[_parse_category_name(classification)] = get_progression_free_survival_for_therapy_line(cohort,
            label=therapyLine,
            therapy_classification=classification,
        )
    survival_per_classification['Others'] = get_progression_free_survival_for_therapy_line(cohort,
        label=therapyLine,
        exclude_filters=dict(therapy_classification=list(survival_per_classification.keys()))
    )
    return survival_per_classification