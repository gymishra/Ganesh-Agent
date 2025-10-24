#!/usr/bin/env python3
import zipfile
import xml.etree.ElementTree as ET
import sys

def extract_text_from_docx(docx_path):
    """Extract text from a .docx file"""
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_file:
            # Read the main document XML
            xml_content = zip_file.read('word/document.xml')
            
            # Parse the XML
            root = ET.fromstring(xml_content)
            
            # Define namespace
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Extract all text elements
            text_elements = root.findall('.//w:t', namespace)
            
            # Combine all text
            full_text = ''
            for element in text_elements:
                if element.text:
                    full_text += element.text
            
            return full_text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

if __name__ == "__main__":
    docx_path = "/home/gyanmis/Skill Builder/GenA forSAP.docx"
    text = extract_text_from_docx(docx_path)
    print(text)
