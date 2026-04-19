# White Box Test Case Report

## Project
Trip Planner

## Scope
This report contains only three white-box test cases (TC01-TC03).

## Test Cases

| Test Case ID | Internal Logic Covered | Input | Expected Output |
|---|---|---|---|
| TC01 | JSON parsing path in `_extract_json` | Valid JSON string with required keys | Parsed dictionary returned successfully |
| TC02 | Main generation success flow in `generate_travel_plan` with mocked Gemini client | Valid destination, month, duration, budget, food preference | `agent_one`, `agent_two`, and `itinerary` objects returned with expected structure |
| TC03 | Error branch when Gemini client is unavailable in `generate_travel_plan` | `_get_gemini_client` returns `None` | `ValueError` is raised |

## Notes
- Testing type: White-box (internal logic, branch behavior, and function-level paths).
- These cases map directly to unit tests in [tests/unit/test_travel_agents.py](tests/unit/test_travel_agents.py).
