import base64
from io import BytesIO

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



# Function to format markdown tables
# def format_markdown_tables(md_text):
#         table_pattern = r'\|.*\|.*\n\|.*\|.*\n(\|.*\|.*\n)+'
#         tables = re.findall(table_pattern, md_text, re.MULTILINE)
        
#         for table in tables:
#             formatted_table = table.replace('\n', '<br>')
#             md_text = md_text.replace(table, formatted_table)
        
#         return md_text