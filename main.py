import os
import sys

# Suppress gRPC warnings from the Google API library
os.environ['GRPC_VERBOSITY'] = 'ERROR'

import google.generativeai as genai
from dotenv import load_dotenv
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION: PATH TO PANDOC ---
PANDOC_PATH = r"C:\Users\Nguyen\Desktop\studocu_unlock\pandoc-3.8.2\pandoc.exe"

def sanitize_topic_for_filename(topic):
    """Clean the topic string to be a valid filename component."""
    invalid_chars = r'[\\/:*?"<>|]'
    cleaned_topic = re.sub(invalid_chars, '', topic)
    return cleaned_topic.strip()

def create_document(model, output_dir, file_index):
    """
    Creates a single document on a completely random topic.
    """
    md_filepath = None # Initialize for use in the except block
    try:
        # 1. Generate a random, interesting topic directly
        topic_prompt = "Generate a random, interesting, and specific topic for a short report or essay. The topic can be about anything. Return only the topic itself."
        topic_response = model.generate_content(topic_prompt)
        full_topic = topic_response.text.strip().replace('**', '')
        if not full_topic:
            raise ValueError("API returned an empty topic")
        print(f"[{file_index}] Topic: {full_topic[:60]}...")

        # 2. Summarize the topic for the filename
        filename_prompt = f"Summarize the following topic into ONE SINGLE, short, concise phrase (5-10 words) suitable for a filename. Only return that phrase, no explanation, no formatting, no newlines. Topic: '{full_topic}'"
        filename_response = model.generate_content(filename_prompt)
        short_topic = filename_response.text.strip().replace('**', '').replace('\n', ' ')
        if not short_topic:
            short_topic = full_topic # Fallback to the full topic
        print(f"[{file_index}] Filename: {short_topic}")

        # 3. Write the detailed content
        print(f"[{file_index}] Writing content...")
        content_prompt = f"""
        Write a detailed analysis or report, approximately 800-1200 words, in English, on the following topic: "{full_topic}".
        The document must have depth, equivalent to a high-quality academic paper (about 1-2 A4 pages).
        Required structure: Title, Introduction, Main Body (divided into 3-4 key points with subheadings), and Conclusion.
        Required format: Markdown.
        IMPORTANT: Do not include any introductory or concluding remarks, conversational text, or any content other than the document itself. The output must start directly with the title of the document.
        """
        content_response = model.generate_content(content_prompt)
        content = content_response.text

        # 4. Prepare filename and paths
        cleaned_short_topic = sanitize_topic_for_filename(short_topic)
        base_filename = f"[Reference][AI][{cleaned_short_topic[:100]}]"
        md_filepath = os.path.join(output_dir, f"{base_filename}.md")
        docx_filepath = os.path.join(output_dir, f"{base_filename}.docx")
        
        # 5. Save and convert the file
        print(f"[{file_index}] Converting to .docx...")
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        subprocess.run(
            [PANDOC_PATH, md_filepath, "-o", docx_filepath],
            check=True, capture_output=True
        )
        
        # 6. Log success
        print(f"[{file_index}] CREATED SUCCESSFULLY: {os.path.basename(docx_filepath)}")

        # 7. Clean up
        os.remove(md_filepath)
        return True

    except Exception as e:
        # Log error
        error_message = str(e)
        if isinstance(e, subprocess.CalledProcessError):
            error_message = e.stderr.decode('utf-8', errors='ignore')
        print(f"[{file_index}] ERROR: {error_message[:300]}")
        if md_filepath and os.path.exists(md_filepath):
            os.remove(md_filepath)
        return False

def main():
    """Main function to coordinate document creation."""
    print("Starting document generation process...")

    if not os.path.exists(PANDOC_PATH):
        print(f"ERROR: pandoc.exe not found at: {PANDOC_PATH}")
        sys.exit(1)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("ERROR: Please add your Gemini API Key to the .env file")
        sys.exit(1)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"ERROR: API configuration failed. Details: {e}")
        sys.exit(1)

    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python main.py <number_of_files>")
        sys.exit(1)
    num_files = int(sys.argv[1])

    output_dir = 'docs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\nWill generate {num_files} file(s) on random topics.\n")

    success_count = 0
    max_workers = min(num_files, 10)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # The 'subject' argument is removed from the call
        futures = {executor.submit(create_document, model, output_dir, i + 1): i for i in range(num_files)}
        
        for future in as_completed(futures):
            if future.result():
                success_count += 1

    print(f"\nFinished! Successfully created {success_count}/{num_files} .docx files in the '{output_dir}' directory.")

if __name__ == "__main__":
    main()