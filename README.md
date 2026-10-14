# Clothes Management Tayyab

Clothes-management-tayyab is a desktop application for clothing inventory, purchases, and sales.

![Tkinter](https://img.shields.io/badge/Tkinter-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The Tkinter implementation is organized around the entry points and modules below.

## Modules

- [`add_categories.py`](add_categories.py) — Add Categories
- [`add_items.py`](add_items.py) — Add Items
- [`add_purchase.py`](add_purchase.py) — Add Purchase
- [`add_sale.py`](add_sale.py) — Add Sale
- [`add_users.py`](add_users.py) — Add Users
- [`admin_dashboard.py`](admin_dashboard.py) — Admin Dashboard
- [`database.py`](database.py) — Database
- [`generate_reports.py`](generate_reports.py) — Generate Reports
- [`main.py`](main.py) — Main
- [`user_dashboard.py`](user_dashboard.py) — User Dashboard

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/Clothes-management-tayyab.git
cd Clothes-management-tayyab
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install tkcalendar reportlab Pillow
```

Dependency versions are not pinned in this repository.

A working Tkinter installation and a graphical desktop session are required.

### 3. Configure and run

Keep the included SQLite database files in their expected locations: [`clothes.db`](clothes.db).

Run from the repository root so relative file paths resolve correctly:

```bash
python main.py
```

## Repository guide

| Path | Purpose |
| --- | --- |
| [`main.py`](main.py) | Application entry point |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
