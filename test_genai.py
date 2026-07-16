import os
from google import genai
from google.genai import types

def test_vertex():
    print("Testing Vertex AI...")
    client = genai.Client(
        vertexai=True,
        project="qwiklabs-gcp-01-f01da7845174",
        location="us-central1"
    )
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hi"
        )
        print(f"Success: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_vertex()
