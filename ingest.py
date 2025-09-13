from opensearchpy import OpenSearch
from preprocess import extract_text_from_pdf, extract_text_from_docx, extract_text_from_image, summarize, tag_document, translate

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "ChangeMeAdmin123!"),
    use_ssl=False,
    verify_certs=False
)

def ingest_file(file_path, file_type):
    if file_type == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        text = extract_text_from_docx(file_path)
    elif file_type == "image":
        text = extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file type")

    doc = {
        "summary": summarize(text),
        "tags": tag_document(text),
        "translation": translate(text),
        "original_text": text
    }

    client.index(index="documents", body=doc)
    print(f"Document ingested: {doc}")

# Example run
ingest_file("sample.pdf", "pdf")
