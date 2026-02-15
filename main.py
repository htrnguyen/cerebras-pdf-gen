import os
import sys
import time

os.environ["GRPC_VERBOSITY"] = "ERROR"

from groq import Groq
from dotenv import load_dotenv
import re
import subprocess
import json

load_dotenv()

# Read PANDOC_PATH from environment variables with fallback
PANDOC_DIR = os.getenv("PANNDOC_PATH", "pandoc-3.8")
if not PANDOC_DIR:
    print("ERROR: PANNDOC_PATH is empty in .env file")
    sys.exit(1)

PANDOC_PATH = os.path.join(PANDOC_DIR, "pandoc.exe")

print(f"Using pandoc at: {PANDOC_PATH}")


def sanitize_topic_for_filename(topic):
    """Clean the topic string to be a valid filename component."""
    invalid_chars = r'[\\/:*?"<>|]'
    cleaned_topic = re.sub(invalid_chars, "", topic)
    return cleaned_topic.strip()


def create_document(client, output_dir, file_index):
    """
    Creates a single document. Returns (success, retry_safe) where:
    - success: True if document created
    - retry_safe: True if error is temporary and worth retrying
    """
    md_filepath = None
    try:
        print(f"[{file_index}] Generating content...")

        # Prompt asking for a JSON object
        prompt = """
        Generate content for a short report or essay on a random, interesting, and specific topic. The topic can be about anything.

        Return a single, valid JSON object with NO other text before or after it.

        The JSON object must have the following three keys:
        1.  "full_topic": A string containing the full, descriptive title of the document.
        2.  "short_topic": A string containing a very short, concise phrase (5-10 words) suitable for a filename. This should be a summary of the full_topic.
        3.  "content": A string containing a detailed analysis or report on the topic, approximately 800-1200 words, in English. The content MUST be formatted in Markdown and follow this structure: Title (as the first line), Introduction, Main Body (divided into 3-4 key points with subheadings), and Conclusion.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=4096,
            top_p=1,
            stream=False,
            stop=None,
            response_format={"type": "json_object"},
        )

        # Parse the JSON response
        response_text = completion.choices[0].message.content.strip()

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if not match:
                raise ValueError("API did not return valid JSON")
            data = json.loads(match.group(0))

        full_topic = data.get("full_topic", "").strip()
        short_topic = data.get("short_topic", "").strip()
        content = data.get("content", "").strip()

        if not all([full_topic, short_topic, content]):
            raise ValueError("API response missing required keys")

        print(f"[{file_index}] ✓ Topic: {full_topic[:50]}...")

        cleaned_short_topic = sanitize_topic_for_filename(short_topic)
        base_filename = f"[Reference][AI][{cleaned_short_topic[:100]}]"
        md_filepath = os.path.join(output_dir, f"{base_filename}.md")
        docx_filepath = os.path.join(output_dir, f"{base_filename}.docx")

        # Write and convert
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(content)

        subprocess.run(
            [PANDOC_PATH, md_filepath, "-o", docx_filepath],
            check=True,
            capture_output=True,
        )

        print(f"[{file_index}] ✓ CREATED: {os.path.basename(docx_filepath)}")
        os.remove(md_filepath)
        return True, True  # success, retry_safe

    except json.JSONDecodeError as e:
        # API returned invalid JSON - likely temp error
        print(f"[{file_index}] JSON parse error - retrying...")
        return False, True

    except subprocess.CalledProcessError as e:
        # Pandoc error - not API related, don't waste quota
        error_msg = e.stderr.decode("utf-8", errors="ignore")
        print(f"[{file_index}] Pandoc error - skipping: {error_msg[:60]}...")
        if md_filepath and os.path.exists(md_filepath):
            os.remove(md_filepath)
        return False, False  # Don't retry pandoc errors

    except Exception as e:
        error_str = str(e).lower()

        # Fatal API errors - don't retry
        if any(
            x in error_str
            for x in ["invalid api key", "authentication", "unauthorized", "403", "401"]
        ):
            print(f"[{file_index}] ✗ FATAL: Invalid API key or auth issue")
            return False, False

        if any(x in error_str for x in ["model", "not found", "404"]):
            print(f"[{file_index}] ✗ FATAL: Model not found")
            return False, False

        # Temporary errors - worth retrying
        if any(
            x in error_str
            for x in ["timeout", "connection", "rate", "429", "503", "500"]
        ):
            print(f"[{file_index}] Temp error - retrying...")
            return False, True

        # Unknown error
        print(f"[{file_index}] Error: {str(e)[:60]}...")
        return False, True  # Default to retry for unknown errors


def main():
    """Main function to coordinate document creation with smart retry."""
    print("Starting document generation process...")

    # Validate pandoc path exists
    if not os.path.exists(PANDOC_PATH):
        print(f"ERROR: pandoc.exe not found at: {PANDOC_PATH}")
        print(f"Make sure PANNDOC_PATH in .env points to a valid pandoc directory")
        sys.exit(1)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: Please add your GROQ_API_KEY to the .env file")
        sys.exit(1)

    # Basic API key validation
    if len(api_key) < 20:
        print("ERROR: API key looks invalid (too short)")
        sys.exit(1)

    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"ERROR: API configuration failed: {e}")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python main.py <number_of_files>")
        sys.exit(1)

    num_files = int(sys.argv[1])
    output_dir = "docs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\nTarget: Generate {num_files} .docx file(s)")
    print("Using smart retry with exponential backoff...\n")

    success_count = 0
    consecutive_failures = 0
    max_consecutive_failures = 5  # Abort if 5 fails in a row (API issue)
    base_delay = 2  # Start with 2 second delay

    file_queue = list(range(1, num_files + 1))  # Queue of file indices to create

    while file_queue and consecutive_failures < max_consecutive_failures:
        file_index = file_queue[0]
        delay = base_delay * (2 ** (consecutive_failures // 2))  # Exponential backoff

        success, retry_safe = create_document(client, output_dir, file_index)

        if success:
            file_queue.pop(0)  # Remove from queue
            success_count += 1
            consecutive_failures = 0  # Reset counter

            # Small delay after success to avoid spam
            if file_queue:
                time.sleep(1)
        else:
            consecutive_failures += 1

            if not retry_safe:
                # Fatal error - abort immediately
                print(f"\n✗ FATAL ERROR detected - aborting to protect API quota")
                break

            if file_queue:
                print(
                    f"⏳ Waiting {delay}s before retry (attempt {consecutive_failures}/5)..."
                )
                time.sleep(delay)

    # Final report
    print(f"\n{'='*60}")
    if success_count == num_files:
        print(f"✓ SUCCESS! Created all {success_count}/{num_files} .docx files")
    elif success_count > 0:
        print(f"⚠ PARTIAL: Created {success_count}/{num_files} .docx files")
        if consecutive_failures >= max_consecutive_failures:
            print(f"  Stopped due to {consecutive_failures} consecutive failures")
    else:
        print(f"✗ FAILED: No files created")
        print(f"  Check API key validity and internet connexion")

    print(f"Files saved to: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
