# Green-Tech Inventory Assistant

This repository contains a lightweight Python prototype of the Green-Tech
Inventory Assistant described in the instructions. It tracks items with
expiration dates, logs consumption, forecasts future needs using a stubbed AI
service with a manual fallback, and records customer attendance to help plan
orders.

---

**Candidate Name:**

**Scenario Chosen:** Inventory assistant with AI forecasting and attendance
analysis

**Estimated Time Spent:** ~4 hours

---

## Quick Start

### Prerequisites:

- Python 3.11 (venv created automatically by the provided configuration)

### Setup & Run Commands:

```powershell
cd c:\Users\alanz\Desktop\side-projects\palo-alto-build
python -m venv .venv          # if not already created
.\.venv\Scripts\activate
pip install -U pip
# there are no external dependencies
```

Run the CLI:

```powershell
python main.py add mango 20 --expires 2026-05-01
python main.py list --filter man
python main.py consume mango 3
python main.py forecast mango --days 7
python main.py attendance 12
python main.py plan
```

### Test Commands:

```powershell
python -m unittest discover -v
```

---

## AI Disclosure

- **Did you use an AI assistant?** Yes (GitHub Copilot + ChatGPT helped draft
  code and tests).
- **How did you verify the suggestions?** Run unit tests, manual inspection, and
  by reasoning through the logic.
- **Example rejected suggestion:** Copilot suggested storing history in a CSV
  file; I opted for an in-memory list for simplicity and testability.

---

## Tradeoffs & Prioritization

- Cut features: no persistent database, web UI, or real AI integration due to
  time constraints.
- Next steps: add a simple storage layer (JSON/SQLite), improve AI hook, and
  build a lightweight web/dashboard interface.
- Known limitations: all state is lost on restart; AI prediction is simulated
  and non-deterministic; CLI does not support deleting attendance records.
