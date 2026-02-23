import os
import zipfile
import xml.etree.ElementTree as ET
import sys

# Ensure UTF-8 output for Windows console
sys.stdout.reconfigure(encoding='utf-8')

def read_docx(file_path):
    try:
        with zipfile.ZipFile(file_path) as zf:
            xml_content = zf.read('word/document.xml')
        
        tree = ET.fromstring(xml_content)
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        text_parts = []
        for p in tree.findall('.//w:p', namespaces):
            paragraph_text = []
            for t in p.findall('.//w:t', namespaces):
                if t.text:
                    paragraph_text.append(t.text)
            if paragraph_text:
                text_parts.append(''.join(paragraph_text))
        
        return '\n'.join(text_parts)
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def main():
    print("Script started...", flush=True)
    base_dir = "选题"
    files = ["A02.docx", "A04.docx"]
    
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}", flush=True)
    
    target_dir = os.path.join(current_dir, base_dir)
    print(f"Target directory: {target_dir}", flush=True)
    
    if os.path.exists(target_dir):
        print("Target directory exists.", flush=True)
        print(f"Listing files in {target_dir}:", flush=True)
        try:
            print(os.listdir(target_dir), flush=True)
        except Exception as e:
            print(f"Error listing dir: {e}", flush=True)
    else:
        print("Target directory DOES NOT exist.", flush=True)

    for filename in files:
        file_path = os.path.join(base_dir, filename)
        print(f"Checking file: {file_path}", flush=True)
        
        if os.path.exists(file_path):
            print(f"--- START OF {filename} ---", flush=True)
            content = read_docx(file_path)
            print(content[:5000], flush=True)
            print(f"--- END OF {filename} ---\n", flush=True)
        else:
            print(f"File not found: {file_path} (Absolute: {os.path.abspath(file_path)})", flush=True)

if __name__ == "__main__":
    main()
