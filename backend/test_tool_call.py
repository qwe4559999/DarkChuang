import requests
import json

def test_chat():
    url = "http://127.0.0.1:8000/api/v1/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "message": "告诉我甲基苯丙胺的结构",
        "use_rag": True
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()
