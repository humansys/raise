---
type: architecture_context
project: "{project_name}"
status: draft
tech_stack:
  # key-value pairs: technology category -> specific tool/framework
  # Examples:
  #   language: Python 3.13
  #   framework: FastAPI
  #   database: PostgreSQL 16
  {}
external_dependencies:
  # List of external system names this project depends on.
  # Examples:
  #   - Jira Cloud API
  #   - AWS S3
  []
users:
  # List of user/actor types that interact with the system.
  # Examples:
  #   - developer
  #   - ci-pipeline
  []
governed_by: []
---

# System Context: {project_name}

> C4 Level 1 — System Context diagram and description
> Fill with /rai-project-create or /rai-project-onboard

## Overview

<!-- High-level description: what is this system and who uses it? -->

## Context Diagram

<!-- System context showing external actors and systems -->

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│  Users   │──────►│  {project_name}  │◄──────│ External │
│          │       │              │       │ Systems  │
└──────────┘       └──────────────┘       └──────────┘
```

## External Interfaces

| System | Direction | Protocol | Description |
|--------|-----------|----------|-------------|
