# 13.4 SharePoint Integration Layer & Repository Abstraction

## Core Concept
The integration layer decouples core business logic from third-party API implementation details. By introducing an abstract repository interface between the application domain and Microsoft Graph, software remains modular, testable without live credentials, and resilient against API or schema changes.

## Key Tools and Design Patterns
- **Abstract Base Class (`abc.ABC`)**: Declares the formal persistence contract (`get_item`, `save_item`, `store_document`) independent of underlying storage technology.
- **Repository Pattern**: Mediates between the domain logic and data mapping layers, presenting a collection-like interface for domain entities.
- **Dependency Inversion Principle (DIP)**: High-level modules (business services) depend on abstractions (interfaces), not on low-level modules (HTTP client libraries).
- **Dependency Injection**: Supplying the concrete repository implementation to the service constructor at runtime.

## Practical Theory: Why Business Logic Must Never Call APIs Directly
When business validation, calculation rules, and data flows are directly interleaved with `requests.get()` or Microsoft Graph endpoints, the entire codebase becomes brittle. Unit testing requires mocking sprawling HTTP payloads, and changing a column name or migrating from SharePoint to PostgreSQL requires rewriting domain logic. Abstracting operations behind a repository interface isolates SharePoint as a swappable infrastructure detail.

## Connection to What Was Built
This folder contains `sharepoint_repository_interface.py` (contract), `sharepoint_repository.py` (concrete implementation using the list and document clients), and `service.py` (`AssetService`, which depends solely on the ABC). `test_integration_layer.py` proves that business rules can be verified purely against a mock repository with zero Graph API calls.
