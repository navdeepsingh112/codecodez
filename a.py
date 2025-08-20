import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
 # Optional. Site URL for rankings on openrouter.ai.
# Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "deepseek/deepseek-r1-0528:free",
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ],
    
  })
)
print("Full API Response:", response.json())