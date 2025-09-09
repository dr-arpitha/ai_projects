from google import genai
from google.genai import types
import logging

# Configure logging for errors only
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def call_main():
    therapist_client = genai.Client()

    user_input = ("I am a teenager going through a hard breakup of 2 month relationship.")
    logger.info(f"Generating advise for user input: {user_input}")
    therapist_instruction = f"""
                            Analyze the emotional state and provide empathetic support based on:
                            User's message: {user_input}

                            Please provide a compassionate response with:
                            1. Validation of feelings
                            2. Gentle words of comfort
                            3. Relatable experiences
                            4. Words of encouragement
                            """

    recovery_instruction = f"""
                            Design a 7-day recovery plan based on:
                            Current state: {user_input}

                            Include:
                            1. Daily activities and challenges
                            2. Self-care routines
                            3. Social media guidelines
                            4. Mood-lifting music suggestions
                            """

    honesty_instruction = f"""
                            Provide honest, constructive feedback about:
                            Situation: {user_input}

                            Include:
                            1. Objective analysis
                            2. Growth opportunities
                            3. Future outlook
                            4. Actionable steps
                            """

    response = therapist_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=[
                therapist_instruction,
            ]
        ),
    )
    print(response.text)

    response = therapist_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=[
                recovery_instruction,
            ]
        ),
    )
    print(response.text)

    response = therapist_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=[
                honesty_instruction,
            ]
        ),
    )
    print(response.text)
    logger.info("I hope you feel better soon!!")


if __name__ == "__main__":
    call_main()


