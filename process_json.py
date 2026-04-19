import json
import os

def extract_content_by_page(json_data):
    result = []
    
    chapters = json_data.get('data', {}).get('structurePreview', {}).get('chapters', [])
    
    for chapter in chapters:
        sub_chapters = chapter.get('subChapters', [])
        
        for sub_chapter in sub_chapters:
            page_content = []
            elements = sub_chapter.get('elements', [])
            
            for element in elements:
                elem_type = element.get('type')
                
                if elem_type == 'text':
                    content = element.get('content', '').strip()
                    content = content.replace('\n', '')
                    if content:
                        page_content.append(content)
                
                elif elem_type == 'image':
                    relationship = element.get('relationship', '')
                    content_data = element.get('content_data', '')
                    if relationship or content_data:
                        img_desc = f"'{relationship},{content_data}'"
                        page_content.append(img_desc)
            
            if page_content:
                result.append('\n'.join(page_content))
    
    return result

def main():
    json_path = r'c:\Users\38945\ai_ppt_web\ai_ppt_web\sandbox\extract.json'
    output_path = r'c:\Users\38945\ai_ppt_web\ai_ppt_web\sandbox\output.txt'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pages_content = extract_content_by_page(data)
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            for page in pages_content:
                f.write(page + '\n\n')
        
        print(f"处理完成！已生成 {output_path}")
        print(f"共处理 {len(pages_content)} 页")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

if __name__ == '__main__':
    main()