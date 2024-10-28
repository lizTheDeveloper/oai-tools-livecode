
import os
import json

from openai import OpenAI
#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
client = OpenAI()


response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a javascript animation creator. Your role is to use javascript animation libraries and html and css to make cool animations on codepen.io. \nYou'll be asked to write a few files, respond with JSON containing the contents of those files.\nPlease use cdnjs.com links as much as possible if using external libraries."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Please make me a cool animation of 1px multicolored smoke coming out of the bottom of the canvas, that you can disturb with your mouse (but make it fancy like waving your hand through smoke), that floats up, and is made of a lightweight particle animation, make sure it spawns new things every second but doesn't let the particle expire until they hit the edge of the canvas. Use a black background and something that will show up, also ensure the canvas is fully the width of the browser. Then open index.html in chrome as the final task."
        }
      ]
    }
  ],
  temperature=1,
  max_tokens=8000,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  tools=[
    {
      "type": "function",
      "function": {
        "name": "write_file",
        "description": "Writes files, given a filename and the text content of the file",
        "parameters": {
          "type": "object",
          "required": [
            "filename",
            "content"
          ],
          "properties": {
            "filename": {
              "type": "string",
              "description": "The name of the file to be created or overwritten"
            },
            "content": {
              "type": "string",
              "description": "The text content to be written into the file"
            }
          },
          "additionalProperties": False
        },
        "strict": True
      }
    }, 
    {
        "type": "function",
        "function": {
            "name": "launch_file_in_chrome",
            "description": "Launches a file in Google Chrome",
            "parameters": {
                "type": "object",
                "required": [
                    "file_path"
                ],
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to be opened in Google Chrome"
                    }
                },
                "strict": True,
                "additionalProperties": False
            }
        }
    }
  ],
  parallel_tool_calls=True,
  response_format={
    "type": "text"
  }
)

print(response)

def write_file(arguments):
    try:
        arguments = json.loads(call.function.arguments)
        filename = arguments.get('filename')
        content = arguments.get('content')
        print(f'Writing to {filename}')
        with open(filename, 'w') as f:
            f.write(content)
        print(f'Wrote to {filename}')
        return f'Wrote to {filename}'
    except Exception as e:
        print(f'Error writing file: {e}')
        return "Error writing file"

def launch_file_in_chrome(arguments):
    file_path = json.loads(arguments).get('file_path')
    os.system(f'open -a "Google Chrome" "file:///Users/annhoward/src/oai-tools-livecode/{file_path}"')
    
tool_calls = response.choices[0].message.tool_calls
for call in tool_calls:
    print(call.function.name)
    print(call.function.arguments)
    if call.function.name == 'write_file':
        results = write_file(call.function.arguments)
    if call.function.name == 'launch_file_in_chrome':
        launch_file_in_chrome(call.function.arguments)
        
