import os
import sqlite3
import base64
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types
import gradio as gr
from PIL import Image


# =========================
# Environment
# =========================

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("Gemini API key found")
else:
    print("Gemini API key not found")


client = genai.Client(api_key=api_key)


# =========================
# Models
# =========================

CHAT_MODEL = "gemini-3.6-flash"
IMAGE_MODEL = "gemini-3.1-flash-image"
TTS_MODEL = "gemini-3.1-flash-tts-preview"


# =========================
# Database
# =========================

DB = "prices.db"


def initialize_database():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                city TEXT PRIMARY KEY,
                price REAL
            )
        """)

        conn.commit()


def set_ticket_price(city, price):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prices (city, price)
            VALUES (?, ?)
            ON CONFLICT(city)
            DO UPDATE SET price = ?
        """, (city.lower(), price, price))

        conn.commit()


def seed_database():
    ticket_prices = {
        "london": 799,
        "paris": 899,
        "tokyo": 1420,
        "sydney": 2999
    }

    for city, price in ticket_prices.items():
        set_ticket_price(city, price)


def get_ticket_price(destination_city: str):
    """
    Get the price of a return ticket to a destination city.

    Args:
        destination_city: The city the customer wants to travel to.

    Returns:
        Ticket price information for the requested city.
    """

    print(
        f"DATABASE TOOL CALLED: Getting price for {destination_city}",
        flush=True
    )

    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT price FROM prices WHERE city = ?",
            (destination_city.lower(),)
        )

        result = cursor.fetchone()

    if result:
        return {
            "destination_city": destination_city,
            "price": result[0]
        }

    return {
        "destination_city": destination_city,
        "price": None,
        "message": "No price data available for this city"
    }


initialize_database()
seed_database()


# =========================
# System Prompt
# =========================

system_message = """
You are a helpful customer support assistant for an airline called FlightAI.

Give short and courteous answers.

Always be accurate.

If you do not know the answer, say so.

When a customer asks about the price of a flight,
use the get_ticket_price tool.

When a destination city is discussed,
mention the city clearly in your response.
"""


# =========================
# Gemini Chat
# =========================

def chat_with_gemini(message, history):

    conversation = []

    for item in history:

        role = item["role"]

        if role == "assistant":
            role = "model"

        conversation.append(
            types.Content(
                role=role,
                parts=[
                    types.Part(
                        text=item["content"]
                    )
                ]
            )
        )

    conversation.append(
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=message
                )
            ]
        )
    )

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=conversation,
        config=types.GenerateContentConfig(
            system_instruction=system_message,
            tools=[
                get_ticket_price
            ]
        )
    )

    return response.text


# =========================
# Image Generation
# =========================

def artist(city):

    prompt = f"""
Create a vibrant travel image representing a vacation in {city}.

Show famous tourist attractions and visual elements associated with the city.

Use a colorful modern travel-poster style.
"""

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=[prompt]
    )

    for part in response.parts:

        if part.inline_data is not None:

            image = part.as_image()

            image_path = "destination.png"

            image.save(image_path)

            return image_path

    return None


# =========================
# Text To Speech
# =========================

def save_wave_file(
    filename,
    pcm,
    channels=1,
    rate=24000,
    sample_width=2
):

    with wave.open(filename, "wb") as wf:

        wf.setnchannels(channels)

        wf.setsampwidth(sample_width)

        wf.setframerate(rate)

        wf.writeframes(pcm)


def talker(message):

    interaction = client.interactions.create(
        model=TTS_MODEL,
        input=f"Say clearly and professionally: {message}",
        response_format={
            "type": "audio"
        },
        generation_config={
            "speech_config": [
                {
                    "voice": "Kore"
                }
            ]
        }
    )

    audio_data = base64.b64decode(
        interaction.output_audio.data
    )

    audio_path = "response.wav"

    save_wave_file(
        audio_path,
        audio_data
    )

    return audio_path


# =========================
# Find Destination
# =========================

def detect_destination(message):

    cities = [
        "london",
        "paris",
        "tokyo",
        "sydney"
    ]

    message_lower = message.lower()

    for city in cities:

        if city in message_lower:

            return city.title()

    return None


# =========================
# Main Chat Function
# =========================

def chat(message, history):

    reply = chat_with_gemini(
        message,
        history
    )

    history = history + [
        {
            "role": "user",
            "content": message
        },
        {
            "role": "assistant",
            "content": reply
        }
    ]

    voice = talker(reply)

    city = detect_destination(message)

    image = None

    if city:
        image = artist(city)

    return "", history, voice, image


# =========================
# Gradio UI
# =========================

with gr.Blocks() as ui:

    gr.Markdown(
        "# FlightAI - Airline Assistant"
    )

    with gr.Row():

        chatbot = gr.Chatbot(
            height=500,
         
        )

        image_output = gr.Image(
            height=500,
            interactive=False
        )

    with gr.Row():

        audio_output = gr.Audio(
            autoplay=True
        )

    with gr.Row():

        message = gr.Textbox(
            label="Chat with our AI Assistant:"
        )

    message.submit(
        chat,
        inputs=[
            message,
            chatbot
        ],
        outputs=[
            message,
            chatbot,
            audio_output,
            image_output
        ]
    )


ui.launch(
    inbrowser=True
)