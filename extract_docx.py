#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
import sys

def extract_text_from_docx(docx_path):
    """Extract text from a docx file using zipfile and xml parsing"""
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_file:
            # Read the main document
            xml_content = zip_file.read('word/document.xml')
            
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Define namespace
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Extract text from all text nodes
            text_elements = root.findall('.//w:t', namespace)
            
            extracted_text = []
            for element in text_elements:
                if element.text:
                    extracted_text.append(element.text)
            
            return ' '.join(extracted_text)
            
    except Exception as e:
        return f"Error extracting text: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_docx.py <docx_file>")
        sys.exit(1)
    
    docx_file = sys.argv[1]
    text = extract_text_from_docx(docx_file)
    print(text)
