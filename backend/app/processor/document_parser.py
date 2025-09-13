from typing import Dict
import PyPDF2
import docx
import os

class DocumentParser:
    def parse(self, file_path: str) -> str:
        """Parse different document types and return text content"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._parse_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._parse_word(file_path)
            elif file_extension == '.txt':
                return self._parse_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
        except Exception as e:
            raise Exception(f"Error parsing document: {str(e)}")

    def _parse_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _parse_word(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _parse_text(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()