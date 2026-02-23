import os
import shutil
import time
import threading
import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from langchain_community.document_loaders import UnstructuredODTLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
import ollama

# Configuration
SOURCE_FOLDER = "./source"
DONE_FOLDER = "./done"
OUTPUT_FOLDER = "./output"
MODEL = "deepseek-r1:1.5b"
EMBEDDING_MODEL = "nomic-embed-text"
INACTIVITY_TIMEOUT = 10
SHUTDOWN_CHECK_INTERVAL = 1
LOG_FILE = "./odt-rag-monitor.log"
LOG_MAX_SIZE = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 10


# Setup logging
def setup_logging():
    """Setup logging to both file and console"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger



# Create necessary directories
for folder in [SOURCE_FOLDER, DONE_FOLDER, OUTPUT_FOLDER]:
    Path(folder).mkdir(exist_ok=True)

class ShutdownManager:
    def __init__(self, timeout_seconds=INACTIVITY_TIMEOUT):
        self.timeout_seconds = timeout_seconds
        self.last_activity_time = time.time()
        self.shutdown_requested = False
        self.lock = threading.Lock()

    def reset_timer(self):
        """Reset the inactivity timer"""
        with self.lock:
            self.last_activity_time = time.time()
            logging.info(f"Activity detected - timer reset. Will shutdown after {self.timeout_seconds} seconds of inactivity.")

    def check_for_shutdown(self):
        """Check if shutdown should occur due to inactivity"""
        with self.lock:
            current_time = time.time()
            time_since_activity = current_time - self.last_activity_time

            if time_since_activity >= self.timeout_seconds:
                logging.info(f"\nNo activity for {self.timeout_seconds} seconds. Initiating shutdown...")
                self.shutdown_requested = True
                return True
            return False

    def should_shutdown(self):
        """Check if shutdown has been requested"""
        with self.lock:
            return self.shutdown_requested

    def get_time_remaining(self):
        """Get time remaining until shutdown"""
        with self.lock:
            current_time = time.time()
            time_since_activity = current_time - self.last_activity_time
            return max(0, self.timeout_seconds - time_since_activity)

class ODTFileHandler(FileSystemEventHandler):
    def __init__(self, shutdown_manager):
        self.processed_files = set()
        self.shutdown_manager = shutdown_manager

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if file_path.endswith('.odt') and file_path not in self.processed_files:
            self.shutdown_manager.reset_timer()
            # Wait a moment to ensure file is fully written
            time.sleep(2)
            self.process_odt_file(file_path)

    def process_odt_file(self, file_path):
        """Process an ODT file through the RAG pipeline"""
        try:
            logging.info(f"Processing ODT file: {file_path}")
            self.processed_files.add(file_path)

            # 1. Load ODT file
            loader = UnstructuredODTLoader(file_path=file_path)
            data = loader.load()
            logging.info("Done loading ODT file...")

            if not data:
                logging.warning("No content found in ODT file")
                return

            # Preview first page content
            content = data[0].page_content
            logging.info(f"Content preview: {content[:100]}...")

            # 2. Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=300
            )
            chunks = text_splitter.split_documents(data)
            logging.info(f"Done splitting into {len(chunks)} chunks...")

            # 3. Ensure embedding model is available
            try:
                ollama.pull(EMBEDDING_MODEL)
            except Exception as e:
                logging.warning(f"Warning: Could not pull embedding model: {e}")

            # 4. Create vector database
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            collection_name = f"odt-rag-{file_name}-{int(time.time())}"

            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=OllamaEmbeddings(model=EMBEDDING_MODEL),
                collection_name=collection_name,
            )
            logging.info("Done adding to vector database...")

            # 5. Set up retrieval chain
            llm = ChatOllama(model=MODEL)

            # Multi-query retriever for better results
            QUERY_PROMPT = PromptTemplate(
                input_variables=["question"],
                template="""You stick to the original question.
                Original question: {question}""",
            )

            retriever = MultiQueryRetriever.from_llm(
                vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
            )

            # RAG prompt template
            template = """Answer the question based ONLY on the following context:
            {context}
            Question: {question}
            """

            prompt = ChatPromptTemplate.from_template(template)

            chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            # 6. Process predefined questions and generate output
            questions = [
                "Generate a short and catchy title for the given article. Output only the title in one line and nothing else."
            ]

            # Generate output content
            output_content = []
            for i, question in enumerate(questions, 1):
                logging.info(f"Processing question {i}/{len(questions)}: {question}")
                try:
                    result = chain.invoke(input=question)
                    output_content.append(f"{result}")
                    logging.info(f"Output of the LLM: {result}")
                except Exception as e:
                    output_content.append(f"\nQ{i}: {question}")
                    output_content.append(f"A{i}: Error processing question: {str(e)}")
                    output_content.append("-" * 30)

            # 7. Save output to text file
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(OUTPUT_FOLDER, f"{file_name}.txt")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_content))

            logging.info(f"Output saved to: {output_file}")

            # 8. Move processed file to DONE folder
            done_file_path = os.path.join(DONE_FOLDER, os.path.basename(file_path))
            shutil.move(file_path, done_file_path)
            logging.info(f"File moved to: {done_file_path}")

            logging.info("Processing completed successfully!")

        except Exception as e:
            logging.Error(f"Error processing file {file_path}: {str(e)}")
            # Move file to done folder even if processing failed to avoid reprocessing
            try:
                done_file_path = os.path.join(DONE_FOLDER, f"ERROR_{os.path.basename(file_path)}")
                shutil.move(file_path, done_file_path)
                logging.Error(f"Error file moved to: {done_file_path}")
            except Exception as move_error:
                logging.Error(f"Could not move error file: {move_error}")

def main():
    """Main function to start file monitoring"""
    logger = setup_logging()
    logging.info("Starting ODT file monitoring...")
    logging.info(f"Source folder: {SOURCE_FOLDER}")
    logging.info(f"Done folder: {DONE_FOLDER}")
    logging.info(f"Output folder: {OUTPUT_FOLDER}")
    logging.info(f"Model: {MODEL}")
    logging.info(f"Embedding model: {EMBEDDING_MODEL}")
    logging.info(f"Inactivity timeout: {INACTIVITY_TIMEOUT} seconds")
    logging.info("-" * 50)

    # Initialize shutdown manager
    shutdown_manager = ShutdownManager(INACTIVITY_TIMEOUT)

    # Check for existing ODT files in source folder
    handler = ODTFileHandler(shutdown_manager)

    # Process any existing ODT files
    existing_files_processed = False
    for file_name in os.listdir(SOURCE_FOLDER):
        if file_name.endswith('.odt'):
            file_path = os.path.join(SOURCE_FOLDER, file_name)
            if os.path.isfile(file_path):
                logging.info(f"Found existing ODT file: {file_name}")
                handler.process_odt_file(file_path)
                existing_files_processed = True
    if existing_files_processed:
        shutdown_manager.reset_timer()

    # Set up file watcher
    observer = Observer()
    observer.schedule(handler, SOURCE_FOLDER, recursive=False)
    observer.start()

    try:
        logging.info(f"Monitoring for new ODT files... ( Will auto-shutdown after {INACTIVITY_TIMEOUT} seconds of inactivity)")
        logging.info("To stop manually press Ctrl+C")
        while True:
            time.sleep(SHUTDOWN_CHECK_INTERVAL)
            if shutdown_manager.check_for_shutdown():
                break
            time_remaining = shutdown_manager.get_time_remaining()
            if time_remaining < 5 and time_remaining > 0:
                logging.info(f"Auto-shutdown in {time_remaining:.1f} seconds...")

    except KeyboardInterrupt:
        logging.info("\nManual shutdown requested...")

    observer.stop()
    logging.info("\nStopping file monitoring...")

    observer.join()
    logging.info("File monitoring stopped.")

if __name__ == "__main__":
    main()
