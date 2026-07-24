from google import genai
import os

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
print("이미지 관련 모델 목록:")
for m in client.models.list():
    if 'image' in m.name.lower() or 'imagen' in m.name.lower():
        print(m.name)
