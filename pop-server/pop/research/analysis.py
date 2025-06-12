
from collections import Counter
from django.db.models import F, Subquery, OuterRef
from pop.research.models.cohort import Cohort
from pop.oncology.models import TherapyLine, SystemicTherapy
from statistics import NormalDist
import math
from statistics import NormalDist

def calculate_Kappler_Maier_survival_curve(
        survival_months, confidence_level=0.95):
    """
    Performs Kappler-Maier analysis to estimate survival probabilities and 95% confidence intervals.

    Args:
        survival_months (array_like): Array containing the number of months survived for each
            patient.
        confidence_level (float): Confidence level for the confidence interval (0.95 default).

    Returns:
        survival_axis (ndarray): Array of months survived, serving as the x-axis.
        est_survival_prob (ndarray): Estimated survival probabilities corresponding to the
            survival axis.
        ci95 (dict): Dictionary containing the upper and lower bounds of 95% confidence
            intervals for the estimated survival probabilities. The keys are 'upper' and 'lower'.

    Notes:
        Uses the analytical Kaplan-Meier estimator 1_ and computes the asymptotic 95%
        confidence intervals 2_ using the log-log approach 3_.

    References:
        .. [1]  https://en.wikipedia.org/wiki/Kapla-Meier_estimator
        .. [2]  Fisher, Ronald (1925), Statistical Methods for Research Workers, Table 1
        .. [3]  Borgan, Liestøl (1990). Scandinavian Journal of Statistics 17, 35-41
    """
    # Remove None values and convert to floats
    survival_months = [float(m) for m in survival_months if m is not None]
    # Check that there are values in the array left    
    if len(survival_months)==0:
        raise ValueError('The input argument cannot be empty or None')

    # Round months to integers
    survival_months = [round(m) for m in survival_months]

    # Generate the axis of survived months
    max_month = int(max(survival_months))
    survival_axis = list(range(0, max_month + 1))

    # Determine the number of alive patients along the axis
    alive = [sum(m >= month for m in survival_months) for month in survival_axis]

    # Determine the number of death events along the axis
    events = [sum(m == month for m in survival_months) for month in survival_axis]
    
    # Truncate the axis regions where nothing more happens
    valid_indices = [i for i, a in enumerate(alive) if a > 0]   
    survival_axis = [survival_axis[i] for i in valid_indices]
    alive = [alive[i] for i in valid_indices]
    events = [events[i] for i in valid_indices]

    # Evaluate the KM survival probability estimator
    est_survival_prob = []
    cumulative_product = 1.0

    for e, a in zip(events, alive):
        cumulative_product *= (1 - e / a)
        est_survival_prob.append(cumulative_product)

    # Evaluate its standard deviation
    cumulative_sum = 0.0
    std = []
    for p, e, a in zip(est_survival_prob, events, alive):
        if a == 0 or a - e == 0:
            std.append(0.0)
            continue
        increment = e / (a * (a - e))
        if increment <= 0:
            std.append(0.0)
            continue
        cumulative_sum += increment
        std_val = math.sqrt(cumulative_sum / math.log(p) ** 2)
        std.append(std_val)

    # Set the normal inverse CDF value for confidence level
    z = NormalDist().inv_cdf(1 - (1 - confidence_level) / 2)
    
    # Compute the 95%-confidence intervals 
    confidence_bands = {
        "lower": [p ** math.exp(+z * s) for p, s in zip(est_survival_prob, std)],
        "upper": [p ** math.exp(-z * s) for p, s in zip(est_survival_prob, std)],
    }

    return survival_axis, est_survival_prob, confidence_bands

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