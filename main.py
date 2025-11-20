import os
import sys

os.environ['GRPC_VERBOSITY'] = 'ERROR'

import google.generativeai as genai
from dotenv import load_dotenv
import re
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

PANDOC_PATH = r"pandoc-3.8.2.1\pandoc.exe"

def sanitize_topic_for_filename(topic):
    """Clean the topic string to be a valid filename component."""
    invalid_chars = r'[\\/:*?"<>|]'
    cleaned_topic = re.sub(invalid_chars, '', topic)
    return cleaned_topic.strip()

def create_document(model, output_dir, file_index):
    """
    Creates a single document by generating a topic, filename, and content
    in a single API call.
    """
    md_filepath = None
    try:
        print(f"[{file_index}] Generating content with a single API call...")
        
        # New, combined prompt asking for a JSON object
        prompt = """
        Generate content for a short report or essay on a random, interesting, and specific topic. The topic can be about anything.

        Return a single, valid JSON object with NO other text before or after it.

        The JSON object must have the following three keys:
        1.  "full_topic": A string containing the full, descriptive title of the document.
        2.  "short_topic": A string containing a very short, concise phrase (5-10 words) suitable for a filename. This should be a summary of the full_topic.
        3.  "content": A string containing a detailed analysis or report on the topic, approximately 800-1200 words, in English. The content MUST be formatted in Markdown and follow this structure: Title (as the first line), Introduction, Main Body (divided into 3-4 key points with subheadings), and Conclusion.
        """

        # Configure the model to return JSON
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # Clean up and parse the JSON response
        response_text = response.text.strip()
        
        # Find the JSON object in the response text
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not match:
            raise ValueError("API did not return a valid JSON object.")
        
        json_text = match.group(0)
        data = json.loads(json_text)

        full_topic = data.get("full_topic", "").strip()
        short_topic = data.get("short_topic", "").strip()
        content = data.get("content", "").strip()

        if not all([full_topic, short_topic, content]):
            raise ValueError("API response is missing one or more required JSON keys (full_topic, short_topic, content).")

        print(f"[{file_index}] Topic: {full_topic[:60]}...")
        print(f"[{file_index}] Filename: {short_topic}")

        cleaned_short_topic = sanitize_topic_for_filename(short_topic)
        base_filename = f"[Reference][AI][{cleaned_short_topic[:100]}]"
        md_filepath = os.path.join(output_dir, f"{base_filename}.md")
        docx_filepath = os.path.join(output_dir, f"{base_filename}.docx")
        
        print(f"[{file_index}] Writing content and converting to .docx...")
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        subprocess.run(
            [PANDOC_PATH, md_filepath, "-o", docx_filepath],
            check=True, capture_output=True
        )
        
        print(f"[{file_index}] CREATED SUCCESSFULLY: {os.path.basename(docx_filepath)}")

        os.remove(md_filepath)
        return True

    except (Exception, json.JSONDecodeError) as e:
        error_message = str(e)
        if isinstance(e, subprocess.CalledProcessError):
            error_message = e.stderr.decode('utf-8', errors='ignore')
        
        # Include response text in error for better debugging
        if 'response' in locals() and hasattr(response, 'text'):
            error_message += f"\nAPI Response Text: {response.text[:500]}"

        print(f"[{file_index}] ERROR: {error_message[:400]}")
        
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
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
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
    max_workers = min(num_files, 3)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # The 'subject' argument is removed from the call
        futures = {executor.submit(create_document, model, output_dir, i + 1): i for i in range(num_files)}
        
        for future in as_completed(futures):
            if future.result():
                success_count += 1

    print(f"\nFinished! Successfully created {success_count}/{num_files} .docx files in the '{output_dir}' directory.")

if __name__ == "__main__":
    main()