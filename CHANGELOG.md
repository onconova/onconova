# Changelog

All notable changes to this project will be documented here.

-----------------

## 1.4.0 - 2026-04-26

### Added

* Added a Terminology Browser page accessible from the sidebar to navigate all platform terminologies, search for coded concepts, and view detailed entry information ([#224](https://github.com/onconova/onconova/pull/224))
* Added a graph view to the vitals timeline showing all vital signs as stacked time-series sub-plots with equidistant date axis, reference range guides, and click-to-open data drawer per date column; defaults to graph when 3 or more entries exist, with a toggle to switch to list view ([#224](https://github.com/onconova/onconova/pull/224))
* Added a dedicated timeline entry design for lifestyle events in the case manager ([#224](https://github.com/onconova/onconova/pull/224))
* Added an edit button on the project management page ([#224](https://github.com/onconova/onconova/pull/224))
* Added structured error handling and validation feedback for case import ([#221](https://github.com/onconova/onconova/pull/221), fixes [#196](https://github.com/onconova/onconova/issues/196))
* Added tooltips to the export button in the case manager explaining why export is disabled when consent is invalid or missing ([#187](https://github.com/onconova/onconova/pull/187), closes [#180](https://github.com/onconova/onconova/issues/180))
* Added customized timeline event components for specialized case manager displays, including neoplastic entities, therapy lines, tumor markers, and multi-line entries ([#179](https://github.com/onconova/onconova/pull/179))
* Added 422 HTTP API error responses for terminology- and database-related errors ([#203](https://github.com/onconova/onconova/pull/203))
* Added a `CodedConceptDoesNotExist` exception for clearer error messages when invalid coded concepts are referenced in many-to-many relations ([#203](https://github.com/onconova/onconova/pull/203), fixes [#197](https://github.com/onconova/onconova/issues/197))
* Added versioning support to all terminology digestors, ensuring version information is propagated to generated `CodedConcept` objects for improved traceability and reproducibility ([#226](https://github.com/onconova/onconova/pull/226), fixes [#223](https://github.com/onconova/onconova/issues/223))
* Added icons to the neoplastic entity relationship selector and context-sensitive help text to form fields ([#173](https://github.com/onconova/onconova/pull/173))

### Changed

- Redesigned case manager timeline entries across all data categories (adverse events, genomic variants and signatures, performance status, systemic therapy lines, tumor markers) for improved readability ([#224](https://github.com/onconova/onconova/pull/224))
- Reorganized the case manager data drawer with a cleaner, more structured layout ([#224](https://github.com/onconova/onconova/pull/224), closes [#171](https://github.com/onconova/onconova/issues/171))
- Redesigned the project management page layout ([#224](https://github.com/onconova/onconova/pull/224))
- Improved general layout and styling across the application: sidebar menu, topbar, footer, typography, content area, and shared page header ([#224](https://github.com/onconova/onconova/pull/224))
- Upgraded `django-pghistory` from 3.5.5 to 3.9.2 and restricted audit context tracking to mutating HTTP requests only (`POST`, `PUT`, `PATCH`, `DELETE`), eliminating unnecessary database round-trips on read endpoints ([#218](https://github.com/onconova/onconova/pull/218), fixes [#209](https://github.com/onconova/onconova/issues/209))
- Upgraded `fhircraft` to v0.8.3 for improved performance and validation, and regenerated all FHIR profile models ([#214](https://github.com/onconova/onconova/pull/214))
- Improved clinical text representations for systemic therapy, radiotherapy, surgery, adverse events, and family history models ([#188](https://github.com/onconova/onconova/pull/188))
- Improved the `Surgery` model description to dynamically include body site, qualifier, and laterality, and replaced "Right and left" with "Bilateral" in `LateralityQualifier` display ([#205](https://github.com/onconova/onconova/pull/205))
- Refactored `TumorMarker` model field placement, corrected analyte result type for `Fibroblast growth factor 23`, and set `ng/ml` as the default mass concentration unit ([#178](https://github.com/onconova/onconova/pull/178))
- Optimized server Python dependencies, separated dev dependencies into a dedicated group, and added `poetry.lock` for reproducible builds ([#174](https://github.com/onconova/onconova/pull/174))
- Updated `pyjwt` dependency to include the `crypto` extra, ensuring cryptographic operations are supported ([#191](https://github.com/onconova/onconova/pull/191))
- Bumped `django` from 5.1 to 5.1.15, patching CVE-2025-64460 and CVE-2025-13372 ([#175](https://github.com/onconova/onconova/pull/175))
- Bumped `werkzeug` from 3.0.0 to 3.1.6 ([#219](https://github.com/onconova/onconova/pull/219))
- Bumped `lucide-angular` from 0.482.0 to 0.563.0 ([#165](https://github.com/onconova/onconova/pull/165))
- Bumped `chartjs-chart-matrix` from 2.1.1 to 3.0.0 ([#167](https://github.com/onconova/onconova/pull/167))

### Fixed

- Fixed bundle ID resolution during import to be order-independent, preventing failures when referenced bundles appear later in the import file ([#220](https://github.com/onconova/onconova/pull/220), fixes [#213](https://github.com/onconova/onconova/issues/213))
- Fixed therapy lines not being updated when importing a patient case bundle ([#220](https://github.com/onconova/onconova/pull/220), fixes [#211](https://github.com/onconova/onconova/issues/211))
- Fixed events of specialized polymorphic resource instances not being returned by the API ([#220](https://github.com/onconova/onconova/pull/220), fixes [#210](https://github.com/onconova/onconova/issues/210))
- Fixed elevated cohort creation so that platform and system administrators can create cohorts for any project ([#221](https://github.com/onconova/onconova/pull/221), fixes [#182](https://github.com/onconova/onconova/issues/182))
- Fixed cohort name edit submission to correctly persist name changes on confirm ([#221](https://github.com/onconova/onconova/pull/221), fixes [#183](https://github.com/onconova/onconova/issues/183))
- Fixed `externalSourceId` serialization to ensure the field is correctly delivered over the API ([#216](https://github.com/onconova/onconova/pull/216), fixes [#200](https://github.com/onconova/onconova/issues/200))
- Fixed NCIT antineoplastic expansion to more reliably include relevant drug concepts and parent categories, and corrected antineoplastic name capitalization ([#215](https://github.com/onconova/onconova/pull/215))
- Fixed period (de)serialization to ensure `DateRangeField` model fields consistently use inclusive upper bounds ([#212](https://github.com/onconova/onconova/pull/212))
- Fixed `PatientCaseBundle` validation and resolver inconsistencies that caused stagings, tumor boards, genomic signatures, history, and completion data to be incorrectly imported ([#208](https://github.com/onconova/onconova/pull/208), fixes [#207](https://github.com/onconova/onconova/issues/207))
- Fixed 422 HTTP error handling when a terminology concept is not found in a many-to-many relation ([#206](https://github.com/onconova/onconova/pull/206))
- Fixed incorrect LOINC code mappings for `Cancer Ag 125` and `Cancer Ag 15-3` tumor marker test codes in the FHIR interface ([#201](https://github.com/onconova/onconova/pull/201))
- Fixed ICD-O-3 morphology digestor to expand codes to all possible behavior qualifiers, ensuring compliance with ICD-O-3 rule F ([#199](https://github.com/onconova/onconova/pull/199), fixes [#198](https://github.com/onconova/onconova/issues/198))
- Fixed population counter remaining stuck in a loading animation when the population size is exactly zero ([#189](https://github.com/onconova/onconova/pull/189), fixes [#169](https://github.com/onconova/onconova/issues/169))
- Fixed case resources being exportable when consent is not valid ([#187](https://github.com/onconova/onconova/pull/187))
- Fixed FHIR serialization bug causing snake_case serialization of FHIR resources instead of expected camelCase ([#185](https://github.com/onconova/onconova/pull/185))
- Fixed `NeoplasticEntityForm` to exclude the current entity from selectable related primaries and to reset form state when switching relationship types ([#176](https://github.com/onconova/onconova/pull/176), fixes [#172](https://github.com/onconova/onconova/issues/172))
- Fixed documentation deployment workflows to use `git pull` instead of `git fetch`, ensuring the latest changes are incorporated before deployment ([#217](https://github.com/onconova/onconova/pull/217))
- Fixed multiple issues with GitHub CI workflows and Dependabot configuration ([#162](https://github.com/onconova/onconova/pull/162))


**Full Changelog**: https://github.com/onconova/onconova/compare/1.3.0...1.4.0

-----------------

## 1.3.0 - 2025-12-12

### Added

* Implemented a complete FHIR R4 mCODE-conform interface with `/fhir/` endpoints supporting standard healthcare resource exchange, providing ([#158](https://github.com/onconova/onconova/pull/158), closes [#73](https://github.com/onconova/onconova/pull/73))
   - Full implementation of the Onconova FHIR Implementation Guide Capabilities
   - mCODE (Minimal Common Oncology Data Elements) profile support
   - Comprehensive validation rules and conformance requirements
   - Full mapping between supported FHIR profiles and REST API schemas 
   - Closes #73 
* Added `fhircraft` as a dependency to handle the FHIR (de)serliazation, model code generation and validation ([#158](https://github.com/onconova/onconova/pull/158))
* Added a `source` field to the `GenomicVariant` ORM model to store the cytogenetic source of the variant ([#158](https://github.com/onconova/onconova/pull/158))
* Added a `hgvsVersion` to the `GenomicVariant` core schema to publically document the HGVS version used internally ([#158](https://github.com/onconova/onconova/pull/158))

### Changed

- Updated the permissions for the `update_user` API route to allow either users with `CanManageUsers` or users who are the requesting user (`IsRequestingUser`) to update user information ([#153](https://github.com/onconova/onconova/pull/153))
- Updated the public release installation steps to instruct users to download the correct `compose.yml` file and added instructions to download the `nginx.conf` reverse proxy configuration  ([#156](https://github.com/onconova/onconova/pull/156))
- Updated the `.env.sample` file to change the default Docker Compose file reference from `compose.prod.yml` to a more generic `compose.yml` for improved clarity for new users following the documentation and removed the section for documentation webserver address (`ONCONOVA_DOCS_WEBSERVER_ADDRESS`) and its related comments, since this configuration is no longer needed ([#157](https://github.com/onconova/onconova/pull/157))
- Split the tumor marker analyte `Fibroblast growth factor` into more specialized analytes `Fibroblast growth factor 2`, `Fibroblast growth factor 23` and `Fibroblast growth factor 21` ([#158](https://github.com/onconova/onconova/pull/158))
- Renamed the TNM category fields in `TNMStaging` to properly use snake-case notation ([#158](https://github.com/onconova/onconova/pull/158))


### Fixed

- Replaces the `jwt` package (version 1.3.1) with the `pyjwt` package (version 2.0), ensuring the project uses the more widely adopted and actively maintained JWT library. The previous dependency was causing errors during the single sign-on (SSO) workflows ([#152](https://github.com/onconova/onconova/pull/152))
- Fixed a bug leading to new users with base permissions not being able to submit their decision on the initial user data usage form, blocking access to the platform ([#153](https://github.com/onconova/onconova/pull/153))
- Fixed a bug when updating the access level of a user that has been provided by an SSO service ([#153](https://github.com/onconova/onconova/pull/154))
- Corrected the link for downloading the sample environment file in the installation instructions, ensuring users save `.env.sample` as `.env` instead of downloading the wrong file ([#156](https://github.com/onconova/onconova/pull/156), fixes [#155](https://github.com/onconova/onconova/pull/155))
- Added missing fields cytogeneticLocation and chromosomes to the GenomicVariant core schema ([#158](https://github.com/onconova/onconova/pull/158))
- Fixed the client reference documentation URL leading to a 404 error in the docs ([#158](https://github.com/onconova/onconova/pull/158))
- Fixed `default_factory` for `dataConstraints` in `Project` schema to avoid a `500` error when posting from the client ([#159](https://github.com/onconova/onconova/pull/159))
- Added the missing `__orm_model__` attribute to the `UserProfile` schema to avoid an error when updating user profiles over the API ([#160](https://github.com/onconova/onconova/pull/160))



**Full Changelog**: https://github.com/onconova/onconova/compare/1.2.1...1.3.0

-----------------

## 1.2.1 - 2025-10-17

### Fixed 

- Fix the documentation deployment workflow for releases. 

**Full Changelog**: https://github.com/onconova/onconova/compare/1.2.0...1.2.1

-----------------

## 1.2.0 - 2025-10-17

### Changed 

- Migrated the source code to https://github.com/onconova/onconova.
- The Onconova FHIR IG source code has been migrated to a separate repo (https://github.com/onconova/fhir) for better maintainability.
- Replace dynamically-generated schemas by static definitions ([#148](https://github.com/onconova/onconova/pull/148)). This will ensure that current and future API versions can be correctly frozen and maintained.
- Refactor code to new organization multi-repo strcuture ([#149](https://github.com/onconova/onconova/pull/149))

**Full Changelog**: https://github.com/onconova/onconova/compare/1.0.0...1.2.0

-----------------

## 1.1.0 - 2025-10-09

### Added 

- Add a FHIR Implementation Guide for Onconova's FHIR Interface (provisional) by @luisfabib in https://github.com/onconova/onconova/pull/142

### Fixed

- Freeze the `compodoc` version to avoid error during build in workflow
- Freeze `pydantic` and `django-ninja` dependencies of the server to avoid bugs caused by newer release combinations
- Refactor annotation check to use inspect.isclass in dataset.py to avoid error in server. 

**Full Changelog**: https://github.com/onconova/onconova/compare/1.0.1...1.1.0

-----------------

## 1.0.0 - 2025-09-03

🎉 First release!

