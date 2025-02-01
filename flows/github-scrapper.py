from prefect import flow, task
from raglight.scrapper.github_scrapper import GithubScrapper
from raglight.rag.builder import Builder
from raglight.config.settings import Settings
import shutil
import logging

persist_directory = "./chroma_db"
collection_name = "github_repos"
repos = [
    "https://github.com/Bessouat40/RAGLight",
    "https://github.com/Bessouat40/LLMChat"
]

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

@task(log_prints=True, retries=3, retry_delay_seconds=10)
def fetch_repo(repo: str) -> str:
    """Clone a GitHub repository and return the local path."""
    logging.info(f"Cloning repository: {repo}")
    github_scrapper.set_repositories([repo])
    repo_path = github_scrapper.clone_all()
    return repo_path

@task(log_prints=True, retries=3, retry_delay_seconds=10)
def ingest_repo_to_vector_store(repo_path: str):
    """Ingest the cloned repository code into the vector store."""
    logging.info(f"Ingesting code from: {repo_path}")
    vector_store.ingest_code(repos_path=repo_path)
    logging.info(f"Ingestion complete for: {repo_path}")

@flow(name="Process Single Repository", log_prints=True)
def process_repo(repo: str) -> None:
    """
    Subflow that processes a repository:
      - Clones the repository,
      - Ingests it into the vector store,
      - Cleans up the cloned directory.
    """
    repo_path = fetch_repo(repo)
    ingest_repo_to_vector_store(repo_path)
    logging.info(f"Repository {repo} processed successfully!")
    shutil.rmtree(repo_path)
    logging.info(f"Directory cleaned up: {repo_path}")

@task(log_prints=True)
def run_process_repo(repo: str) -> None:
    """
    Wrapper task to run the subflow process_repo.
    This function enables mapping on the subflow.
    """
    process_repo(repo)

@flow(name="Update GitHub Vector Store", log_prints=True)
def update_vector_store(repos: list[str]):
    """
    Main flow that updates the vector store by processing a list of repositories.
    Mapping is used here to run the processing of each repository in parallel.
    """
    run_process_repo.map(repos)
    logging.info("All repository processing tasks have been submitted.")

if __name__ == "__main__":
    update_vector_store.serve(
        name="github-vector-store-scheduler",
        cron="0 0 * * *",  # Run daily at midnight
        parameters={
            "repos": repos,
        },
    )
