import base64
from io import BytesIO

import os
from doc2docx import convert
from docx import Document
import docx
import markdown2
from htmldocx import HtmlToDocx


def generate_document(text, idx,title):
  # Convert the Markdown content to HTML using markdown2
  html = markdown2.markdown(text, extras=["tables"])

  # Create a new Word document
  doc = docx.Document()

  # Add the title to the document
  doc.add_heading(title, 0)

  # Convert HTML to Word document using HtmlToDocx
  html_to_docx_parser = HtmlToDocx()
  html_to_docx_parser.add_html_to_document(html, doc)

  # Save the document to a BytesIO object
  file_bytes = BytesIO()
  doc.save(file_bytes)
  file_bytes.seek(0)
  
  text_bytes = file_bytes.read()

  return text_bytes

def generate_download_link(text,title):
  # Convert the Markdown content to HTML using markdown2
  html = markdown2.markdown(text, extras=["tables"])

  # Create a new Word document
  doc = docx.Document()

  # Add the title to the document
  doc.add_heading(title, 0)

  # Convert HTML to Word document using HtmlToDocx
  html_to_docx_parser = HtmlToDocx()
  html_to_docx_parser.add_html_to_document(html, doc)


  # Save the document to a BytesIO object
  file_bytes = BytesIO()
  doc.save(file_bytes)
  file_bytes.seek(0)

  # Create a download link for the Word document
  download_link = create_download_link(file_bytes.read(),
                                       f"{title}.docx")
  return download_link


def create_download_link(val, filename):
  b64 = base64.b64encode(val)
  return f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64.decode()}" download="{filename}">Download file</a>'


def extract_doc_text(uploaded_file):
    
  tmpdirname = './tmp'
  if not os.path.exists(tmpdirname):
      os.makedirs(tmpdirname)

  # Define the paths for the input and output files
  input_file_path = os.path.join(tmpdirname, uploaded_file.name)
  output_file_path = os.path.join(tmpdirname, "output.docx")
  
  # Save the uploaded file to the tmp location
  with open(input_file_path, 'wb') as f:
      f.write(uploaded_file.read())
  
  try:
      convert(input_file_path, output_file_path)
      all_text = extract_docx_text(output_file_path)      
      return all_text  
  finally:
      # Clean up the temporary files if needed
      if os.path.exists(input_file_path):
          os.remove(input_file_path)
      if os.path.exists(output_file_path):
          os.remove(output_file_path)

def extract_docx_text(docx_file):
    doc = Document(docx_file)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)
