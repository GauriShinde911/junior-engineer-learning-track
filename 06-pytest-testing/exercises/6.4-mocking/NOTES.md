# 6.4 Mocking

## Core Concepts
Mocking replaces slow, non-deterministic, or external dependencies (network HTTP requests, third-party services, message queues) with controllable test doubles. This guarantees fast test execution, isolates unit failures, and simulates failure conditions that are hard to reproduce live (like network timeouts or 503 errors).

## Key Pytest Features
- `mocker.patch("module.target", return_value=...)`: Pytest-mock fixture that patches an object during a single test and automatically cleans up afterwards.
- `side_effect = Exception(...)`: Configures a mock to raise an exception or cycle through multiple values when invoked.
- `mock.assert_called_once_with(...)`: Verifies that a collaborator was invoked exactly once with expected parameters.
- `mock.assert_not_called()`: Ensures safety guards prevent unwanted operations (e.g. saving invalid records).

## Testing Theory: What to Mock vs Not to Mock
- **Mock at Architectural Seams**: Mock external boundaries (HTTP clients, email servers, external payment gateways). Keep the code under test 100% real.
- **The Danger of Over-Mocking**: If you mock your internal domain entities or utility functions, your tests become tautological (testing that the mock does what you told it to do). Tests pass, but production code fails due to integration mismatches.
- **Don't Mock What You Don't Own**: When interfacing with complex third-party SDKs, wrap them in a thin internal adapter and mock your own adapter interface.

## Connection to Exercises
In `test_weather_service.py`, `requests.get` is patched to simulate JSON payloads, 404 responses, and socket timeouts without making live internet requests. In `test_repository_service.py`, `UserRepository` is mocked to isolate `UserService` business rules (duplicate email prevention, normalization) from real database engines.
