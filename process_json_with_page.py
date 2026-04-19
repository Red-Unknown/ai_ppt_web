import json
import re
import os

def normalize_brackets(text):
    text = text.replace('（', '(').replace('）', ')')
    text = text.replace('【', '(').replace('】', ')')
    text = text.replace('[', '(').replace(']', ')')
    text = text.replace('「', '(').replace('」', ')')
    text = text.replace('『', '(').replace('』', ')')
    return text

def normalize_page_numbering(page_text):
    lines = page_text.split('\n')
    result = []
    
    letter_pattern = re.compile(r'^\(([a-zA-Z])\)\s*')
    circle_pattern = re.compile(r'^([①②③④⑤⑥⑦⑧⑨⑩])')
    
    circle_to_num = {'①':'1', '②':'2', '③':'3', '④':'4', '⑤':'5', '⑥':'6', '⑦':'7', '⑧':'8', '⑨':'9', '⑩':'10'}
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            result.append(line)
            continue
        
        letter_match = letter_pattern.match(stripped)
        circle_match = circle_pattern.match(stripped)
        
        if letter_match:
            content = letter_pattern.sub('', stripped).strip()
            result.append(f"(1) {content}")
        elif circle_match:
            circle_num = circle_match.group(1)
            content = circle_pattern.sub('', stripped).strip()
            result.append(f"({circle_to_num[circle_num]}) {content}")
        else:
            result.append(line)
    
    return '\n'.join(result)

def extract_content_with_page_number(json_data):
    result = []
    
    chapters = json_data.get('data', {}).get('structurePreview', {}).get('chapters', [])
    page_number = 1
    
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
                page_text = '\n'.join(page_content)
                page_text = normalize_brackets(page_text)
                page_text = normalize_page_numbering(page_text)
                page_with_number = f"=== 第 {page_number} 页 ===\n{page_text}"
                result.append(page_with_number)
                page_number += 1
    
    return result

def main():
    json_path = r'c:\Users\38945\ai_ppt_web\ai_ppt_web\sandbox\extract.json'
    output_path = r'c:\Users\38945\ai_ppt_web\ai_ppt_web\sandbox\output_with_page.txt'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pages_content = extract_content_with_page_number(data)
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            for page in pages_content:
                f.write(page + '\n\n')
        
        print(f"处理完成！已生成 {output_path}")
        print(f"共处理 {len(pages_content)} 页")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

if __name__ == '__main__':
    main()