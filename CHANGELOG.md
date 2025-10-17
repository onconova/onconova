# Changelog

All notable changes to this project will be documented here.

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

