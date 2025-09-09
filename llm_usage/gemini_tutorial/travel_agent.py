import vertexai
from vertexai.preview.generative_models import GenerativeModel, FunctionDeclaration, Tool, HarmCategory, HarmBlockThreshold, Content, Part

import requests
import os
from datetime import date

SERP_API_KEY = os.environ.get("SERP API", os.getenv("SERP_API_KEY"))

def event_api(query: str, htichips: str = "date:today"):
  URL = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&engine=google_events&q={query}&htichips={htichips}&hl=en&gl=us"
  response = requests.get(URL).json()
  return response["events_results"]


def hotel_api(query:str, check_in_date:str, check_out_date:int, hotel_class:int = 3, adults:int = 2):
    URL = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&engine=google_hotels&q={query}&check_in_date={check_in_date}&check_out_date={check_out_date}&adults={int(adults)}&hotel_class={int(hotel_class)}&currency=USD&gl=us&hl=en"
    response = requests.get(URL).json()
    
    return response["properties"]

event_function = FunctionDeclaration(
    name = "event_api",
    description = "Retrieves event information based on a query and optional filters.",
    parameters = {
        "type":"object",
        "properties": {
            "query":{
                "type":"string",
                "description":"The query you want to search for (e.g., 'Events in Austin, TX')."
            },
            "htichips":{
                "type":"string",
                "description":"""Optional filters used for search. Default: 'date:today'.
                
                Options:
                - 'date:today' - Today's events
                - 'date:tomorrow' - Tomorrow's events
                - 'date:week' - This week's events
                - 'date:weekend' - This weekend's events
                - 'date:next_week' - Next week's events
                - 'date:month' - This month's events
                - 'date:next_month' - Next month's events
                - 'event_type:Virtual-Event' - Online events
                """,
            }
    },
    "required": [
            "query"
        ]
    },
)

hotel_function = FunctionDeclaration(
    name="hotel_api",
    description="Retrieves hotel information based on location, dates, and optional preferences.",
    parameters= {
        "type":"object",
        "properties": {
            "query":{
                "type":"string",
                "description":"Parameter defines the search query. You can use anything that you would use in a regular Google Hotels search."
            },
            "check_in_date":{
                "type":"string",
                "description":"Check-in date in YYYY-MM-DD format (e.g., '2024-04-30')."
            },
           "check_out_date":{
               "type":"string",
               "description":"Check-out date in YYYY-MM-DD format (e.g., '2024-05-01')."
           },
           "hotel_class":{
               "type":"integer",
                "description":"""hotel class.


                  Options:
                  - 2: 2-star
                  - 3: 3-star
                  - 4: 4-star
                  - 5: 5-star
                
                  For multiple classes, separate with commas (e.g., '2,3,4')."""
           },
           "adults":{
               "type": "integer",
               "description": "Number of adults. Only integers, no decimals or floats (e.g., 1 or 2)"
           }
    },
    "required": [
            "query",
            "check_in_date",
            "check_out_date"
        ]
    },
)



generation_config = {
    "max_output_tokens": 128,
    "temperature": .5,
    "top_p": .3,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

tools = Tool(function_declarations=[event_function, hotel_function])

model = GenerativeModel(
    #model_name = 'gemini-1.5-pro-001', 
    model_name = 'gemini-2.5-flash', 
    generation_config = generation_config, 
    safety_settings = safety_settings, 
    tools = [tools])
chat = model.start_chat()
response = chat.send_message("Hello")
print(response.text)


CallableFunctions = {
    "event_api": event_api,
    "hotel_api": hotel_api
}

today = date.today()

def mission_prompt(prompt:str):
    return f"""
    Thought: I need to understand the user's request and determine if I need to use any tools to assist them.
    Action: 
    
    - If the user's request needs following APIs from available ones: weather, event, hotel, and I have all the required parameters, call the corresponding API.
    - Otherwise, if I need more information to call an API, I will ask the user for it.
    - If the user's request doesn't need an API call or I don't have enough information to call one, respond to the user directly using the chat history.
    - Respond with the final answer only

    [QUESTION] 
    {prompt}

    [DATETIME]
    {today}

    """.strip()



def Agent(user_prompt):
    prompt = mission_prompt(user_prompt)
    response = chat.send_message(prompt)
    tools = response.candidates[0].function_calls
    while tools:
        for tool in tools:
            function_res = CallableFunctions[tool.name](**tool.args)
            response = chat.send_message(Content(role="function_response",parts=[Part.from_function_response(name=tool.name, response={"result": function_res})]))
        tools = response.candidates[0].function_calls
    return response.text


response1 = Agent("Hello")
print(response1)

response2 = Agent("What events are there to do in Atlanta, Georgia?")
print(response2)

response3 = Agent("Are there any hotel avaiable in Midtown Atlanta for this weekend?")
print(response3)
