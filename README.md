## LLMChatExporter
Extracting chats exported from Gemini (single supported source). Not an official Gemini or Google project.

---

### Features
- Export chats from Gemini HTML exports into plain text.

### Requirements
- Python 3.10–3.13
- Dependencies (managed by Poetry):
    - beautifulsoup4 >=4.14.2,<5.0.0
    - lxml >=6.0.2,<7.0.0
    - PySide6 >=6.10.0,<7.0.0
    - black >=25.9.0,<26.0.0 (dev formatting)

### Installation (Poetry)
1. Install Poetry (if you don't have it):
- Recommended: `curl -sSL https://install.python-poetry.org | python3 -`
2. Clone the repository and install with Poetry:
```bash
git clone https://github.com/tom2208/LLMChatExporter.git
cd LLMChatExporter
poetry install
```

3. Run the CLI via Poetry:
    * One-off:
        ```bash
        poetry run python llmchatexporter <input.html> <output.md>
        ```
    * Or spawn the virtual env:
        ```bash
        poetry shell
        python llmchatexporter <input.html> <output.txt>
        ```

### Usage (CLI)
```bash
LLMChatExporter <input> <output>
```

* `<input>` - path to the Gemini-exported HTML file.
* `<output>`- path to write the extracted conversation (markdown).

How to obtain the HTML to export:

* Simple page save: Right-click the chat you want to download in your browser and choose "Save as..." (Save as HTML). This produces an HTML file the tool can parse for plain-text chats.
* If the chat contains images or dynamically loaded content: the simple "Save as..." may omit needed content. Instead:
    1. Open the chat page in Chromium/Chrome.
    2. Press F12 to open Developer Tools.
    3. In the Elements panel, right-click the top element and choose "Copy" → "Copy outerHTML" or "Copy element" (or "Copy" → "Copy outerHTML"/"Copy element" depending on your browser) to copy the full page HTML.
    4. Paste the copied content into a new .html file and save. This ensures embedded images/data and dynamic content included in the DOM are preserved for extraction.

### Example
```bash
poetry run python llmchatexporter chat_export.html conversation.md
```

### Development
Format code with Black:
```bash
black .
```

### License
GNU General Public License v3.0 — see LICENSE file.

### Contributing
Fork, create a feature branch, run tests and Black, open a PR describing your changes.

### Contact
Author: tom2208 dev.tom2208@proton.me