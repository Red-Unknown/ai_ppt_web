"""
Web层 - parser.py 上传接口测试
测试 /lesson/upload 和 /lesson/parse 接口
"""
import requests
import io
import json

BASE_URL = "http://localhost:8001"


def test_upload_ppt():
    """测试上传PPT文件"""
    print("=" * 60)
    print("测试 /lesson/upload 接口")
    print("=" * 60)
    
    results = []
    
    # 测试1: 上传 .ppt 文件
    print("\n[测试 1] 上传 .ppt 文件")
    files = {'file': ('test.ppt', b'fake ppt content', 'application/vnd.ms-powerpoint')}
    data = {'course_id': 'course_001', 'school_id': 'SCH001'}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/upload", files=files, data=data)
        print(f"  输入: file=test.ppt, course_id=course_001")
        print(f"  预期: 返回200状态码")
        print(f"  实际: 状态码={response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  响应: {json.dumps(result, ensure_ascii=False)[:200]}")
            results.append(("上传.ppt文件", True))
            
            # 验证响应字段
            if 'code' in result and result['code'] == 200:
                results.append(("响应code=200", True))
            else:
                results.append(("响应code=200", False))
                
            if 'data' in result and 'fileId' in result['data']:
                results.append(("响应包含fileId", True))
            else:
                results.append(("响应包含fileId", False))
        else:
            results.append(("上传.ppt文件", False))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("上传.ppt文件", False))
    
    # 测试2: 上传 .pptx 文件
    print("\n[测试 2] 上传 .pptx 文件")
    files = {'file': ('test.pptx', b'fake pptx content', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
    data = {'course_id': 'course_001', 'school_id': 'SCH001'}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/upload", files=files, data=data)
        print(f"  输入: file=test.pptx")
        print(f"  预期: 返回200状态码")
        print(f"  实际: 状态码={response.status_code}")
        results.append(("上传.pptx文件", response.status_code == 200))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data', {}).get('fileType') == 'pptx':
                results.append(("fileType正确", True))
            else:
                results.append(("fileType正确", False))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("上传.pptx文件", False))
    
    # 测试3: 上传 .pdf 文件
    print("\n[测试 3] 上传 .pdf 文件")
    files = {'file': ('test.pdf', b'fake pdf content', 'application/pdf')}
    data = {'course_id': 'course_001', 'school_id': 'SCH001'}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/upload", files=files, data=data)
        print(f"  输入: file=test.pdf")
        print(f"  预期: 返回200状态码")
        print(f"  实际: 状态码={response.status_code}")
        results.append(("上传.pdf文件", response.status_code == 200))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data', {}).get('fileType') == 'pdf':
                results.append(("pdf类型正确", True))
            else:
                results.append(("pdf类型正确", False))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("上传.pdf文件", False))
    
    # 测试4: 上传不支持的文件类型
    print("\n[测试 4] 上传不支持的文件类型 (.png)")
    files = {'file': ('test.png', b'fake png content', 'image/png')}
    data = {}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/upload", files=files, data=data)
        print(f"  输入: file=test.png")
        print(f"  预期: 返回400错误")
        print(f"  实际: 状态码={response.status_code}")
        results.append(("拒绝不支持类型", response.status_code == 400))
        
        if response.status_code == 400:
            error_msg = response.json().get('detail', '')
            print(f"  错误信息: {error_msg}")
            if 'Unsupported' in error_msg or 'type' in error_msg:
                results.append(("错误信息正确", True))
            else:
                results.append(("错误信息正确", False))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("拒绝不支持类型", False))
    
    # 测试5: 上传空文件
    print("\n[测试 5] 上传空文件")
    files = {'file': ('empty.txt', b'', 'text/plain')}
    data = {}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/upload", files=files, data=data)
        print(f"  输入: file=empty.txt (空内容)")
        print(f"  预期: 返回400错误")
        print(f"  实际: 状态码={response.status_code}")
        results.append(("拒绝空文件", response.status_code == 400))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("拒绝空文件", False))
    
    # 测试6: 测试响应字段完整性
    print("\n[测试 6] 验证响应字段完整性")
    files = {'file': ('complete_test.ppt', b'test content', 'application/vnd.ms-powerpoint')}
    data = {'course_id': 'course_complete', 'school_id': 'SCH999'}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/upload", files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            data_fields = result.get('data', {})
            
            required_fields = ['fileId', 'fileName', 'fileType', 'fileSize', 'fileUrl', 'uploadedAt']
            missing = [f for f in required_fields if f not in data_fields]
            
            print(f"  检查字段: {required_fields}")
            print(f"  缺失字段: {missing if missing else '无'}")
            results.append(("响应字段完整", len(missing) == 0))
            
            # 检查course_id和school_id是否正确传递
            if data_fields.get('courseId') == 'course_complete':
                results.append(("course_id传递正确", True))
            else:
                results.append(("course_id传递正确", False))
                
            if data_fields.get('schoolId') == 'SCH999':
                results.append(("school_id传递正确", True))
            else:
                results.append(("school_id传递正确", False))
        else:
            results.append(("响应字段完整", False))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("响应字段完整", False))
    
    return results


def test_parse_interface():
    """测试 /lesson/parse 接口"""
    print("\n" + "=" * 60)
    print("测试 /lesson/parse 接口")
    print("=" * 60)
    
    results = []
    
    # 测试1: 无签名验证
    print("\n[测试 1] 缺少签名验证")
    payload = {
        "fileUrl": "test.ppt",
        "fileType": "ppt"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/lesson/parse", json=payload)
        print(f"  输入: 无enc签名字段")
        print(f"  预期: 返回403错误")
        print(f"  实际: 状态码={response.status_code}")
        results.append(("缺少签名返回403", response.status_code == 403))
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("缺少签名返回403", False))
    
    return results


def main():
    """运行所有Web层测试"""
    print("\n" + "=" * 60)
    print("开始 Web 层测试 - parser.py 上传接口")
    print("=" * 60)
    
    all_results = []
    
    # 1. 上传接口测试
    all_results.extend(test_upload_ppt())
    
    # 2. 解析接口测试
    all_results.extend(test_parse_interface())
    
    # 输出测试汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    for name, result in all_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有Web层测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
