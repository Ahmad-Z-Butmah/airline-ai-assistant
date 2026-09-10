# Airline AI Assistant

Airline AI Assistant is a multimodal customer support application built with Python, Google Gemini, Gradio, and SQLite.

The assistant can answer travel questions, retrieve ticket prices from a local database, generate destination images, and convert responses into speech.

## Overview

The project combines conversational AI with function calling and multimodal output to create a simple airline support experience.

The application can:

- Answer customer travel questions
- Maintain conversation history
- Retrieve ticket prices from SQLite
- Use function calling to access application data
- Generate travel images for supported destinations
- Convert text responses into speech
- Display text, image, and audio responses through Gradio

## Available Destinations

The current ticket database includes:

- London
- Paris
- Tokyo
- Sydney

## How It Works

1. The user sends a travel question through the Gradio interface.
2. Gemini analyzes the request and conversation history.
3. If a ticket price is needed, the model calls the price lookup function.
4. The application retrieves the matching price from SQLite.
5. Gemini generates the final response using the returned data.
6. If the destination is supported, the application can also generate a travel image.
7. The response can be converted into speech and returned with the text output.

```text
Customer Question
        |
        v
      Gemini
        |
        v
  Function Calling
        |
        v
      SQLite
        |
        v
  Final Response
     /       \
    v         v
 Image      Speech
        |
        v
   Gradio Interface
```

## Example

A customer can ask:

```text
How much is a ticket to Paris?
```

The assistant retrieves the ticket price from the SQLite database and includes it in the generated response.

When a supported destination is mentioned, the application can also generate a destination image and an audio version of the response.

## Tech Stack

- Python
- Google Gemini
- Gradio
- SQLite
- Function Calling
- Image Generation
- Text-to-Speech

## Project Structure

```text
airline-ai-assistant/
│
├── main.py
├── prices.db
├── .env
├── .gitignore
└── requirements.txt
```

The SQLite database is created automatically when the application runs for the first time.

## Running the Project

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Run the application:

```powershell
python main.py
```

Open the Gradio link shown in the terminal in your browser.

## Security

API keys and sensitive configuration should not be committed to the repository.

Keep the `.env` file excluded through `.gitignore` and use environment variables for private credentials.
