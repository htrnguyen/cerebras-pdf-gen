# AI Document Generator

A command-line tool that uses the Google Gemini API to automatically generate detailed reports on random topics and saves them as `.docx` files.

## Features

-   Generates random, interesting topics.
- Uses the `gemini-2.5-flash` model to write 800-1200 word articles in Markdown.
-   Automatically converts Markdown files to `.docx` using Pandoc.
-   Supports concurrent document creation.

## Requirements

-   Python 3.x
-   [Pandoc](https://pandoc.org/installing.html)
-   A Google Gemini API Key.

## Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/htrnguyen/ai-document-generator.git
    cd ai-document-generator
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure API Key:**
    - Create a `.env` file in the root directory.
    - Add your API key to the `.env` file:
        ```
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```

## Usage

Run the script from the command line, providing the number of documents you want to create.

**Example:** To generate 5 documents:

```bash
python main.py 5
```

The output `.docx` files will be saved in the `docs/` directory.
