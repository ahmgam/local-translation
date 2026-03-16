import argparse
import json
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants for Ollama API (with defaults from .env or current values)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "translategemma:12b")
SUMMARIZATION_MODEL = os.getenv("SUMMARIZATION_MODEL", "llama3.1:8b")


def summarize_text(text: str) -> str:
    """Summarize *text* using Ollama."""
    prompt = f"""Summarize the following text concisely. Focus on the main topics, key points, and overall context.

Text to summarize:
{text}
"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": SUMMARIZATION_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        try:
            result = response.json()
            return result.get("response", "")
        except ValueError:
            try:
                parsed = json.loads(response.text)
                return parsed.get("response", "")
            except json.JSONDecodeError:
                return ""
    except Exception as e:
        print(f"[ERROR] Summarization error: {e}")
        return ""


def translate_text(text: str, target_lang: str, summary: str = "") -> str:
    """Translate *text* into *target_lang* using Ollama."""
    # Skip translation for empty or whitespace-only lines to avoid unnecessary API calls
    if not text.strip():
        return text
    prompt = f"""You are a professional translator.

    Context:
    The following summary describes the content and context of the file being translated. Use it only to better understand the meaning of the text and produce a more accurate translation.

    Summary:
    {summary}

    Task:
    Translate the provided text into: {target_lang}.

    Rules:
    - Use the summary only as contextual guidance.
    - Translate the text faithfully while preserving the intended meaning.
    - Output ONLY the translated text.
    - Do NOT include explanations, notes, comments, or the original text.
    - If a word or phrase has multiple possible translations, choose the single most natural and contextually appropriate translation.
    - Keep the formatting of the original text (e.g., markdown syntax) intact in the translation.
    - do NOT attempt to translate code snippets, URLs, or any text that appears to be a code block. Instead, preserve them exactly as they are.
    Text to translate:
    {text}
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": TRANSLATION_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        try:
            result = response.json()
            return result.get("response", "")
        except ValueError:
            try:
                parsed = json.loads(response.text)
                return parsed.get("response", "")
            except json.JSONDecodeError:
                return text
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error: {http_err}")
        if http_err.response is not None:
            print(f"[ERROR] Response body: {http_err.response.text[:200]}")
        return text
    except Exception as e:
        print(f"[ERROR] Translation error: {e}")
        return text


def main():
    parser = argparse.ArgumentParser(
        description="Translate a markdown file using Ollama."
    )
    parser.add_argument("file_path", help="Path to the markdown file to translate")
    parser.add_argument(
        "target_lang",
        nargs="?",
        default="Arabic",
        help="Target language for translation (default: Arabic)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="Directory to write the translated file. If omitted, the original file is overwritten.",
        default=None,
    )
    args = parser.parse_args()

    # Verify Ollama service is reachable before proceeding
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"Unable to reach Ollama at {OLLAMA_URL}: {e}")
        sys.exit(1)

    if not os.path.isfile(args.file_path):
        print(f"File not found: {args.file_path}")
        sys.exit(1)

    with open(args.file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("Summarizing content...")
    summary = summarize_text(content)
    print(f"Summary: {summary[:200]}...")

    lines = content.splitlines()

    if len(lines) == 0:
        print("No lines found in input file!")
        return

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        output_path = os.path.join(args.output_dir, os.path.basename(args.file_path))
    else:
        output_path = args.file_path

    with open(output_path, "w", encoding="utf-8") as f:
        total = len(lines)
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                f.write("\n")
                f.flush()
                continue
            translated_line = translate_text(stripped, args.target_lang, summary)
            if not translated_line:
                translated_line = stripped
            f.write(translated_line + "\n")
            f.flush()

    print(f"Translation completed. Output written to {output_path}")


if __name__ == "__main__":
    main()
