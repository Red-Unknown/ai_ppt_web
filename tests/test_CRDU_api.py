# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZWFjaGVyXzAwMSIsInJvbGUiOiJ0ZWFjaGVyIiwiZW1haWwiOiJ0ZWFjaGVyQGV4YW1wbGUuY29tIiwibmFtZSI6Ilx1NWYyMFx1ODAwMVx1NWUwOCIsImV4cCI6MTc3NjUyMDU1NX0.Y7OsDvjIJjwfst7cirSZeUS6sMzHARLxtJXGH_z_Bqs'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

results = []

def log(msg):
    results.append(msg)

log('=== 1. GET /api/v1/subjects ===')
r = requests.get('http://localhost:8001/api/v1/subjects', headers=headers)
log(f'Status: {r.status_code}')
log(f'Response: {r.text}')
log('')

log('=== 2. POST /api/v1/subjects ===')
r = requests.post('http://localhost:8001/api/v1/subjects', headers=headers, json={'name': 'Python'})
log(f'Status: {r.status_code}')
log(f'Response: {r.text}')
subject_id = r.json().get('id') if r.status_code == 201 else None
log('')

if subject_id:
    log('=== 3. PUT /api/v1/subjects/{id} ===')
    r = requests.put(f'http://localhost:8001/api/v1/subjects/{subject_id}', headers=headers, json={'name': 'Python Advanced'})
    log(f'Status: {r.status_code}')
    log(f'Response: {r.text}')
    log('')

    log('=== 4. DELETE /api/v1/subjects/{id} ===')
    r = requests.delete(f'http://localhost:8001/api/v1/subjects/{subject_id}', headers=headers)
    log(f'Status: {r.status_code}')
    log(f'Response: {r.text}')
    log('')

log('=== 5. GET /api/v1/courses ===')
r = requests.get('http://localhost:8001/api/v1/courses', headers=headers)
log(f'Status: {r.status_code}')
log(f'Response: {r.text}')
log('')

log('=== 6. POST /api/v1/courses ===')
r = requests.post('http://localhost:8001/api/v1/courses', headers=headers, json={
    'title': 'Python Basic',
    'description': 'Intro to Python',
    'subject_id': 1,
    'chapter_id': 1
})
log(f'Status: {r.status_code}')
log(f'Response: {r.text}')
course_id = r.json().get('id') if r.status_code == 201 else None
log('')

log('=== 7. GET /api/v1/courses/{id} ===')
r = requests.get('http://localhost:8001/api/v1/courses/1', headers=headers)
log(f'Status: {r.status_code}')
log(f'Response: {r.text}')
log('')

log('=== 8. PUT /api/v1/courses/{id} ===')
if course_id:
    r = requests.put(f'http://localhost:8001/api/v1/courses/{course_id}', headers=headers, json={'title': 'Python Basic Updated'})
    log(f'Status: {r.status_code}')
    log(f'Response: {r.text}')
    log('')

log('=== 9. DELETE /api/v1/courses/{id} ===')
if course_id:
    r = requests.delete(f'http://localhost:8001/api/v1/courses/{course_id}', headers=headers)
    log(f'Status: {r.status_code}')
    log(f'Response: {r.text}')
    log('')

log('=== 10. GET /api/v1/ppts ===')
r = requests.get('http://localhost:8001/api/v1/ppts', headers=headers)
log(f'Status: {r.status_code}')
log(f'Response: {r.text}')
log('')

log('=== Done ===')

with open('f:\\college\\sophomore\\服务外包\\test_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
