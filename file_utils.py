import base64
from io import BytesIO

import docx
import markdown
from htmldocx import HtmlToDocx


def generate_document(text, idx,title):
  # Convert the Markdown content to HTML
  html = markdown.markdown(text)

  # Create a new Word document
  doc = docx.Document()
  
  # Add the HTML content to the document
  doc.add_heading(f"{title}", 0)

  html_to_docx_parser = HtmlToDocx()
  html_to_docx_parser.add_html_to_document(html, doc)

  # Save the document to a BytesIO object
  file_bytes = BytesIO()
  doc.save(file_bytes)
  file_bytes.seek(0)
  
  text_bytes = file_bytes.read()

  # Create a download link for the Word document
  download_link = create_download_link(file_bytes.read(),
                                       f"generated_document_{idx}.docx")

  return download_link,text_bytes


def create_download_link(val, filename):
  b64 = base64.b64encode(val)
  return f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64.decode()}" download="{filename}">Download file</a>'
