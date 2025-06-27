from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq
from brain_of_the_doctor import encode_image

# Test if the model supports vision
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Test with the acne image
    encoded_image = encode_image("acne.jpg")
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "What do you see in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=100
    )
    
    print("SUCCESS: Model supports vision!")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("This model might not support vision. Let's try text-only.")
    
    # Test text-only
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, can you see images?"
                }
            ],
            max_tokens=50
        )
        print(f"Text-only works: {completion.choices[0].message.content}")
    except Exception as e2:
        print(f"Text-only also failed: {e2}")
