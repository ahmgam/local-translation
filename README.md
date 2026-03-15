# Local Translation Script

A CLI tool that translates text files using Ollama models. The script uses a two-step approach: first summarizing the content to understand context, then translating each line with that context in mind.

## Requirements

- Python 3
- [Ollama](https://ollama.ai/) running locally on port 11434
- Two Ollama models installed:
  - Translation model (default: `translategemma:12b`)
  - Summarization model (default: `llama3.1:8b`)

## Installation

1. Install Python dependencies:
```bash
pip install requests
```

2. Pull the required Ollama models:
```bash
ollama pull translategemma:12b
ollama pull llama3.1:8b
```

## Usage

```bash
python translate.py <file_path> [target_lang] [--output-dir <dir>]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `file_path` | Path to the file to translate | Required |
| `target_lang` | Target language for translation | `Arabic` |
| `--output-dir` | Directory to write the translated file | Overwrites original |

### Examples

```bash
# Translate to Arabic (default)
python translate.py input.txt

# Translate to French
python translate.py input.txt French

# Translate and save to output directory
python translate.py input.txt Arabic --output-dir ./translated
```

## How It Works

The script processes files in the following logical steps:

1. **Verify Ollama Connection** - Ensures the Ollama service is running and accessible at `http://localhost:11434`

2. **Read Input File** - Loads the entire file content into memory

3. **Summarize Content** - Uses the summarization model (`llama3.1:8b`) to generate a concise summary of the entire file. This provides context for better translation accuracy.

4. **Translate Line-by-Line** - Processes each non-empty line individually:
   - Passes the line to the translation model (`translategemma:12b`)
   - Includes the file summary in the prompt as context
   - Preserves empty lines as-is

5. **Write Output** - Writes the translated content to the specified output path (or overwrites the original file if no output directory is specified)

### Translation Prompt

The translation prompt includes:
- Instructions to act as a professional translator
- The generated summary for contextual understanding
- Target language specification
- Rules for accurate translation (natural phrasing, preserve meaning/tone)
- Instructions to keep markdown formatting and code snippets intact

## Configuration

Edit the constants at the top of `translate.py` to customize:

```python
OLLAMA_URL = "http://localhost:11434"      # Ollama API endpoint
TRANSLATION_MODEL = "translategemma:12b"   # Model used for translation
SUMMARIZATION_MODEL = "llama3.1:8b"        # Model used for summarization
```

## Error Handling

- If Ollama is unreachable, the script exits with an error
- If a specific line fails to translate, the original text is preserved
- HTTP errors and JSON parsing errors are caught and logged
