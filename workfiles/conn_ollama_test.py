import requests
import socket


def test_ollama_connection():
    # Test 1: Check if port is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 11434))
    if result == 0:
        print("Port 11434 is open")
    else:
        print("Port 11434 is closed")
    sock.close()

    # Test 2: Test API endpoint and list models
    try:
        response = requests.get('http://localhost:11434/api/tags')
        print("\nAPI Response Status:", response.status_code)
        if response.status_code == 200:
            models = response.json()
            print("Available models:", models)

            if not models or 'deepseek-coder' not in str(models):
                print("\nDeepseek-coder not found. Installing...")
                # Test model pull
                pull_response = requests.post(
                    'http://localhost:11434/api/pull',
                    json={"name": "deepseek-coder"}
                )
                print("Pull response:", pull_response.status_code)
                if pull_response.status_code == 200:
                    print("Deepseek-coder installed successfully")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Ollama API")
    except Exception as e:
        print(f"Error: {str(e)}")


def test_ollama_mistral():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        print("\nAPI Response Status:", response.status_code)
        if response.status_code == 200:
            models = response.json()
            print("Available models:", models)

            if not models or 'mistral' not in str(models):
                print("\nMistral not found. Installing...")
                # Test model pull
                pull_response = requests.post(
                    'http://localhost:11434/api/pull',
                    json={"name": "mistral"}
                )
                print("Pull response:", pull_response.status_code)
                if pull_response.status_code == 200:
                    print("Mistral installed successfully")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Ollama API")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_ollama_mistral()
