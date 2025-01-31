from prefect import flow, task
from datetime import timedelta
from raglight.scrapper.github_scrapper import GithubScrapper
from raglight.rag.builder import Builder
from raglight.config.settings import Settings
import shutil
import logging

persist_directory = "./chroma_db"
collection_name = "github_repos"
repos = ["https://github.com/Bessouat40/RAGLight", "https://github.com/Bessouat40/LLMChat"]

Settings.setup_logging()

vector_store = (
        Builder()
        .with_embeddings(Settings.HUGGINGFACE, model_name=Settings.DEFAULT_EMBEDDINGS_MODEL)
        .with_vector_store(
            Settings.CHROMA,
            persist_directory=persist_directory,
            collection_name=collection_name,
        )
        .build_vector_store()
    )

github_scrapper = GithubScrapper()

@task(log_prints=True)
def fetch_repos(repos: list[str]) -> str:
    github_scrapper.set_repositories(repos)
    repos_path = github_scrapper.clone_all()
    return repos_path

@task(log_prints=True)
def ingest_to_vector_store(repos_path: str):
    vector_store.ingest_code(repos_path=repos_path)

@flow(name="Update GitHub Vector Store", log_prints=True)
def update_vector_store(repos: list[str], persist_directory: str, collection_name: str):
    repos_path = fetch_repos(repos)
    ingest_to_vector_store(repos_path)
    logging.info("✅ GitHub repositories successfully indexed!")
    shutil.rmtree(repos_path)
    logging.info("✅ GitHub repositories cleaned successfully!")


if __name__ == "__main__":
    update_vector_store.serve(
        name="github-vector-store-scheduler",
        cron="0 0 * * *", # Run daily at midnight
        parameters={
            "repos": repos,
            "persist_directory": persist_directory,
            "collection_name": collection_name,
        },
    )
