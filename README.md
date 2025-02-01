# Prefect GitHub Indexer

A Prefect pipeline that periodically scrapes one or more GitHub repositories, generates embeddings, and indexes them in ChromaDB.

## What is Prefect?

Prefect is a modern workflow orchestration platform that helps you:

- Write data workflows in Python using a straightforward, decorator-based API.
- Schedule your workflows (flows) to run at specific times or intervals (daily, weekly, etc.).
- Monitor flow executions in a web-based UI, with clear logs and task statuses.
- Handle retries, concurrency limits, configuration of infrastructure (Docker, Kubernetes, etc.), and more.

In this project, Prefect orchestrates:

- Scraping GitHub repositories.
- Generating embeddings for code files.
- Indexing these embeddings into ChromaDB.
- Scheduling daily or periodic runs to keep your embeddings up-to-date.

## Architecture Overview

This repository’s main flow is defined in flows/github-scrapper.py. Here’s how it all fits together:

1. Flow: update_vector_store
   The top-level orchestration function that processes multiple GitHub repos in parallel.
2. Tasks: fetch_repo, ingest_repo_to_vector_store
   Smaller, reusable steps that do the actual work (cloning a repo, ingesting into ChromaDB, etc.).
3. Subflow: process_repo
   Called for each repo. Manages the end-to-end flow of cloning, indexing, and cleanup for that repository.
4. Scheduling: The flow can be scheduled to run at midnight every day (cron="0 0 \* \* \*").
   Prefect’s server and agent allow you to:

Server (UI & API): See your flow runs, logs, and manage deployments from a nice dashboard.
Agent (Worker): Listens for scheduled or triggered flow runs and executes them (in Docker containers or other infrastructure).

## Installation

1. Clone this repository.
2. Install Prefect and any additional dependencies:

```bash
python -m pip install -U prefect
```

## Running Locally

You can test the flow directly by running :

```bash
python flows/github-scrapper.py
```

By default, every day at midnight this will:

- Clone the specified repositories.
- Ingest them into ChromaDB (in the local chroma_db folder).
- Print logs about each step.

## Prefect Server

Prefect comes with a built-in API and UI (sometimes referred to as [Orion UI] in older docs). You can start it locally by running :

```bash
python -m prefect server start
```

Then open [localhost:4200](http://localhost:4200/dashboard) in your browser. You’ll see:

- A dashboard with Deployments (flows you’ve registered),
- Flow Runs (individual executions of flows),
- Logs for debugging, etc.

Registering your flow with the server allows you to schedule it from the UI, monitor runs, and scale out using agents on other machines or Docker containers.

## Docker Deployment

For a more production-like setup, you can run everything via Docker Compose. This will spin up:

- prefect-server (UI + API),
- prefect-agent (the worker that executes flows),
- A Docker volume for ChromaDB data (chroma_db).

### Build and run

```bash
docker-compose up -d --build
```

Once the server is up, visit [localhost:4200](http://localhost:4200/dashboard).
