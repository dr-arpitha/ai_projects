from google import genai
from google.genai import types

# Define the function declaration for the model
# schedule_meeting_function = {
#     "name": "schedule_meeting",
#     "description": "Schedules a meeting with specified attendees at a given time and date.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "attendees": {
#                 "type": "array",
#                 "items": {"type": "string"},
#                 "description": "List of people attending the meeting.",
#             },
#             "date": {
#                 "type": "string",
#                 "description": "Date of the meeting (e.g., '2024-07-29')",
#             },
#             "time": {
#                 "type": "string",
#                 "description": "Time of the meeting (e.g., '15:00')",
#             },
#             "topic": {
#                 "type": "string",
#                 "description": "The subject or topic of the meeting.",
#             },
#         },
#         "required": ["attendees", "date", "time", "topic"],
#     },
# }

# Define a function that the model can call to control smart lights
set_light_values_declaration = {
    "name": "set_light_values",
    "description": "Sets the brightness and color temperature of a light.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "integer",
                "description": "Light level from 0 to 100. Zero is off and 100 is full brightness",
            },
            "color_temp": {
                "type": "string",
                "enum": ["daylight", "cool", "warm"],
                "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.",
            },
        },
        "required": ["brightness", "color_temp"],
    },
}

# This is the actual function that would be called based on the model's suggestion
def set_light_values(brightness: int, color_temp: str) -> dict[str, int | str]:
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {"brightness": brightness, "colorTemperature": color_temp}

client = genai.Client()
tools = types.Tool(function_declarations=[set_light_values_declaration])
config = types.GenerateContentConfig(tools=[tools])
prompt = "Turn the lights down to a romantic level"

contents = [
    types.Content(
        role="user", parts=[types.Part(text=prompt)]
    )
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=config,
)

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    #  In a real app, you would call your function here:
    #  result = schedule_meeting(**function_call.args)
else:
    print("No function call found in the response.")
    print(response.text)

tool_call = response.candidates[0].content.parts[0].function_call
result = ""
if tool_call == "set_light_values":
    print(f"Function before calling: {result}")
    result = set_light_values(**tool_call.args)
    print(f"Function execution result: {result}")

#Append function result so that agent can show it to the user
function_response_part = types.Part.from_function_response(name=tool_call.name, response={"result": result})

contents.append(response.candidates[0].content)
contents.append(types.Content(
        role="user", parts=[function_response_part]
    ))

final_result = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=config,)

print(final_result.text)


