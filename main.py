from fastapi import FastAPI
from docxtpl import DocxTemplate
from fastapi.responses import Response, FileResponse
from models.init import Invoice, Product
from docx2pdf import convert
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


TEMPLATE_DIR = "download/templates/"
DOCUMENTS_DIR = "download/documents/"
PDFS_DIR = "download/pdfs/"
DOCX_MIMETYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


if not os.path.exists(DOCUMENTS_DIR):
    os.makedirs(DOCUMENTS_DIR)

if not os.path.exists(PDFS_DIR):
    os.makedirs(PDFS_DIR)


def convert_products_to_context(products: list[Product]):
    context = []
    for i, product in enumerate(products):
        context.append({
            "rn": i + 1,
            "pn": product.name,
            "pq": product.quantity,
            "pup": product.price,
            "ptp": product.price * product.quantity
        })
    return context


def generate_docx(filename: str, invoice: Invoice):
    shutil.copy2(f"{TEMPLATE_DIR}invoice_template.docx", f"{DOCUMENTS_DIR}{filename}")

    doc = DocxTemplate(f"{DOCUMENTS_DIR}{filename}")

    context = {
        "date": invoice.date,
        "title": invoice.title,
        "description": invoice.description,
        "address": invoice.address,
        "total": invoice.total,
        "products": convert_products_to_context(invoice.products)
    }

    doc.render(context)

    doc.save(f"{DOCUMENTS_DIR}{filename}")


def generate_pdf(filename: str):
    convert(f"{DOCUMENTS_DIR}{filename}.docx", f"{PDFS_DIR}{filename}.pdf")


def delete_document_files():
    for file in os.listdir(DOCUMENTS_DIR):
        os.remove(f"{DOCUMENTS_DIR}{file}")


def delete_pdf_files():
    for file in os.listdir(PDFS_DIR):
        os.remove(f"{PDFS_DIR}{file}")


@app.post("/generate/invoice/{filename}")
async def generate_invoice_files(filename: str, invoice: Invoice):
    filename = f"invoice__[{filename}][{invoice.id}]"
    generate_docx(filename + ".docx", invoice)
    generate_pdf(filename)

    return {
        "message": "Invoice generated successfully",
        "docx": f"http://localhost:8000/download/documents/{filename}.docx",
        "pdf": f"http://localhost:8000/download/pdfs/{filename}.pdf",
    }


@app.get("/download/documents/{filename}")
async def download_docx(response: Response, filename: str):
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = DOCX_MIMETYPE

    return FileResponse(f"{DOCUMENTS_DIR}{filename}", media_type=DOCX_MIMETYPE, filename=filename)


@app.get("/download/pdfs/{filename}")
async def download_pdf(response: Response, filename: str):
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/pdf"

    return FileResponse(f"{PDFS_DIR}{filename}", media_type="application/pdf", filename=filename)


@app.get("/list/documents")
def list_documents():
    return os.listdir(DOCUMENTS_DIR)


@app.get("/list/pdfs")
def list_pdfs():
    return os.listdir(PDFS_DIR)


@app.get("/delete/documents")
def delete_documents():
    delete_document_files()
    return {"message": "All documents deleted successfully"}


@app.get("/delete/pdfs")
def delete_pdfs():
    delete_pdf_files()
    return {"message": "All pdfs deleted successfully"}


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the FastAPI Docx Generator",
        "documentation_t1": "http:://localhost:8000/docs",
        "documentation_t2": "http:://localhost:8000/redoc",
    }

