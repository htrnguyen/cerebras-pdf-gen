# AI Document Generator

A command-line tool that uses the Google Gemini API to automatically generate detailed reports on random topics and saves them as `.docx` files.

## Features

-   Generates random, interesting topics.
- Uses the `gemini-2.5-flash` model to write 800-1200 word articles in Markdown.
-   Automatically converts Markdown files to `.docx` using Pandoc.
-   Supports concurrent document creation.

## Requirements

-   Python 3.x
-   A Google Gemini API Key.
-   **Pandoc:** You must install Pandoc and ensure its executable is in your system's PATH.

## Setup

1.  **Install Pandoc:**
    -   Go to the [official Pandoc installation page](https://pandoc.org/installing.html).
    -   Download and run the installer for your operating system.
    -   **Important:** During installation, make sure you select the option to add Pandoc to your system's PATH. You can verify this by opening a new terminal and running `pandoc --version`.

2.  **Clone the repository:**

    ```bash
    git clone https://github.com/htrnguyen/ai-document-generator.git
    cd ai-document-generator
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    -   Create a `.env` file from the example: `copy .env.example .env` (on Windows) or `cp .env.example .env` (on Mac/Linux).
    -   Add your API key to the new `.env` file:
        ```
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
    -   Get your key here: https://aistudio.google.com/api-keys
## Usage

Run the script from the command line, providing the number of documents you want to create.

**Example:** To generate 5 documents:

```bash
python main.py 5
```

The output `.docx` files will be saved in the `docs/` directory.
