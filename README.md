# prefect-github-indexer

A Prefect pipeline that periodically scrapes a GitHub repository, generates embeddings, and indexes them in ChromaDB. Avoids duplicates by checking file hashes. Perfect for building a searchable vector database from code.

## Installation

```bash
python -m pip install -U prefect
```

## Run flow

```bash
python src/github_scrapper.py
```

## Run prefect server

```bash
python -m prefect server start
```
