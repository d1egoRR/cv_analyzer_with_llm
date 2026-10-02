# AGENTS.md

## Project Overview

CV Analyzer is a software project developed in Python using FastAPI.

The project follows Hexagonal Architecture (Ports and Adapters) and prioritizes modularity, maintainability, testability, and simplicity.

The application requirements and features will evolve over time. Always follow the latest approved specifications and explicit user instructions.

## Core Principles

- Follow Python best practices and PEP 8.
- Apply Hexagonal Architecture.
- Prioritize simplicity and maintainability.
- Keep components modular and loosely coupled.
- Apply separation of concerns.
- Avoid overengineering and premature optimization.
- Use dependency injection where appropriate.
- Minimize external dependencies.
- Design for testability.
- Implement only what is explicitly requested.

## Language

- Use English exclusively for source code, identifiers, comments, technical documentation, and project structure.
- Use descriptive and consistent naming conventions.
- Follow Python naming conventions.
- Keep technical documentation clear and concise.

## Technology Stack

- Language: Python.
- API Framework: FastAPI.
- Data Validation: Pydantic.
- ASGI Server: Uvicorn.
- Containerization: Docker.
- Local Orchestration: Docker Compose.
- Testing: pytest.

Prefer standard library functionality whenever it is sufficient.

Avoid unnecessary third-party dependencies.

## Architecture

Use Hexagonal Architecture (Ports and Adapters).

Organize the application around the following responsibilities:

### Domain

- Contains core business models and domain rules.
- Must remain independent of infrastructure and delivery mechanisms.
- Must not depend on FastAPI, Pydantic, or external frameworks.
- Should not contain unnecessary abstractions.

### Application

- Contains application use cases and orchestration logic.
- Coordinates domain behavior.
- Defines ports when external dependencies or architectural boundaries require them.
- Must remain independent of delivery and infrastructure implementations.

### Adapters

- Implement communication with external systems.
- Include inbound adapters such as HTTP endpoints.
- Include outbound adapters such as external API clients, database repositories, or other infrastructure integrations when required.
- Translate external data into application-level representations.

### Dependency Rules

- Dependencies must point inward.
- Domain must not depend on application, adapters, or infrastructure.
- Application must not depend on concrete adapter implementations.
- Keep dependencies explicit.
- Avoid circular dependencies.
- Introduce interfaces or protocols only when they serve a clear architectural purpose.

Do not create empty packages, unnecessary layers, or abstractions without a concrete use case.

## Project Structure

- Keep the project structure aligned with its architectural responsibilities.
- Use a clear application entry point.
- Organize packages by responsibility rather than creating excessive nested directories.
- Keep related functionality together.
- Reevaluate the structure as the project evolves.
- Avoid moving or renaming modules without a clear benefit.

## Python Coding Standards

- Follow PEP 8.
- Use type hints consistently.
- Prefer explicit and readable code.
- Use Python 3.12+ unless the project specifies another version.
- Handle exceptions explicitly.
- Avoid broad exception handling unless justified.
- Use asynchronous programming when it provides a clear benefit.
- Avoid unnecessary global mutable state.
- Keep functions and classes focused.
- Use dataclasses or appropriate domain objects where useful.
- Avoid unnecessary inheritance.
- Document public interfaces when appropriate.

## API Development

When developing HTTP APIs:

- Follow REST conventions.
- Use appropriate HTTP methods and status codes.
- Keep FastAPI routers focused on HTTP concerns.
- Validate incoming requests using Pydantic.
- Separate transport schemas from domain models when appropriate.
- Use dependency injection to connect application services and adapters.
- Use consistent error handling.
- Avoid exposing internal implementation details.
- Support request cancellation and appropriate timeouts.
- Document API contracts using OpenAPI.
- Maintain backward compatibility unless a breaking change is explicitly requested.

## External Integrations

When integrating external services:

- Isolate external dependencies behind appropriate ports.
- Implement provider-specific behavior in outbound adapters.
- Handle timeouts, errors, and rate limits appropriately.
- Keep credentials and configuration outside source code.
- Avoid coupling business logic to specific providers.
- Make integrations testable without requiring live external services.

## Docker and Deployment

- Use Docker for application containerization.
- Prefer multi-stage builds when appropriate.
- Use minimal production images.
- Run containers as non-root users whenever possible.
- Avoid including secrets in container images.
- Use environment variables for runtime configuration when appropriate.
- Use Docker Compose for local development when needed.
- Keep development and production configurations clearly separated.
- Ensure the application shuts down gracefully.
- Keep Docker configuration simple and maintainable.

## Configuration and Security

- Keep configuration separate from business logic.
- Validate configuration at application startup.
- Never hardcode credentials, tokens, or secrets.
- Avoid logging sensitive information.
- Validate and sanitize external input where appropriate.
- Apply secure defaults.
- Consider privacy and data protection requirements when handling personal information.

## Testing

- Use pytest as the default testing framework.
- Write unit tests for domain and application logic.
- Test FastAPI endpoints independently.
- Use dependency overrides, mocks, or fakes for external dependencies when appropriate.
- Add integration tests for critical application flows.
- Cover relevant edge cases and error scenarios.
- Keep tests deterministic.
- Avoid requiring external services for ordinary unit tests.
- Ensure the complete test suite passes before considering a task complete.

## Code Quality

- Format code consistently.
- Use a Python formatter and linter when configured in the project.
- Prefer Ruff for linting and formatting when appropriate.
- Keep dependencies up to date when requested or necessary.
- Avoid unnecessary code duplication.
- Remove dead code when it is safe to do so.
- Do not introduce linting tools or quality frameworks without a clear benefit or explicit requirement.

## Documentation

- Maintain a README.md with relevant project information.
- Document setup, configuration, and execution instructions.
- Keep API documentation synchronized with the implementation.
- Document important architectural decisions when necessary.
- Update documentation when changes affect existing instructions or behavior.
- Avoid duplicating information across documentation files.

## Requirements and Specifications

- Follow the latest approved specifications and explicit user instructions.
- Treat approved specifications as the source of truth for functional requirements.
- Do not assume that previous requirements remain valid after changes.
- Do not implement features that are not requested.
- Identify ambiguities and conflicting requirements before making significant implementation decisions.
- Keep implementation aligned with the current project stage.
- Update relevant specifications when explicitly required by the development workflow.

## Development Workflow

Before implementing a task:

1. Inspect the existing project structure and relevant code.
2. Read the applicable specifications and documentation.
3. Understand the requirements and expected behavior.
4. Identify the affected architectural components.
5. Propose a simple implementation approach for substantial changes.
6. Implement only the required changes.
7. Add or update tests.
8. Run formatting, linting, and tests as appropriate.
9. Verify relevant Docker configurations when applicable.
10. Update documentation when necessary.

## Agent Behavior

- Do not introduce unrequested features.
- Do not modify unrelated files.
- Do not add dependencies without justification.
- Do not make unnecessary architectural changes.
- Do not assume future requirements.
- Do not duplicate existing functionality.
- Do not silently ignore errors or failing tests.
- Explain significant technical trade-offs when relevant.
- Ask for clarification when essential requirements are ambiguous.
- Prefer incremental and verifiable changes.
- Preserve existing working behavior unless the task explicitly requires changing it.

## Priority

When instructions conflict, apply the following order:

1. Explicit user instructions in the current task.
2. Latest approved project specifications.
3. Existing architectural decisions and project documentation.
4. This file's general development guidelines.
5. General coding conventions and best practices.

Always identify important conflicts instead of silently making assumptions.