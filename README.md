# Python REST API Integration & Reliability Monitor

A hands-on project demonstrating how a client integrates with a REST API, validates returned data, handles failures, and tests the integration automatically with GitHub Actions.

## What it demonstrates

- Calling a public REST API with Python
- Checking HTTP status codes and handling network/JSON errors
- Validating required fields in API responses
- Unit testing successful responses and failure scenarios with mocked HTTP calls
- Running tests automatically on every push and pull request
- Producing a JSON integration report in CI

The project uses the public JSONPlaceholder demo API. It does not require an API key. JSONPlaceholder is a test service, so this project is for learning and demonstration, not production use.

## Architecture

```text
Python API client
    |
    v
GET /posts/1  ---> Public REST API
    |
    v
HTTP status + JSON parsing
    |
    v
Response validation
    |
    v
Integration summary (JSON)
```

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install and run:
```bash
pip install -r requirements.txt
python -m src.api_client --post-id 1
pytest -v
python -m src.api_client --post-id 1 --report integration-report.json
```

The API client prints the returned post details. With `--report`, it also writes a small JSON summary.

## Run a local failure test

The automated tests mock API responses, so they can test error cases without relying on the internet. Tests cover a successful response, HTTP errors, invalid JSON, missing fields, and network timeouts.

```bash
pytest -v
```

## GitHub setup

1. Create a GitHub repository named `python-api-integration-monitor`.
2. Upload or push this project to the repository.
3. Open **Actions** and select the `API Integration Tests` workflow.
4. Push a small change or open a pull request to trigger it.
5. Review the test results and download the `integration-report` artifact.

## Interview explanation

> I built a Python REST API integration project that calls a public API, checks the HTTP response, validates required fields, and handles common failures such as non-success status codes, invalid JSON, and timeouts. I added automated tests for both successful and unsuccessful scenarios, then configured GitHub Actions to run the test suite on every push and pull request. This helped me practise API dependencies, error handling, test coverage, and how integration failures can affect delivery readiness.

Only claim the workflow has passed after you have run it yourself.

## Example risks and mitigations

| Risk | Delivery impact | Mitigation |
|---|---|---|
| API is unavailable | Integration cannot retrieve data | Handle timeout/errors and report a clear failure |
| API returns unexpected fields | Client cannot process the response | Validate required fields and test malformed responses |
| API changes its response format | Tests or downstream code may fail | Keep response validation and regression tests |
| External API rate limits | Requests may be delayed or rejected | Use modest request volume and document limits |

## Suggested project-management artefacts

Add these to your project notes or GitHub Issues:
- Scope: fetch one post and validate its response.
- Acceptance criteria: valid response parsed; invalid status/data handled; tests pass in CI.
- Milestones: API client; error handling; tests; CI workflow; documentation.
- Definition of done: code reviewed, tests pass, README updated.

## Next improvements

- Add retry with exponential backoff for transient failures.
- Add request/response timing metrics.
- Integrate a second API and normalise data from both sources.
- Add a small dashboard for response latency and error rate.
