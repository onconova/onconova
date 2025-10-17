# Changelog

All notable changes to this project will be documented here.

-----------------

## 1.1.0 - 2025-10-09

### Added 

- Add a FHIR Implementation Guide for Onconova's FHIR Interface (provisional) by @luisfabib in https://github.com/onconova/onconova/pull/142

### Fixed

- Freeze the `compodoc` version to avoid error during build in workflow
- Freeze `pydantic` and `django-ninja` dependencies of the server to avoid bugs caused by newer release combinations
- Refactor annotation check to use inspect.isclass in dataset.py to avoid error in server. 

**Full Changelog**: https://github.com/onconova/onconova/compare/1.0.0...1.0.1

-----------------

## 1.0.0 - 2025-09-03

🎉 First release!

