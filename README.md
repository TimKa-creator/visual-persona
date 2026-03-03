# 👗✨ AI Stylist Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![AI](https://img.shields.io/badge/AI-Google_Gemini-orange)
![Telegram](https://img.shields.io/badge/Interface-Aiogram_3-blue)
![Style](https://img.shields.io/badge/Vibe-Stylist-purple)

A Telegram bot that acts as your **personal elite image maker and stylist**. Send it a photo, and it analyzes your physical features to recommend perfectly matching clothing palettes, flattering hairstyles, makeup techniques, and your unique aesthetic vibe.

The bot uses Google's Gemini Vision API to understand facial proportions, skin undertones, and overall aesthetics, translating visual data into a comprehensive personal style guide.

---

## 🚀 Features

* **🖼️ Deep Visual Analysis:** Goes beyond basic object recognition to analyze face shapes, body proportions, and colorimetry.
* **🎭 Comprehensive Style Breakdown:** Generates highly structured, personalized advice across 7 key categories:
    * 📐 **Face Shape & Features:** Identifies the shape (oval, square, heart, etc.) and analyzes proportions.
    * 🎨 **Color Season:** Determines seasonal color palette (Winter, Spring, Summer, Autumn) based on skin, eyes, and hair.
    * 👗 **Figure & Silhouettes:** Highlights physical strengths and suggests the best clothing cuts.
    * ✂️ **Hair & Makeup:** Recommends haircuts, styling, and makeup accents that flatter natural features.
    * 🧥 **Clothing Palette:** Lists refreshing colors to wear and shades to avoid.
    * ✨ **Style Vector & Vibe:** Defines the core aesthetic (e.g., Dramatic, Romantic, Natural) and the first impression you make.
    * 🐾 **Animal Spirit:** A playful, metaphorical association based on facial features (e.g., fox, feline, deer).
* **🔄 Multi-Key Rotation System:** Built-in API key load balancer. Automatically switches between multiple Gemini API keys to bypass free-tier rate limits (429 errors) and ensure 100% uptime.
* **⚡ Fully Asynchronous:** Built on `aiogram 3.x`, handling multiple users concurrently without blocking the main thread.
* **📝 Graceful Formatting:** Smart HTML parsing and custom text-chunking mechanism ensure long, detailed analyses are delivered beautifully without hitting Telegram's 4096-character limit.

---

## 🛠️ Tech Stack & Architecture

The processing pipeline is designed for speed, stability, and aesthetic output:

1.  **Input:** User sends a photo via Telegram (`aiogram`).
2.  **In-Memory Processing:** The image is downloaded to RAM using `BytesIO` (not saved to disk) for fast processing and optimal cloud deployment. `PIL` prepares the image for the Vision model.
3.  **AI Generation (`google-generativeai`):**
    * A highly structured prompt strictly forces the LLM to output specific HTML formatting instead of Markdown.
    * The image bytes are passed to the `gemini-1.5-flash` model.
    * If a rate limit (`ResourceExhausted`) is hit, the global key index shifts, hot-swaps the API key, and retries seamlessly.
4.  **Output:** Long HTML responses are smartly chunked by paragraphs (`\n\n`) to prevent broken tags and sent back to the user with a slight delay to respect Telegram's flood limits.

---

## ⚙️ Installation

### Prerequisites
* **Python 3.10+**
* A Telegram Bot Token from [@BotFather](https://t.me/botfather).
* One or more API keys from [Google AI Studio](https://aistudio.google.com/).

### Steps

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-stylist-bot.git](https://github.com/YOUR_USERNAME/ai-stylist-bot.git)
    cd ai-stylist-bot
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Create a `.env` file in the root directory. Add multiple Gemini keys separated by commas (no spaces) to enable the Key Rotation feature.
    ```env
    BOT_TOKEN=your_telegram_bot_token_here
    GEMINI_API_KEY=key1,key2,key3
    ```

5.  **Run the bot**
    ```bash
    python bot.py
    ```

---

## 📂 Project Structure

* `bot.py` - Core application logic, API rotation, HTML chunking, and Telegram handlers.
* `.env` - Environment variables (ignored by git).
* `requirements.txt` - Python dependencies for deployment.
* `.gitignore` - Standard Python gitignore rules.

---

## 🐛 Troubleshooting

* **API Key Invalid (400):** Ensure your `GEMINI_API_KEY` string has no spaces around the commas or equal sign.
* **Rate Limits (429):** The bot handles this automatically if multiple keys are provided. If all keys are exhausted, the bot will gracefully notify the user to try again later.
* **Telegram Parse Error:** If the AI hallucinates Markdown despite the prompt, the HTML chunker might fail. The prompt is strictly engineered to prevent this, but monitor logs if it happens.
* **Missing Dependencies:** Ensure your virtual environment is activated `(venv)` before running `pip install`.

---

## 📜 License

This project is open-source and created for educational and aesthetic purposes.