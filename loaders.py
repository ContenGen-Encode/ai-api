from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from typing import List, Optional
from pathlib import Path
import os
import json

class JsonLoader():
    def __init__(self, file_path: str):
        self.file_path = file_path    
        self.data = None

    def load_data(self):
        with open(self.file_path, "r") as f:
            self.data = json.load(f)
        return self.data

    def get_data(self):
        return self.data

class PDFDocumentLoader:
    """
    A class to handle PDF document loading and processing using LangChain.
    """
    def __init__(self, file_path: str):
        """
        Initialize the PDF loader.
        
        Args:
            file_path (str): Path to the PDF file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")
        
        self.file_path = file_path
        self.loader = PyPDFLoader(file_path)
    
    def load_documents(self) -> List[dict]:
        """
        Load and process the PDF document.
        
        Returns:
            List[dict]: List of document pages with metadata
        """
        
        documents = self.loader.load()
        return [
            {
                "page_content": doc.page_content,
                "metadata": {
                    "source": self.file_path,
                    "page": doc.metadata.get("page", 0)
                }
            }
            for doc in documents
        ]

class CSVDocumentLoader:
    """
    A class to handle CSV document loading and processing using LangChain.
    """
    def __init__(self, file_path: str, source_column: Optional[str] = None):
        """
        Initialize the CSV loader.
        
        Args:
            file_path (str): Path to the CSV file
            source_column (Optional[str]): Column to use as source identifier
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found at {file_path}")
        
        self.file_path = file_path
        self.source_column = source_column
        self.loader = CSVLoader(
            file_path=file_path,
            source_column=source_column
        )
    
    def load_documents(self) -> List[dict]:
        """
        Load and process the CSV document.
        
        Returns:
            List[dict]: List of document rows with metadata
        """
        documents = self.loader.load()
        return [
            {
                "page_content": doc.page_content,
                "metadata": {
                    "source": self.file_path,
                    "row": idx
                }
            }
            for idx, doc in enumerate(documents)
        ]

# Example usage
if __name__ == "__main__":
    # Example with PDF
    try:
        pdf_loader = PDFDocumentLoader(r"C:\Users\Seb\Desktop\example.pdf")
        pdf_docs = pdf_loader.load_documents()
        print("PDF Documents loaded successfully!")
        print(f"Number of pages: {len(pdf_docs)}")
    except FileNotFoundError as e:
        print(f"PDF Error: {e}")
    
    # Example with CSV
    try:
        csv_loader = CSVDocumentLoader(r"C:\Users\Seb\Desktop\example.csv")
        csv_docs = csv_loader.load_documents()
        print("CSV Documents loaded successfully!")
        print(f"Number of rows: {len(csv_docs)}")
    except FileNotFoundError as e:
        print(f"CSV Error: {e}")
