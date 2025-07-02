import { Config } from "driver.js";

const TourDriverConfig: Config = {
    showProgress: true,
    steps: [
        { element: '.pop-cohort-manager-header', popover: { 
            side: "right", align: 'start', 
            title: 'Cohort Information',
            description: 'You can see all metadata associated with this cohort', 
        }},
        { element: '#cohort-manager-edit-name-button', popover: { 
            side: "right", align: 'start', 
            title: "Change the Cohort's Title",
            description: 'You can change the title of this cohort by clicking this button.', 
        }},
        { element: '.cohort-manager-stats', popover: { 
            side: "right", align: 'start', 
            title: "Cohort Statistics",
            description: 'A collection of aggregated statistics that will update as the cohort is updated. Uncertainties are shown for certain values as interquartile ranges.', 
        }},
        { element: '.cohort-manager-cohort-definition', popover: { 
            side: "right", align: 'start', 
            title: "Cohort Composition Criteria",
            description: 'These widget allow you to define the criteria used to define which cases are included and/or excluded in this cohort.', 
        }},
        { element: 'pop-cohort-query-builder:nth-of-type(1)', popover: { 
            side: "top", align: 'start', 
            title: "Cohort Ruleset",
            description: 'This is a ruleset, a a set of rules chained by logical operators (and/or).', 
        }},
        { element: '.q-condition-select:nth-of-type(1)', popover: { 
            side: "top", align: 'start', 
            title: "Logical Operators",
            description: 'Use this selector to define the logical operator used to chain the rules within the ruleset.', 
        }},
        { element: '.q-rule:nth-of-type(1)', popover: { 
            side: "top", align: 'start', 
            title: "Rules",
            description: 'This is a rule, the basic element for creating the query that will be used to filter the cohort cases.', 
        }},
        { element: '.q-entity-select:nth-of-type(1)', popover: { 
            side: "top", align: 'center', 
            title: "Rule - Resource",
            description: 'A rule centers around a resource and a set of conditions. This rule will select all patient cases that have such a resource matching all conditions.', 
        }},
        { element: '.q-filters-container:nth-of-type(1)', popover: { 
            side: "top", align: 'center', 
            title: "Rule - Conditions",
            description: 'This one of the conditions of a rule that will be applied to the resource.', 
        }},
        { element: '.q-field-select:nth-of-type(1)', popover: { 
            side: "top", align: 'center', 
            title: "Rules - Field",
            description: 'Each condition is applied to a specific property of the resource', 
        }},
        { element: '.q-filters-description-icon:nth-of-type(1)', popover: { 
            side: "top", align: 'center', 
            title: "Rules - Field Description",
            description: 'Hovering over this question mark will display the description of the selected property.', 
        }},
        { element: '.q-operator-select', popover: { 
            side: "top", align: 'center', 
            title: "Rules - Operator",
            description: 'The operator choice will determine the type of filter/comparison that will be applied to the that property.', 
        }},
        { element: '.q-rule-value-container:nth-of-type(1)', popover: { 
            side: "top", align: 'center', 
            title: "Rules - Value",
            description: 'You will be prompted to enter a value against which to evaluate the condition.', 
        }},
        { element: '.rule-filter-button-group:nth-of-type(1)', popover: { 
            side: "left", align: 'center', 
            title: "Rules - Actions",
            description: 'You can add and remove conditions to a rule by using these buttons.', 
        }},
        { element: '.q-rule-add-button:nth-of-type(1)', popover: { 
            side: "left", align: 'center', 
            title: "Chaining Rules",
            description: 'You can add and chain additional rules within a ruleset by clicking this button.', 
        }},
        { element: '.q-ruleset-add-button:nth-of-type(1)', popover: { 
            side: "left", align: 'center', 
            title: "Nested Rulesets",
            description: 'Similarly, you can create nested rulesets by clicking this button. Nested rulesets can have different logical operators allowing you to create complex queries.', 
        }},

        { element: '.cohort-manager-save-button', popover: { 
            side: "top", align: 'center', 
            title: "Updating the Cohort",
            description: 'Submits the current cohort definition criteria and updates the cases in the cohort (and all other derived metrics).', 
        }},
        { element: '.p-tablist', popover: { 
            side: "top", align: 'center', 
            title: "Cohort Composition",
            description: 'A collection of results related to the cohort composition. You can switch betewen the different tabs.',
        }},
        { element: '.pop-cohort-manager-tabs .p-tab:nth-of-type(1)', popover: { 
            side: "top", align: 'center', 
            title: "Cohort Composition",
            description: 'A list of all cases included in the cohort. ',
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(1)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.moveNext()
            },
        }},
        { element: '.p-tabpanels', popover: { 
            side: "top", align: 'start', 
            title: "Cohort Composition",
            description: 'The list of cohort cases behaves exactly as the case explorer entries.',  
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(2)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.moveNext()
            },
        }},
        { element: '.pop-cohort-manager-tabs .p-tab:nth-of-type(2)', popover: { 
            side: "top", align: 'center', 
            title: "Cohort Analysis",
            description: 'A collection of of aggregated data analyses represented graphically.', 
            onPrevClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(1)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.movePrevious()
            }
        }},
        { element: '.p-tabpanels canvas:nth-of-type(1)', popover: { 
            side: "top", align: 'start', 
            title: "Cohort Analysis Graphs",
            description: "All graphs are interactive and show additiona data when hovered over. Categories can be blended in and out by interacting with the legend. You can download the graph's data or the graph itself as an image by right-clicking any graph.",  
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(3)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.moveNext()
            },
        }},
        { element: '.pop-cohort-manager-tabs .p-tab:nth-of-type(3)', popover: { 
            side: "top", align: 'center', 
            title: "Datasets",
            description: 'A tool to view, manage, adn export data associated with this cohort.', 
            onPrevClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(2)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.movePrevious()
            }
        }},
        { element: '.load-dataset-button', popover: { 
            side: "top", align: 'center', 
            title: "Loading datasets",
            description: `If available, you can load any of your project's dataset definitions.`,
        }},
        { element: '.pop-data-selector-tree', popover: { 
            side: "top", align: 'center', 
            title: "Creating Datasets",
            description: `Search and select any data elements and they will be added to the dataset preview table.`,
        }},
        { element: '.pop-dataset-table', popover: { 
            side: "top", align: 'center', 
            title: "Dataset Preview",
            description: `You can interact with the live dataset data in this table. Nested data elements can be expanded and collapsed by clicking on them.`,
        }},
        { element: '.dataset-save-button', popover: { 
            side: "top", align: 'center', 
            title: "Dataset Saving",
            description: `Before a dataset can be exported, any changes must be saved.`,
        }},
        { element: '.dataset-metadata-form', popover: { 
            side: "top", align: 'center', 
            title: "Dataset Details",
            description: `To save the dataset, you may need to add some details.`,
        }},
        { element: '.dataset-download-button', popover: { 
            side: "top", align: 'center', 
            title: "Exporting Datasets",
            description: `The saved dataset can be exported for all cases in the cohort. Clicking will prompt you to select a data format. Only project leaders (or administrators) can export datasets for other users.`,
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(4)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.moveNext()
            },
        }},
        { element: '.pop-cohort-manager-tabs .p-tab:nth-of-type(4)', popover: { 
            side: "top", align: 'center', 
            title: "Contributors",
            description: 'A ranking of contributors to the data contained in this cohort.', 
            onNextClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(5)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.moveNext()
            },
            onPrevClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(3)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.movePrevious()
            }
        }},
        { element: '.pop-cohort-manager-tabs .p-tab:nth-of-type(5)', popover: { 
            side: "top", align: 'center', 
            title: "History",
            description: 'The audit trail of the cohort, containing all changes and data exports associated to the cohort.', 
            onPrevClick: (el, step, {config, state, driver}) => {
                const element = document.querySelector('.pop-cohort-manager-tabs .p-tab:nth-of-type(4)') as HTMLElement;
                if (element) {
                    element.click();
                }
                driver.movePrevious()
            }
        }},
        {popover: { 
            side: "left", align: 'center', 
            title: 'Finished',
            description: `Congratulations! This is the end of the tour for the cohort manager page.`, 
        }},
    ]
};
export default TourDriverConfig;