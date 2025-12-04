# Carbon Loan Tracker (CLT)

A full-stack Django web application for tracking citizen carbon emissions, calculating tree offset requirements, and managing the planting verification workflow.

## Features

- **User Roles**: Citizen, Planting Agent, Admin.
- **Carbon Ledger**: Tracks annual CO2 emissions and debt status.
- **Calculator**: Converts consumption (km, kWh) to CO2 tonnes and required trees.
- **Tree Transactions**: "Purchase" trees to offset debt.
- **Verification System**: Agents upload photo proof of planting; Admins approve.
- **Dashboards**: Role-specific dashboards with stats and charts.
- **API**: Full REST API with OpenAPI documentation.

## Tech Stack

- Django 4.2+
- Django REST Framework
- TailwindCSS (via CDN)
- SQLite
- Pytest

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone/Navigate to the project folder**:
   ```bash
   cd carbon_loan_tracker
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local dev)
   ```

5. **Database Setup**:
   ```bash
   python manage.py migrate
   ```

6. **Load Sample Data**:
   ```bash
   python manage.py load_sample_data
   ```
   This creates:
   - Superuser: `admin` / `admin123`
   - Agents: `agent1` / `password123`, etc.
   - Citizens: `citizen1` / `password123`, etc.
   - Sample ledgers and transactions.

7. **Run Server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the App**:
   - Web App: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - API Docs: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
   - Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Testing

Run the test suite:
```bash
pytest
```
