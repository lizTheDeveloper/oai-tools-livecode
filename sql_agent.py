
import os
import json
import psycopg2

from openai import OpenAI
#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
client = OpenAI()

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

def execute_sql(arguments):
    try:
        arguments = json.loads(call.function.arguments)
        sql = arguments.get('sql')
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        print(f'Error executing SQL: {e}')
        return f"Error executing SQL: {e}"

def prompt_gpt(messages):
  # print(messages)
  all_messages = [{
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": """
You are a coding AI, who can write files, and execute SQL queries. 
You'll be asked by the user to perform some task, write code to the best of your ability, and use the SQL query tool to execute statements against the database we have provided.
Do not write example code, with placeholder values. Always write code that is specific to the user's request.
Never use "example.com" or IDs that you haven't verified exist in the database. The code you write will be executed, so keep this in mind as you write a query, which is why you should never use example data.
You are not educating the user, they won't see your response, so you don't need to explain your code or explain to the user how they might do something on their own.
You have two tools available to you: write_file and execute_sql.
            """
          }
        ]
      }]
  for message in messages:
    all_messages.append(message)
    
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=all_messages,
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
          "name": "execute_sql",
          "description": "Executes a SQL statement",
          "parameters": {
              "type": "object",
              "required": [
                  "sql"
              ],
              "properties": {
                  "sql": {
                      "type": "string",
                      "description": "The SQL statement to execute"
                  }
              },
              "additionalProperties": False
          },
          "strict": True
      }
    }     
    ],
    parallel_tool_calls=True,
    response_format={
        "type": "text"
      }
  )

  return response


messages = []

should_continue = True
while should_continue:
  user_request = input("> ")
  if user_request == 'exit':
    should_continue = False
    break
  
  messages.append({
      "role": "user",
      "content": [
          {
              "type": "text",
              "text": user_request
          }
      ]
  })
  
  print(messages)

  response = prompt_gpt(messages)
  if response.choices[0].message.content is not None:
    messages.append({
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": response.choices[0].message.content
            }
        ]
    })
  else:
    messages.append({
      "role": "assistant",
      "tool_calls": response.choices[0].message.tool_calls
    })

  
  tool_calls = response.choices[0].message.tool_calls
  for call in tool_calls:
      print(call.function.name)
      print(call.function.arguments)
      if call.function.name == 'write_file':
          results = write_file(call.function.arguments)
      if call.function.name == 'execute_sql':
          results = execute_sql(call.function.arguments)
      function_call_result_message = {
          "role": "tool",
          "content": json.dumps(results),
          "tool_call_id": call.id
      }
      messages.append(function_call_result_message)
  if len(tool_calls) > 0:
      response = prompt_gpt(messages)
      messages.append({
          "role": "assistant",
          "content": [
              {
                  "type": "text",
                  "text": response.choices[0].message.content
              }
          ]
      })
      print(response.choices[0].message.content)
        
