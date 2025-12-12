# Changelog

All notable changes to this project will be documented here.

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

