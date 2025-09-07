# MMX Engineering Spec Manager (Work in Progress)

This repository contains an early, actively evolving prototype of a desktop application for managing engineering specifications. The goal is to import project information from Innergy, adapt and enrich it within a local data model, and export data in formats suitable for Microvellum and related workflows.

Important: This is an incomplete work in progress. Interfaces, data models, and features are subject to change without notice. Expect rough edges, missing features, and occasional breaking changes while the project is under active development.


## Highlights (Current State)
- Desktop GUI built with PySide6 (Qt for Python).
- Data persistence using SQLAlchemy with a default SQLite database file stored in the OS application data directory.
- Pluggable import pipeline with an Innergy importer (prototype stage).
- Early exporters and mappers to move towards Microvellum-compatible outputs.
- Example datasets and workbooks in the repository for experiments.
- A growing test suite using pytest and pytest-qt.


## Roadmap (Subject to Change)
- Stabilize core data models and migrations.
- Expand importers (Innergy and others) and improve resilience and progress reporting.
- Solidify exporters for Microvellum (XML/XLSX) and add validation.
- Enhance the GUI for project browsing, editing, and export workflows.
- Configuration UI and richer settings persistence.
- Packaging and distribution for Windows/macOS/Linux.


## Repository Structure (Overview)
- main.py — Entry point to launch the GUI application.
- mmx_engineering_spec_manager/
  - controllers/ — Qt controller layer, e.g., MainWindowController.
  - data_manager/ — DataManager orchestrates database access, import sync, and project lifecycle.
  - db_models/ — SQLAlchemy ORM models (Project, Product, SpecificationGroup, Prompts, etc.).
  - dtos/, mappers/, repositories/ — Data transfer, mapping, and persistence helpers.
  - exporters/, importers/ — IO integrations (e.g., Innergy importer; Microvellum exporters WIP).
  - services/ — Business logic services.
  - utilities/ — Settings, logging, persistence helpers, and lightweight migrations.
  - views/ — Qt widgets, dialogs, and UI components.
- example_data/ — Sample inputs (innergy/json, microvellum/xml, etc.).
- example_workbooks/ — Example spreadsheets for experimentation.
- tests/ — pytest test suite, organized by feature area.

Note: Folder content is evolving; not all modules are complete.


## Requirements
- Python 3.10+ recommended.
- OS with GUI support (Qt/PySide6). Headless usage is not currently supported.

Python dependencies are listed in requirements.txt, including:
- PySide6 — UI toolkit
- SQLAlchemy — ORM and database engine
- python-dotenv — Environment configuration
- requests — HTTP client (for importers)
- pytest, pytest-qt, pytest-cov, pytest-mock — Testing stack


## Installation and Setup
1. Clone the repository:
   git clone https://github.com/your-org/mmx-engineering-spec-manager.git
   cd mmx-engineering-spec-manager

2. Create and activate a virtual environment (example using venv):
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment (optional but recommended):
   Create a .env file in the repository root to override defaults:
   # Innergy importer configuration
   INNERGY_API_KEY=your_api_key_here
   INNERGY_BASE_URL=https://app.innergy.com

   # Database configuration (default is a SQLite file under the OS app data directory)
   # Examples:
   # DATABASE_URL=sqlite:///absolute/path/to/projects.db
   # DATABASE_URL=sqlite:///:memory:
   # DATABASE_URL=postgresql://user:password@host:5432/dbname

   # Export templates (optional, for exporters still in progress)
   # MICROVELLUM_XML_TEMPLATE_PATH=/path/to/template.xml
   # XLSX_TEMPLATE_PATH=/path/to/template.xlsx

The application determines the writable application data directory using Qt's QStandardPaths. A default SQLite database (projects.db) will be created there if DATABASE_URL is not set.


## Running the Application
From the repository root with the virtual environment activated:
   python -m mmx_engineering_spec_manager  # if packaged as module (future)
   # or, for the current layout:
   python main.py

On first launch, the DataManager will initialize the database schema. Lightweight, idempotent migrations for specific tables may run automatically for SQLite.


## Working with Data
- Imports: A prototype InnergyImporter exists. Depending on your configuration and test data, you may use example_data/innergy for local trials.
- Models: Key entities include Project, Product, SpecificationGroup, and various Prompt/Callout models. Relationships are defined using SQLAlchemy relationships.
- Settings: The utilities/settings.py module aggregates environment variables into a Settings object used across the app.
- Persistence: The utilities/persistence.py module constructs the SQLAlchemy engine based on DATABASE_URL (or a default SQLite path) and binds a sessionmaker.


## Testing
Run tests from the repository root:
   pytest

Generate a coverage report:
   pytest --cov=mmx_engineering_spec_manager --cov-report=term-missing

Note: Some GUI tests (pytest-qt) may require a display environment. Use a suitable CI configuration or a virtual display server as needed.


## Example Data
The example_data directory includes sample inputs for importers (and exporter prototypes). These are for experimentation only and do not represent production-ready data.


## Contributing
Contributions are welcome, but please note the project’s active and fast-moving status.
- Open an issue to propose changes or report bugs.
- For PRs, aim for minimal, self-contained changes with tests where possible.
- Follow the existing code style and structure; keep modules cohesive.


## Project Status and Disclaimer
This software is provided as-is, without any guarantees. It is pre-alpha and incomplete. APIs, file formats, and user interfaces may change at any time. Use at your own risk and avoid using it for production work until a stable release is announced.


## License
This project is licensed under the terms of the LICENSE file in the repository root.


## Acknowledgements
- Qt for Python (PySide6)
- SQLAlchemy
- pytest and related plugins

If you have questions or need help with setup, please open an issue with details about your OS, Python version, and any error messages you encounter.
