# Rules Extractor Component Changelog

All notable changes to the Rules Extractor component will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of the Rules Extractor component
- Core functionality for extracting business rules from legacy code
- Integration with OpenRouter LLM API
- Support for RPGLE code analysis
- Pydantic models for business rules
- Prompt templates and example-based extraction
- Debug mode and detailed logging
- Command-line interface for file processing

### Changed
- Moved component from /src directory to root level
- Updated import paths to reflect new structure
- Enhanced error handling and logging

### Technical Debt
- Need to implement proper test coverage
- Documentation needs to be expanded
- Example collection needs to be enriched 