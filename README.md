# Green-Tech Inventory Assistant

**Candidate Name:** Alan Zhang

**Scenario Chosen:** Green-Tech Inventory Assistant

**Estimated Time Spent:** 6 hours

**Youtube Link:** https://www.youtube.com/watch?v=OOkaXQAWccE

---

## Quick Start

### Prerequisites:

- Python 3.11 (venv created automatically by the provided configuration)

### Setup & Run Commands:

```powershell
python -m venv .venv # if not already created
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

Run the Web App:

```powershell
flask run
```

### Test Commands:

```powershell
python -m unittest discover -v
```

---

## AI Disclosure

- **Did you use an AI assistant?** Yes (GitHub Copilot helped draft code and tests).
- **How did you verify the suggestions?** Run unit tests, manual inspection, and
  by reasoning through the logic.
- **Example rejected suggestion:** Copilot suggested storing history in a CSV
  file; I opted for an in-memory list for simplicity and testability.

---

## Tradeoffs & Prioritization

- Cut features: no persistent database, web UI, or advanced AI integrations due to time constraints.
- Next steps: add a simple storage layer (JSON/SQLite), improve AI hook, and build a lightweight web/dashboard interface.
- Known limitations: all state is lost on restart; AI prediction is simulated and non-deterministic; CLI does not support deleting attendance records.
