# Reconcile AI

A reconciliation and approval automation platform that combines a Python backend with a Next.js frontend to manage exceptions, approvals, and consequential actions in a streamlined workflow.

## Overview

This project is designed to help teams review and resolve reconciliation mismatches efficiently. It provides:
- backend APIs for reconciliation workflows
- AI-assisted investigation and action planning
- approval-based execution flows
- dashboard and activity tracking
- frontend views for approvals, exceptions, and activity monitoring

## Architecture

This repository is split into two main branches:

- `backend`: contains the Python/FastAPI backend application
- `frontend`: contains the Next.js frontend application
- `main`: project-level setup and shared repo metadata

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL / relational database support
- AI-powered workflow orchestration

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- Shadcn UI components

## Project Structure

```text
reconcile_ai/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   ├── cleanup_duplicate_approval.py
│   ├── reset_demo.py
│   ├── seed_reconciliation_data.py
│   └── seed_test.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
├── docker-compose.yml
├── .gitignore
└── README.md


```
Features
Reconciliation case tracking
Exception and approval workflows
AI-driven action suggestions
Review and execution history
Case investigation tools
Dashboard visibility for operational teams

Backend Setup
Open the backend folder.
**Create a virtual environment:
    python -m venv .venv
    source .venv/bin/activate
**Install dependencies
    pip install -r requirements.txt

**Run the backend:
   uvicorn app.main:app --reload

Frontend Setup
Open the frontend folder.
Install dependencies:
  npm install

**Run the development server
  npm run dev
   
  



