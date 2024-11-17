from django.core.management.base import BaseCommand
from django.utils import timezone
from pop.terminology.utils import ValueSetComposer, printRed, printGreen, load_SNOMED_database
import django.apps 
import traceback

class Command(BaseCommand):
    """
    Django management command to synchronize valuesets in the database.

    This command allows synchronizing valuesets in the database with external sources.
    It provides options to skip existing valuesets, force a reset, and specify
    which valuesets to synchronize.

    Usage:
        python manage.py synchronize_valuesets --valuesets <valueset_names> --skip-existing --force-reset

    Args:
        --valuesets: A list of valueset names to synchronize. Use 'all' to synchronize all valuesets.
        --skip-existing: Skip valuesets that already contain entries.
        --force-reset: Reset all valuesets prior to synchronization (WARNING: Will trigger deletion cascades in the rest of the database).
        --prune-dangling: Delete all dangling concepts in the database that are not collected by the valueset (WARNING: Will trigger deletion cascades in the rest of the database).
        --collection-limit: Limit the number of concepts to be collected. For testing and debugging purposes.

    Example:
        python manage.py synchronize_valuesets --valuesets CTCAETerms MedicationClinicalDrugsIngredients --skip-existing
    """
    
    help = """Synchronizes valuesets in the database"""    

    #------------------------------------------------------------------------------------------
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '--valuesets', 
            nargs='+', 
            type=str,
            default='all'
        )
        # Named (optional) arguments
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Debug mode (no database changes)',
            default=False,
        )   
        # Named (optional) arguments
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip valuesets containing entries',
            default=False,
        )    
        parser.add_argument(
            '--force-reset',
            action='store_true',
            default=False,
            help='Resets all valuesets prior to synchronization (WARNING: Will trigger deletion cascades in the rest of the database)',
        )    
        parser.add_argument(
            '--prune-dangling',
            action='store_true',
            default=False,
            help='Delete all dangling concepts in the database that are not collected by the valueset (WARNING: Will trigger deletion cascades in the rest of the database)',
        )    
        parser.add_argument(
            '--collection-limit',
            type=int,
            default=9999999999,
            help='Limit the number of concepts to be collected. For testing and debugging purposes.',
        )   
        parser.add_argument(
            '--raise-failed',
            action='store_true',
            default=False,
            help='Raise failed valueset synchronizations as exceptions instead of printing them.',
        )   
    #------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------
    def handle(self, *args, **options):
        """
        Main handler for the 'synchronize_valuesets' command.

        Args:
            *args: Unused positional arguments.
            **options: Command-line options.
        """
        # Get list of models defined on Django
        if options['valuesets']=='all':
            valueset_models = list(django.apps.apps.get_app_config('terminology').get_models())
        else:
            valueset_models = [django.apps.apps.get_model('terminology', valueset_name) for valueset_name in options['valuesets']]
        
        if options['debug']:
            print('\n ⓘ Debug mode enabled (database state will remain unchanged)')

        # loop through the subset of matching models and delete entries 
        total_synchronized = 0
        failed = []
        for valueset_model in valueset_models:
            
            # Skip special models
            if valueset_model.__name__ in ['TreeStructure','UnifiedCodesForUnitsOfMeasure']:
                continue
            
            try:
                ValueSetComposer(valueset_model, 
                    skip_existing=options['skip_existing'], 
                    force_reset=options['force_reset'],
                    prune_dangling=options['prune_dangling'],
                    concepts_limit=options['collection_limit'],
                    debug_mode=options['debug'],
                ).compose()
                total_synchronized += 1
            except: 
                if options['raise_failed']:
                    traceback.print_exc()
                    raise RuntimeError(f'Failed to synchronize model {valueset_model.__name__}')
                else:
                    printRed(f'ERROR: Failed to synchronize model {valueset_model.__name__}' )    
                    failed.append(valueset_model.__name__)
                    traceback.print_exc()
        
        # Clear the SNOMED CT terminology from memory
        if load_SNOMED_database.cache_info().currsize > 0:
            load_SNOMED_database.cache_clear()
            print('\n ⓘ SNOMED CT terminology cache cleared succesfully.')
        
        print('\n-------------------------------------------')
        print('SUMMARY')
        if total_synchronized>0:
            printGreen(f"✓ {total_synchronized} valueset(s) synchronized succesfully.")
        if failed:
            printRed(f"❌The following {len(failed)} valueset(s) failed to synchronize:")
            for fail in failed:
                printRed(f"Valueset: <{fail}>")
        print('-------------------------------------------')                
        print()
    #------------------------------------------------------------------------------------------