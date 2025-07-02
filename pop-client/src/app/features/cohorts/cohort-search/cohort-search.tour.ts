import { Config } from "driver.js";

const TourDriverConfig: Config = {
    showProgress: true,
    steps: [
        { element: '.cohort-search-results-count', popover: { 
            side: "bottom", align: 'center', 
            title: 'Result Count',
            description: 'Shows the total number of cases that match the search criteria.', 
        }},
        { element: '.cohort-search-filters', popover: { 
            side: "bottom", align: 'center', 
            title: 'Filters',
            description: 'These widgets allow you to filter cohorts by their attributes.', 
        }},
        { element: '#cohort-search-refresh-cohorts-button', popover: { 
            side: "bottom", align: 'center', 
            title: 'Refresh Cohorts',
            description: 'You can manually refresh the results using this button.', 
        }},
        { element: '#cohort-search-new-cohort-button', popover: { 
            side: "bottom", align: 'center', 
            title: 'Adding New Cohorts',
            description: 'If you have the appropriate permissions, clicking this button will open a form to register a new cohort.', 
        }},
        { element: 'pop-cohort-search-item:nth-of-type(1)', popover: { 
            side: "right", align: 'center', 
            title: 'Cohort Overview',
            description: 'For each cohort matching your search criteria you will see a card containing an overview of the cohort.', 
        }},
        { element: 'pop-cohort-search-item:nth-of-type(1) .p-splitbutton-button', popover: { 
            side: "right", align: 'center', 
            title: 'Opening the Cohort',
            description: 'Click to open the details and management page for the selected cohort.', 
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('pop-cohort-search-item:nth-of-type(1) .p-splitbutton-dropdown') as HTMLElement;
                if (element) {
                    element.click();
                }
                setTimeout(() => {
                        driver.moveNext();
                }, 250);
            }
        }},
        { element: 'pop-cohort-search-item:nth-of-type(1) .p-tieredmenu-item.export-action', popover: { 
            side: "right", align: 'center', 
            title: 'Exporting Cohort Definitions',
            description: 'The definition of a cohort (not its data) can be exported as in a format that can be imported into other systems.', 
        }},
        { element: 'pop-cohort-search-item:nth-of-type(1) .p-tieredmenu-item.delete-action', popover: { 
            side: "right", align: 'center', 
            title: 'Deleting Cohort',
            description: 'Administrators can delete cohort cases in exceptional cases.', 
            onNextClick: (el, step, {config, state, driver}) => {
                (document.querySelector('body') as HTMLElement).click()
                driver.moveNext();
            }
        }},
        { element: '.p-paginator', popover: { 
            side: "top", align: 'center', 
            title: 'Pagination',
            description: 'You can browse through the different result pages using this toolbar.', 
        }},
        {popover: { 
            side: "left", align: 'center', 
            title: 'Finished',
            description: `Congratulations! This is the end of the tour for the cohort explorer page.`, 
        }},
    ]
};
export default TourDriverConfig;