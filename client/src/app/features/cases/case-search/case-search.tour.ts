import { Config } from "driver.js";

const TourDriverConfig: Config = {
    showProgress: true,
    steps: [
        { element: '.case-search-filters', popover: { 
            side: "bottom", align: 'center', 
            title: 'Filters',
            description: 'These widgets allow you to filter cases by their attributes.', 
        }},
        { element: '#case-manager-refresh-cases-button', popover: { 
            side: "bottom", align: 'center', 
            title: 'Refresh Cases',
            description: 'You can manually refresh the results using this button.', 
        }},
        { element: '#case-manager-new-case-button', popover: { 
            side: "bottom", align: 'center', 
            title: 'Adding New Cases',
            description: 'If you have the appropriate permissions, clicking this button will open a form to register a new patient case.', 
        }},
        { element: '.case-search-results-count', popover: { 
            side: "bottom", align: 'center', 
            title: 'Result Count',
            description: 'Shows the total number of cases that match the search criteria.', 
        }},
        { element: '.case-search-sorting', popover: { 
            side: "bottom", align: 'center', 
            title: 'Result Ordering',
            description: 'You can change the order of the results using these widgets.', 
        }},
        { element: '.layout-buttons', popover: { 
            side: "bottom", align: 'center', 
            title: 'Layout',
            description: 'You can change the layout of the results between a list and a grid using these widgets.', 
        }},
        { element: 'onconova-case-search-item:nth-of-type(1), tr:nth-of-type(2)', popover: { 
            side: "right", align: 'center', 
            title: 'Case Details',
            description: 'For each case matching your search criteria you will see a card containing the basic details of the case.', 
        }},
        { element: 'onconova-case-search-item:nth-of-type(1) .p-splitbutton-button, tr:nth-of-type(2) .p-splitbutton-button', popover: { 
            side: "right", align: 'center', 
            title: 'Accessing the Case',
            description: 'This button will open the case details and management page for the selected case.', 
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('onconova-case-search-item:nth-of-type(1) .p-splitbutton-dropdown, tr:nth-of-type(2) .p-splitbutton-dropdown') as HTMLElement;
                if (element) {
                    element.click();
                }
                setTimeout(() => {
                        driver.moveNext();
                }, 250);
            }
        }},
        { element: '.p-tieredmenu-item:nth-of-type(1)', popover: { 
            side: "right", align: 'center', 
            title: 'Exporting Cases',
            description: 'Users with elevated rights (e.g. project leaders) can export the patient case data as a bundle that can be imported into other systems.', 
        }},
        { element: '.p-tieredmenu-item:nth-of-type(2)', popover: { 
            side: "right", align: 'center', 
            title: 'Exporting Cases',
            description: 'You can delete an erroneous patient case with this option.', 
        }},
        { element: '.p-tieredmenu-item:nth-of-type(3)', popover: { 
            side: "right", align: 'center', 
            title: 'Updating Patient Details',
            description: 'Opens a form to update the details of the patient case.', 
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
            description: `Congratulations! This is the end of the tour for the case explorer page.`, 
        }},
    ]
};
export default TourDriverConfig;