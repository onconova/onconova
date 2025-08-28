import { Config } from "driver.js";

const TourDriverConfig: Config = {
    showProgress: true,
    steps: [
        { element: '.case-manager-header-summary', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Case Summary',
            description: 'Here you can view a summary of the patient case that will automatically update as data is added or updated.', 
        }},
        { element: '.case-manager-header-data-completion', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Case Data Completion',
            description: 'This meter will show the percentage of data categories that have been marked as completed. It serves as a proxy for the overall data quality of the patient case.', 
        }},
        { element: '.case-manager-header-metadata', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Metadata',
            description: 'The rest of the summary contains metadata such as the anonymization status of the data shown, data contributors for the case, and other information.', 
        }},
        { element: '#case-manager-export-case-button', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Exporting the Case',
            description: 'Users with elevated rights (e.g. project leaders) can export the patient case data as a bundle that can be imported into other systems.', 
        }},
        { element: '#case-manager-data-management-button', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Data Management Mode',
            description: 'By default cases cannot be edited. To enable/disable data management mode and remove the anonymization of the data, click on this button. This may require either an elevated role or permission from your project leader(s).', 
        }},
        { element: 'onconova-case-manager-panel:nth-of-type(1)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Data Category Panels',
            description: 'This is a data category panel where you can view, create and update data for the patient case.', 
        }},
        { element: '.onconova-case-manager-counter-badge:nth-of-type(1)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Entries Counter',
            description: 'This small badge indicates the number of entries for the data category for the current patient case.', 
        }},
        { element: '.onconova-case-manager-completion-indicator:nth-of-type(1)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Completion Indicator',
            description: `If a data category is marked as completed, a small star ★ icon will appear to indicate that this category has been completed.
            Completed categories will contribute towards the completion rate of the patient case. Note that completed categories cannot be modified unless they are reopened.`, 
        }},
        { element: '.onconova-case-manager-menu-button:nth-of-type(1)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Adding New Entries',
            description: `The "Add" button will open a modal form to create a new entry for the data category.<br>This option is only enabled if the data category is not completed and if data management has been enabled.`, 
        }},
        { element: '.onconova-case-manager-menu-button:nth-of-type(2)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Context Menu',
            description: `Each data category has a button which will open its own dedicated submenu.`, 
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.onconova-case-manager-menu-button:nth-of-type(2)') as HTMLElement;
                if (element) {
                    element.click();
                }
                setTimeout(() => {
                        driver.moveNext();
                }, 250);
            }
        }},
        { element: 'onconova-case-manager-panel .p-menu-item:nth-of-type(1)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Adding New Entries',
            description: `You can also add a new entry for the data category using this menu option.<br>Again, this option is only enabled if the data category is not completed and if data management has been enabled.`, 
        }},
        { element: 'onconova-case-manager-panel .p-menu-item:nth-of-type(2)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Refreshing Data',
            description: `The "Refresh" button can be used to reload the data for the data category from the server.`, 
        }},
        { element: 'onconova-case-manager-panel .p-menu-item:nth-of-type(4)', onconovaover: { 
            side: "right", align: 'center', 
            title: 'Completing A Category',
            description: `This last button allows the marking of a data category as complete or incomplete. Use this once all entries for a data category have been collected or when a completed category has developed new entries.`, 
            onNextClick: (el, step, {config, state, driver}) => {
                (document.querySelector('body') as HTMLElement).click()
                const element = document.querySelector('.onconova-case-manager-panel-timeline-event-entry:nth-of-type(1)') as HTMLElement;
                if (!element) {
                    driver.destroy()
                } else {
                    driver.moveNext()
                }
            }
        }},
        { element: 'onconova-case-manager-panel-timeline:nth-of-type(1)', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Timelines',
            description: `For each data category a timeline is provided listing all existing entries for that category.`, 
        }},
        { element: '.onconova-case-manager-panel-timeline-event-entry:nth-of-type(1)', onconovaover: { 
            side: "bottom", align: 'center', 
            title: 'Data Entries',
            description: `For each data entry a short description is provided. You can click on the entry to see the full details.`, 
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.onconova-case-manager-panel-timeline-event-entry:nth-of-type(1)') as HTMLElement;
                if (element) {
                    element.click();
                }
                setTimeout(() => {
                        driver.moveNext();
                }, 250);
            }
        }},
        { element: '.p-drawer', onconovaover: { 
            side: "left", align: 'center', 
            title: 'Data Details',
            description: `This panel contains the full details for the selected data entry.`, 
        }},
        { element: 'onconova-drawer-properties', onconovaover: { 
            side: "left", align: 'center', 
            title: 'Properties',
            description: `The section includes all editable data for the selected resource. Certain property values (e.g. codeable concepts) can be expanded to reveal additional information.`, 
        }},
        { element: '.onconova-case-manager-drawer-metadata', onconovaover: { 
            side: "left", align: 'center', 
            title: 'Metadata',
            description: `The section provides non-editable information about the selected resource.`, 
        }},
        { element: '.onconova-case-manager-drawer-history', onconovaover: { 
            side: "left", align: 'center', 
            title: 'History',
            description: `The section provides the full audit trail for this specific resource. You can check who and when the resource was created and/or updated.`, 
        }},
        { element: '.p-splitbutton-button', onconovaover: { 
            side: "left", align: 'center', 
            title: 'Updating resources',
            description: `Use this button to open the edit form for the selected resource if data management has been enabled.`, 
        }},
        { element: '.p-splitbutton-dropdown', onconovaover: { 
            side: "left", align: 'center', 
            title: 'Other actions',
            description: `Open this menu to access other actions related to the resource, such as deleting or exporting it.`, 
            onNextClick: (el, step, {config, state, driver}) => {
                (document.querySelector('.onconova-case-manager-drawer-hide-button') as HTMLElement).click()
                driver.moveNext()
            }
        }},
        {onconovaover: { 
            side: "left", align: 'center', 
            title: 'Finished',
            description: `Congratulations! This is the end of the tour for the case manager page.`, 
        }},
    ]
};

export default TourDriverConfig;