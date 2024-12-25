# Data Pipeline for Qualys and Crowdstrike Hosts

### Requirements
1. Python 3.10+
2. MongoDB installed locally or remotely.

### Setup Instructions
1. Clone this repository.
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Configure .env with:
- QUALYS_API_TOKEN
- CROWDSTRIKE_API_TOKEN
- MONGO_URI
4. Run the pipeline:
    If you are using poetry
    `poetry run python -m src.main`

5. Visualizations will appear for:
- Host distribution by OS.
- Old vs new hosts.