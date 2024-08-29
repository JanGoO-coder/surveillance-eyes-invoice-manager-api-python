from fastapi import FastAPI
from docxtpl import DocxTemplate
from fastapi.responses import Response, FileResponse
from models.init import Invoice, Product, InvoiceRequest
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess
from typing import List


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


def convert_products_to_context(products: List[Product]):
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


def generate_docx(filename: str, invoice: Invoice, template: str = "surveillance_eyes_invoice_template.docx"):
    shutil.copy2(f"{TEMPLATE_DIR}{template}", f"{DOCUMENTS_DIR}{filename}")

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


def convert_file_to_pdf(docx_file_path, output_dir, pdf_filename):
    subprocess.run(
        f'libreoffice \
        --headless \
        --convert-to pdf \
        --outdir {output_dir} {docx_file_path}', shell=True)
    
    pdf_file_path = f'{output_dir}{pdf_filename}'
    
    if os.path.exists(pdf_file_path):
        return pdf_file_path
    else:
        return None
    

def generate_pdf(filename: str):
    file = convert_file_to_pdf(f"{DOCUMENTS_DIR}{filename}.docx", f"{PDFS_DIR}", f"{filename}.pdf")
    if file:
        print(f'File converted to {file}.')
    else:
        print('Unable to convert the file.')


def delete_document_files():
    for file in os.listdir(DOCUMENTS_DIR):
        os.remove(f"{DOCUMENTS_DIR}{file}")


def delete_pdf_files():
    for file in os.listdir(PDFS_DIR):
        os.remove(f"{PDFS_DIR}{file}")


@app.post("/generate/invoice/{filename}")
async def generate_invoice_files(filename: str, invoiceRequest: InvoiceRequest):
    delete_document_files()
    delete_pdf_files()

    filename = f"invoice__[{filename}][{invoiceRequest.invoice.id}]"
    generate_docx(filename + ".docx", invoiceRequest.invoice, invoiceRequest.template)
    generate_pdf(filename)

    return {
        "message": "Invoice generated successfully",
        "docx": f"/download/documents/{filename}.docx",
        "pdf": f"/download/pdfs/{filename}.pdf",
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


@app.get("/list/templates")
def list_templates():
    return os.listdir(TEMPLATE_DIR)


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

