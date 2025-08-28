import { Config } from "driver.js";

const TourDriverConfig: Config = {
    showProgress: true,
    steps: [
        { element: '.project-search-filters', popover: { 
            side: "bottom", align: 'center', 
            title: 'Filters',
            description: 'These widgets allow you to filter projects by their attributes.', 
        }},
        { element: '#project-search-refresh-projects-button', popover: { 
            side: "bottom", align: 'center', 
            title: 'Refresh Projects',
            description: 'You can manually refresh the results using this button.', 
        }},
        { element: '#project-search-new-project-button', popover: { 
            side: "bottom", align: 'center', 
            title: 'Adding New Projects',
            description: 'If you have the appropriate permissions, clicking this button will open a form to register a new project.', 
        }},
        { element: '.project-search-results-count', popover: { 
            side: "bottom", align: 'center', 
            title: 'Result Count',
            description: 'Shows the total number of projects that match the search criteria.', 
        }},
        { element: '.project-search-sorting', popover: { 
            side: "bottom", align: 'center', 
            title: 'Result Ordering',
            description: 'You can change the order of the results using these widgets.', 
        }},
        { element: '.layout-buttons', popover: { 
            side: "bottom", align: 'center', 
            title: 'Layout',
            description: 'You can change the layout of the results between a list and a grid using these widgets.', 
        }},
        { element: 'onconova-project-search-item:nth-of-type(1)', popover: { 
            side: "right", align: 'center', 
            title: 'Project Overview',
            description: 'For each project matching your search criteria you will see a card containing an overview of the project.', 
        }},
        { element: 'onconova-project-search-item:nth-of-type(1) .p-splitbutton-button', popover: { 
            side: "right", align: 'center', 
            title: 'Opening the Project',
            description: 'Click to open the details and management page for the selected project.', 
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('onconova-project-search-item:nth-of-type(1) .p-splitbutton-dropdown') as HTMLElement;
                if (element) {
                    element.click();
                }
                setTimeout(() => {
                        driver.moveNext();
                }, 250);
            }
        }},
        { element: 'onconova-project-search-item:nth-of-type(1) .p-tieredmenu-item:nth-of-type(1)', popover: { 
            side: "right", align: 'center', 
            title: 'Updating Project Details',
            description: 'Opens a form to update the details of the project.', 
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
            description: `Congratulations! This is the end of the tour for the project explorer page.`, 
        }},
    ]
};
export default TourDriverConfig;