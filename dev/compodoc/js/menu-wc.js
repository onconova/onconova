'use strict';

customElements.define('compodoc-menu', class extends HTMLElement {
    constructor() {
        super();
        this.isNormalMode = this.getAttribute('mode') === 'normal';
    }

    connectedCallback() {
        this.render(this.isNormalMode);
    }

    render(isNormalMode) {
        let tp = lithtml.html(`
        <nav>
            <ul class="list">
                <li class="title">
                    <a href="index.html" data-type="index-link">Application documentation</a>
                </li>

                <li class="divider"></li>
                ${ isNormalMode ? `<div id="book-search-input" role="search"><input type="text" placeholder="Type to search"></div>` : '' }
                <li class="chapter">
                    <a data-type="chapter-link" href="index.html"><span class="icon ion-ios-home"></span>Getting started</a>
                    <ul class="links">
                        <li class="link">
                            <a href="overview.html" data-type="chapter-link">
                                <span class="icon ion-ios-keypad"></span>Overview
                            </a>
                        </li>
                        <li class="link">
                            <a href="index.html" data-type="chapter-link">
                                <span class="icon ion-ios-paper"></span>README
                            </a>
                        </li>
                    </ul>
                </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#components-links"' :
                            'data-bs-target="#xs-components-links"' }>
                            <span class="icon ion-md-cog"></span>
                            <span>Components</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="components-links"' : 'id="xs-components-links"' }>
                            <li class="link">
                                <a href="components/AbstractFormBase.html" data-type="entity-link" >AbstractFormBase</a>
                            </li>
                            <li class="link">
                                <a href="components/AdverseEventFormComponent.html" data-type="entity-link" >AdverseEventFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AppComponent.html" data-type="entity-link" >AppComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AppFooterComponent.html" data-type="entity-link" >AppFooterComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AppLayoutComponent.html" data-type="entity-link" >AppLayoutComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AppSidebarMenuComponent.html" data-type="entity-link" >AppSidebarMenuComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AppTopBarComponent.html" data-type="entity-link" >AppTopBarComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AuthCallbackComponent.html" data-type="entity-link" >AuthCallbackComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AuthLayoutComponent.html" data-type="entity-link" >AuthLayoutComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/BoxPlotComponent.html" data-type="entity-link" >BoxPlotComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CancerIconComponent.html" data-type="entity-link" >CancerIconComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseImporterBundleViewerComponent.html" data-type="entity-link" >CaseImporterBundleViewerComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseImporterComponent.html" data-type="entity-link" >CaseImporterComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseManagerComponent.html" data-type="entity-link" >CaseManagerComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseManagerDrawerComponent.html" data-type="entity-link" >CaseManagerDrawerComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseManagerPanelComponent.html" data-type="entity-link" >CaseManagerPanelComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseManagerPanelTimelineComponent.html" data-type="entity-link" >CaseManagerPanelTimelineComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseSearchComponent.html" data-type="entity-link" >CaseSearchComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CaseSearchItemCardComponent.html" data-type="entity-link" >CaseSearchItemCardComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CodedConceptTreeComponent.html" data-type="entity-link" >CodedConceptTreeComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortBuilderComponent.html" data-type="entity-link" >CohortBuilderComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortContributorsComponent.html" data-type="entity-link" >CohortContributorsComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortFormComponent.html" data-type="entity-link" >CohortFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortGraphsComponent.html" data-type="entity-link" >CohortGraphsComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortGraphsContextMenu.html" data-type="entity-link" >CohortGraphsContextMenu</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortQueryBuilderComponent.html" data-type="entity-link" >CohortQueryBuilderComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortSearchComponent.html" data-type="entity-link" >CohortSearchComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortSearchItemComponent.html" data-type="entity-link" >CohortSearchItemComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/CohortTraitPanel.html" data-type="entity-link" >CohortTraitPanel</a>
                            </li>
                            <li class="link">
                                <a href="components/ComorbiditiesAssessmentFormComponent.html" data-type="entity-link" >ComorbiditiesAssessmentFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ConceptSelectorComponent.html" data-type="entity-link" >ConceptSelectorComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ConsentNoticeModalComponent.html" data-type="entity-link" >ConsentNoticeModalComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DashboardComponent.html" data-type="entity-link" >DashboardComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DataCompletionStatsComponent.html" data-type="entity-link" >DataCompletionStatsComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DatasetComposerComponent.html" data-type="entity-link" >DatasetComposerComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DataSummaryComponent.html" data-type="entity-link" >DataSummaryComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DataSummaryCounterComponent.html" data-type="entity-link" >DataSummaryCounterComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DatePickerComponent.html" data-type="entity-link" >DatePickerComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DisclaimerBannerComponent.html" data-type="entity-link" >DisclaimerBannerComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DistributionGraphComponent.html" data-type="entity-link" >DistributionGraphComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DoughnutGraphComponent.html" data-type="entity-link" >DoughnutGraphComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DrawerDataPropertiesComponent.html" data-type="entity-link" >DrawerDataPropertiesComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ErrorComponent.html" data-type="entity-link" >ErrorComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ExportConfirmDialogComponent.html" data-type="entity-link" >ExportConfirmDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/FamilyHistoryFormComponent.html" data-type="entity-link" >FamilyHistoryFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/FormControlErrorComponent.html" data-type="entity-link" >FormControlErrorComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/GenomicSignatureFormComponent.html" data-type="entity-link" >GenomicSignatureFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/GenomicVariantFormComponent.html" data-type="entity-link" >GenomicVariantFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/IdenticonComponent.html" data-type="entity-link" >IdenticonComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/KapplerMeierCurveComponent.html" data-type="entity-link" >KapplerMeierCurveComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/LifestyleFormComponent.html" data-type="entity-link" >LifestyleFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/LoginComponent.html" data-type="entity-link" >LoginComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/MeasureInputComponent.html" data-type="entity-link" >MeasureInputComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ModalFormHeaderComponent.html" data-type="entity-link" >ModalFormHeaderComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/MultiReferenceSelectComponent.html" data-type="entity-link" >MultiReferenceSelectComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/NeoplasticEntityFormComponent.html" data-type="entity-link" >NeoplasticEntityFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/NestedTableComponent.html" data-type="entity-link" >NestedTableComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/OncoplotComponent.html" data-type="entity-link" >OncoplotComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/PasswordResetFormComponent.html" data-type="entity-link" >PasswordResetFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/PatientFormComponent.html" data-type="entity-link" >PatientFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/PerformanceStatusFormComponent.html" data-type="entity-link" >PerformanceStatusFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/PopoverFilterButtonComponent.html" data-type="entity-link" >PopoverFilterButtonComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/PrimaryEntitiesTableComponent.html" data-type="entity-link" >PrimaryEntitiesTableComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ProjectFormComponent.html" data-type="entity-link" >ProjectFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ProjectManagementComponent.html" data-type="entity-link" >ProjectManagementComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ProjectSearchComponent.html" data-type="entity-link" >ProjectSearchComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ProjectSearchItemComponent.html" data-type="entity-link" >ProjectSearchItemComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ProviderSignupComponent.html" data-type="entity-link" >ProviderSignupComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/RadioSelectComponent.html" data-type="entity-link" >RadioSelectComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/RadiotherapyFormComponent.html" data-type="entity-link" >RadiotherapyFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/RandomPaperComponent.html" data-type="entity-link" >RandomPaperComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/RangeInputComponent.html" data-type="entity-link" >RangeInputComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/RiskAssessmentFormComponent.html" data-type="entity-link" >RiskAssessmentFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/SettingsDialogComponent.html" data-type="entity-link" >SettingsDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/StagingFormComponent.html" data-type="entity-link" >StagingFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/SurgeryFormComponent.html" data-type="entity-link" >SurgeryFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/SystemicTherapyFormComponent.html" data-type="entity-link" >SystemicTherapyFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/TreatmentResponseFormComponent.html" data-type="entity-link" >TreatmentResponseFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/TumorBoardFormComponent.html" data-type="entity-link" >TumorBoardFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/TumorMarkerFormComponent.html" data-type="entity-link" >TumorMarkerFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/UserBadgeComponent.html" data-type="entity-link" >UserBadgeComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/UserDetailsComponent.html" data-type="entity-link" >UserDetailsComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/UserFormComponent.html" data-type="entity-link" >UserFormComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/UserSelectorComponent.html" data-type="entity-link" >UserSelectorComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/UsersManagementCompnent.html" data-type="entity-link" >UsersManagementCompnent</a>
                            </li>
                            <li class="link">
                                <a href="components/VitalsFormComponent.html" data-type="entity-link" >VitalsFormComponent</a>
                            </li>
                        </ul>
                    </li>
                        <li class="chapter">
                            <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#directives-links"' :
                                'data-bs-target="#xs-directives-links"' }>
                                <span class="icon ion-md-code-working"></span>
                                <span>Directives</span>
                                <span class="icon ion-ios-arrow-down"></span>
                            </div>
                            <ul class="links collapse " ${ isNormalMode ? 'id="directives-links"' : 'id="xs-directives-links"' }>
                                <li class="link">
                                    <a href="directives/DateMaskDirective.html" data-type="entity-link" >DateMaskDirective</a>
                                </li>
                            </ul>
                        </li>
                        <li class="chapter">
                            <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#injectables-links"' :
                                'data-bs-target="#xs-injectables-links"' }>
                                <span class="icon ion-md-arrow-round-down"></span>
                                <span>Injectables</span>
                                <span class="icon ion-ios-arrow-down"></span>
                            </div>
                            <ul class="links collapse " ${ isNormalMode ? 'id="injectables-links"' : 'id="xs-injectables-links"' }>
                                <li class="link">
                                    <a href="injectables/AllAuthApiService.html" data-type="entity-link" >AllAuthApiService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/AppConfigService.html" data-type="entity-link" >AppConfigService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/AuthService.html" data-type="entity-link" >AuthService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/DatasetComposeService.html" data-type="entity-link" >DatasetComposeService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/DownloadService.html" data-type="entity-link" >DownloadService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/LayoutService.html" data-type="entity-link" >LayoutService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/TypeCheckService.html" data-type="entity-link" >TypeCheckService</a>
                                </li>
                            </ul>
                        </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#interceptors-links"' :
                            'data-bs-target="#xs-interceptors-links"' }>
                            <span class="icon ion-ios-swap"></span>
                            <span>Interceptors</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="interceptors-links"' : 'id="xs-interceptors-links"' }>
                            <li class="link">
                                <a href="interceptors/APIAuthInterceptor.html" data-type="entity-link" >APIAuthInterceptor</a>
                            </li>
                            <li class="link">
                                <a href="interceptors/UnauthorizedInterceptor.html" data-type="entity-link" >UnauthorizedInterceptor</a>
                            </li>
                        </ul>
                    </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#guards-links"' :
                            'data-bs-target="#xs-guards-links"' }>
                            <span class="icon ion-ios-lock"></span>
                            <span>Guards</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="guards-links"' : 'id="xs-guards-links"' }>
                            <li class="link">
                                <a href="guards/AuthGuard.html" data-type="entity-link" >AuthGuard</a>
                            </li>
                            <li class="link">
                                <a href="guards/CaseResolver.html" data-type="entity-link" >CaseResolver</a>
                            </li>
                        </ul>
                    </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#interfaces-links"' :
                            'data-bs-target="#xs-interfaces-links"' }>
                            <span class="icon ion-md-information-circle-outline"></span>
                            <span>Interfaces</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? ' id="interfaces-links"' : 'id="xs-interfaces-links"' }>
                            <li class="link">
                                <a href="interfaces/AccountConfiguration.html" data-type="entity-link" >AccountConfiguration</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/AllAuthConfiguration.html" data-type="entity-link" >AllAuthConfiguration</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/AllAuthResponse.html" data-type="entity-link" >AllAuthResponse</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/AppConfig.html" data-type="entity-link" >AppConfig</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/AuthenticationMeta.html" data-type="entity-link" >AuthenticationMeta</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/DataService.html" data-type="entity-link" >DataService</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Entity.html" data-type="entity-link" >Entity</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/EntityMap.html" data-type="entity-link" >EntityMap</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Field.html" data-type="entity-link" >Field</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/FieldMap.html" data-type="entity-link" >FieldMap</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/InputContext.html" data-type="entity-link" >InputContext</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/MeasureUnit.html" data-type="entity-link" >MeasureUnit</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/MFAConfiguration.html" data-type="entity-link" >MFAConfiguration</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/OpenIDCredentials.html" data-type="entity-link" >OpenIDCredentials</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Option.html" data-type="entity-link" >Option</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/ProjectMember.html" data-type="entity-link" >ProjectMember</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/ProviderConfig.html" data-type="entity-link" >ProviderConfig</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/QueryBuilderConfig.html" data-type="entity-link" >QueryBuilderConfig</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/RadioChoice.html" data-type="entity-link" >RadioChoice</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/RadioChoice-1.html" data-type="entity-link" >RadioChoice</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Reference.html" data-type="entity-link" >Reference</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Resource.html" data-type="entity-link" >Resource</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/ResourceCreate.html" data-type="entity-link" >ResourceCreate</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Rule.html" data-type="entity-link" >Rule</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/RuleFilter.html" data-type="entity-link" >RuleFilter</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/RuleSet.html" data-type="entity-link" >RuleSet</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/SocialAccountConfiguration.html" data-type="entity-link" >SocialAccountConfiguration</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/UserSessionsConfiguration.html" data-type="entity-link" >UserSessionsConfiguration</a>
                            </li>
                        </ul>
                    </li>
                        <li class="chapter">
                            <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#pipes-links"' :
                                'data-bs-target="#xs-pipes-links"' }>
                                <span class="icon ion-md-add"></span>
                                <span>Pipes</span>
                                <span class="icon ion-ios-arrow-down"></span>
                            </div>
                            <ul class="links collapse " ${ isNormalMode ? 'id="pipes-links"' : 'id="xs-pipes-links"' }>
                                <li class="link">
                                    <a href="pipes/CamelCaseToTitleCasePipe.html" data-type="entity-link" >CamelCaseToTitleCasePipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/getEventGradesPipe.html" data-type="entity-link" >getEventGradesPipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/GetFullNamePipe.html" data-type="entity-link" >GetFullNamePipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/GetNameAcronymPipe.html" data-type="entity-link" >GetNameAcronymPipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/IsStringPipe.html" data-type="entity-link" >IsStringPipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/MapOperatorsPipe.html" data-type="entity-link" >MapOperatorsPipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/ReplacePipe.html" data-type="entity-link" >ReplacePipe</a>
                                </li>
                                <li class="link">
                                    <a href="pipes/ResolveResourcePipe.html" data-type="entity-link" >ResolveResourcePipe</a>
                                </li>
                            </ul>
                        </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#miscellaneous-links"'
                            : 'data-bs-target="#xs-miscellaneous-links"' }>
                            <span class="icon ion-ios-cube"></span>
                            <span>Miscellaneous</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="miscellaneous-links"' : 'id="xs-miscellaneous-links"' }>
                            <li class="link">
                                <a href="miscellaneous/functions.html" data-type="entity-link">Functions</a>
                            </li>
                            <li class="link">
                                <a href="miscellaneous/typealiases.html" data-type="entity-link">Type aliases</a>
                            </li>
                            <li class="link">
                                <a href="miscellaneous/variables.html" data-type="entity-link">Variables</a>
                            </li>
                        </ul>
                    </li>
                    <li class="chapter">
                        <a data-type="chapter-link" href="coverage.html"><span class="icon ion-ios-stats"></span>Documentation coverage</a>
                    </li>
            </ul>
        </nav>
        `);
        this.innerHTML = tp.strings;
    }
});