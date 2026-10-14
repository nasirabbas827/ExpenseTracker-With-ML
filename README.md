# Expense Tracker With ML

ExpenseTracker-With-ML is a personal finance application for recording income and expenses.

![Django](https://img.shields.io/badge/Django-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The data model covers `Profile`, `Category`, `Income`, `Expense`.

## Implemented workflows

The source defines these handlers:

- **User Register** — `user_register`
- **User Login** — `user_login`
- **Logout** — `logout_view`
- **Dashboard** — `dashboard`
- **Update Profile** — `update_profile`
- **Change Password** — `change_password`
- **Add Category** — `add_category`
- **View Categories** — `view_categories`
- **Edit Category** — `edit_category`
- **Delete Category** — `delete_category`
- **Add Income** — `add_income`
- **View Income** — `view_income`

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/ExpenseTracker-With-ML.git
cd ExpenseTracker-With-ML
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Django pandas plotly numpy scikit-learn python-dateutil Pillow
```

Dependency versions are not pinned in this repository.

### 3. Configure and run

Review [`myproject/settings.py`](myproject/settings.py) for database, media, and any email configuration. Use a local copy of the supplied database when available.

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/. If you need a Django administration account, run `python manage.py createsuperuser`. Application-specific user roles may be managed separately.

## Repository guide

| Path | Purpose |
| --- | --- |
| [`db.sqlite3`](db.sqlite3) | Included SQLite database |
| [`manage.py`](manage.py) | Django command-line entry point |
| [`myapp`](myapp) | Django application modules |
| [`myproject`](myproject) | Django project configuration |
| [`templates`](templates) | HTML page templates |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
