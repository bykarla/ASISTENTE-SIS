import requests
import json
import time

BASE_URL = "http://localhost:8000"
QUERY_URL = f"{BASE_URL}/api/v1/asistente-virtual/query"

def run_test():
    # Wait for the server to be up
    print(f"Checking if {BASE_URL} is up...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print("Server is up!")
                break
        except requests.exceptions.ConnectionError:
            print(f"Server not ready, retrying in 2 seconds... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("Failed to connect to the server. Exiting tests.")
        return

    print("\n--- Test 1: Simple text query ---")
    payload = {
        "mensaje": "Hola, ¿cómo estás?",
        "tipo_entrada": "texto"
    }
    
    response = requests.post(QUERY_URL, data=payload)
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"JSON Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print("Could not parse JSON. Raw response:")
        print(response.text)

if __name__ == "__main__":
    run_test()
