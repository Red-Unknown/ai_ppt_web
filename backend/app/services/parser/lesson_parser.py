
import os
import uuid
import requests
import tempfile
import win32com.client
import pythoncom
from typing import Dict, Any, List, Optional
from pptx import Presentation
from pypdf import PdfReader
from backend.app.schemas.parser import Chapter, SubChapter, FileInfo, StructurePreview, PageElement, BoundingBox

# Import pdfminer.six components
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine, LTTextBox

class LessonParserService:
    def __init__(self):
        pass

    def parse_courseware(self, file_url: str, file_type: str) -> Dict[str, Any]:
        """
        Main entry point for parsing courseware.
        Returns a dictionary matching the ParseData schema structure (minus parseId/taskStatus).
        """
        # 1. Download the file
        temp_file_path = self._download_file(file_url)
        converted_file_path = None
        
        try:
            if file_type.lower() in ['ppt', 'pptx']:
                # If it's a .ppt file, convert to .pptx first using COM
                if temp_file_path.lower().endswith('.ppt'):
                    converted_file_path = self._convert_ppt_to_pptx(temp_file_path)
                    return self._parse_ppt(converted_file_path, file_url)
                else:
                    return self._parse_ppt(temp_file_path, file_url)
            elif file_type.lower() == 'pdf':
                return self._parse_pdf(temp_file_path, file_url)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        finally:
            # Cleanup temp file
            if os.path.exists(temp_file_path):
                # Only delete if it was downloaded (not local original)
                if temp_file_path != file_url:
                    try:
                        os.remove(temp_file_path)
                    except:
                        pass
            if converted_file_path and os.path.exists(converted_file_path):
                try:
                    os.remove(converted_file_path)
                except:
                    pass

    def _download_file(self, url: str) -> str:
        # Check if it's a local path first (for testing/sandbox)
        if os.path.exists(url):
            return url
            
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create a temporary file
        suffix = os.path.splitext(url)[1]
        if not suffix:
             # Default fallback if no extension in URL
            suffix = ".tmp" 
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            return tmp.name

    def _convert_ppt_to_pptx(self, ppt_path: str) -> str:
        """
        Convert .ppt to .pptx using Windows COM interface.
        """
        pythoncom.CoInitialize()
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        
        abs_ppt_path = os.path.abspath(ppt_path)
        output_path = os.path.splitext(abs_ppt_path)[0] + "_converted.pptx"
        
        try:
            # Use headless mode with caution, sometimes visible=1 works better
            # Open(FileName, ReadOnly, Untitled, WithWindow)
            deck = powerpoint.Presentations.Open(abs_ppt_path, True, False, False)
            deck.SaveAs(output_path, 24) # 24 is ppSaveAsOpenXMLPresentation
            deck.Close()
            return output_path
        except Exception as e:
            raise RuntimeError(f"Failed to convert PPT to PPTX: {str(e)}")
        finally:
            if powerpoint.Presentations.Count == 0:
                powerpoint.Quit()

    def _parse_ppt(self, file_path: str, original_url: str) -> Dict[str, Any]:
        prs = Presentation(file_path)
        file_size = os.path.getsize(file_path)
        page_count = len(prs.slides)
        file_name = os.path.basename(original_url)

        chapters = []
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        current_chapter = Chapter(
            chapterId=str(uuid.uuid4()),
            chapterName="默认章节",
            subChapters=[]
        )
        
        for i, slide in enumerate(prs.slides):
            title = f"第 {i+1} 页"
            if slide.shapes.title:
                title = slide.shapes.title.text
            
            elements = []
            # Extract elements with coordinates
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                if not shape.text.strip():
                    continue
                    
                # Calculate relative coordinates
                # shape.left, shape.top are in EMUs
                # slide_width, slide_height are in EMUs
                x = shape.left / slide_width
                y = shape.top / slide_height
                w = shape.width / slide_width
                h = shape.height / slide_height
                
                elements.append(PageElement(
                    type="text",
                    content=shape.text.strip(),
                    bbox=BoundingBox(x=x, y=y, width=w, height=h)
                ))

            sub_chapter = SubChapter(
                subChapterId=str(uuid.uuid4()),
                subChapterName=title.strip() if title else f"Page {i+1}",
                isKeyPoint=False,
                pageRange=f"{i+1}",
                elements=elements
            )
            current_chapter.subChapters.append(sub_chapter)
            
        chapters.append(current_chapter)

        return {
            "fileInfo": FileInfo(fileName=file_name, fileSize=file_size, pageCount=page_count),
            "structurePreview": StructurePreview(chapters=chapters)
        }

    def _parse_pdf(self, file_path: str, original_url: str) -> Dict[str, Any]:
        """
        Parse PDF using pdfminer.six to extract text blocks with coordinates.
        """
        # Get basic info
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(original_url)
        
        # Use pypdf for page count (fast)
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        
        chapters = []
        current_chapter = Chapter(
            chapterId=str(uuid.uuid4()),
            chapterName="PDF 内容",
            subChapters=[]
        )
        
        # Extract pages with layout analysis
        # This is slower but provides coordinates
        for i, page_layout in enumerate(extract_pages(file_path)):
            page_width = page_layout.width
            page_height = page_layout.height
            
            elements = []
            page_text_content = ""
            
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if not text:
                        continue
                        
                    page_text_content += text + "\n"
                    
                    # Coordinate system in PDF is bottom-left origin
                    # We need top-left origin for frontend consistency (0.0 to 1.0)
                    
                    # element.x0, element.y0 (bottom-left)
                    # element.x1, element.y1 (top-right)
                    
                    # Calculate relative coordinates (Top-Left Origin)
                    # x = x0 / width
                    # y = (height - y1) / height  <-- Flip Y axis
                    # w = (x1 - x0) / width
                    # h = (y1 - y0) / height
                    
                    x = element.x0 / page_width
                    y = (page_height - element.y1) / page_height
                    w = (element.x1 - element.x0) / page_width
                    h = (element.y1 - element.y0) / page_height
                    
                    # Clamp values to 0-1 just in case
                    x = max(0.0, min(1.0, x))
                    y = max(0.0, min(1.0, y))
                    w = max(0.0, min(1.0, w))
                    h = max(0.0, min(1.0, h))
                    
                    elements.append(PageElement(
                        type="text",
                        content=text,
                        bbox=BoundingBox(x=x, y=y, width=w, height=h)
                    ))

            # Determine title from first line of text
            lines = page_text_content.split('\n')
            title = lines[0] if lines else f"第 {i+1} 页"
            if len(title) > 50:
                title = title[:50] + "..."

            sub_chapter = SubChapter(
                subChapterId=str(uuid.uuid4()),
                subChapterName=title.strip(),
                isKeyPoint=False,
                pageRange=f"{i+1}",
                elements=elements
            )
            current_chapter.subChapters.append(sub_chapter)
            
        chapters.append(current_chapter)
        
        return {
            "fileInfo": FileInfo(fileName=file_name, fileSize=file_size, pageCount=page_count),
            "structurePreview": StructurePreview(chapters=chapters)
        }

parser_service = LessonParserService()
