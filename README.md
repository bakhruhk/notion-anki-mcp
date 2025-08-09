# Notion-Anki MCP Server

A Model Context Protocol (MCP) server that automatically generates Anki flashcards from Notion pages. This tool extracts questions and answers from Notion toggle blocks and converts them into structured Anki cards using OpenAI's API, with real-time import via AnkiConnect.

## 🎯 Use Cases

- **Students**: Convert study notes from Notion into flashcards for spaced repetition
- **Professionals**: Transform training materials and documentation into memorable cards
- **Educators**: Quickly create quiz content from lesson plans
- **Researchers**: Convert paper summaries and key concepts into study materials

## ✨ Features

- **Notion Integration**: Extracts content from Notion pages via official API
- **Smart Parsing**: Recognizes toggle blocks as question-answer pairs
- **AI Enhancement**: Uses OpenAI to refine and improve flashcard quality  
- **Real-time Import**: Automatically adds cards to Anki via AnkiConnect
- **MCP Protocol**: Works with MCP-compatible clients like Claude Desktop

## 📋 Prerequisites

Before setting up this project, ensure you have:

1. **Notion API Access**
   - Create a [Notion integration](https://developers.notion.com/docs/create-a-notion-integration)
   - Get your API key from the integration settings

2. **OpenAI API Access**
   - Sign up for [OpenAI API](https://platform.openai.com/api-keys)
   - Create an API key with sufficient credits

3. **Anki Setup**
   - Install [Anki](https://apps.ankiweb.net/) desktop application
   - Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on
   - Keep Anki running during flashcard generation

4. **Python Environment**
   - Python 3.8 or higher
   - pip package manager

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/notion-anki-mcp.git
cd notion-anki-mcp
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
NOTION_API_KEY=your_notion_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Start the MCP Server
```bash
python server.py
```

## 📖 How to Structure Your Notion Pages

For the tool to work effectively, structure your Notion pages as follows:

### Toggle Block Format
Create toggle blocks where:
- **Toggle title** = Your question
- **Toggle content** = The answer/explanation

Example structure:
```
📝 Machine Learning Concepts

🔽 What is supervised learning?
   Supervised learning is a type of machine learning where...
   - Uses labeled training data
   - Learns mapping from inputs to outputs
   - Examples: classification, regression

🔽 What's the difference between classification and regression?
   Classification predicts categories/classes while regression predicts continuous values...
```

### Supported Content Types
Within toggle blocks, the tool supports:
- Plain text paragraphs
- Bulleted lists
- Numbered lists
- Basic formatting (bold, italic, etc.)

## 🛠️ Usage

### Via MCP Client (Recommended)
1. Configure your MCP client to connect to this server
2. Use the available tools:
   - `search_page`: Find a Notion page by name
   - `extract_page_content`: Extract questions and answers from a page
   - `generate_flashcards`: Create and import Anki cards

### Direct Python Usage
```python
import asyncio
from server import search_notion_page, fetch_page_content, generate_flashcards_gpt

async def create_flashcards(page_name):
    # Search for the page
    page_result = await search_notion_page(page_name)
    if not page_result:
        print(f"Page '{page_name}' not found")
        return
    
    # Extract content
    topics, content = await fetch_page_content(page_result['page_id'])
    
    # Generate and import flashcards
    cards = await generate_flashcards_gpt(page_name, topics, content)
    print(f"Created {len(cards)} flashcards for '{page_name}'")

# Run the example
asyncio.run(create_flashcards("Your Page Name"))
```

## 🔧 API Reference

### MCP Tools

#### `search_page`
Searches for a Notion page by name.

**Parameters:**
- `page_name` (string): The title of the Notion page to search for

**Returns:**
```json
{
  "status": "success",
  "page_name": "Page Title",
  "result": {
    "result": "Found",
    "page_id": "page-uuid",
    "link": "https://notion.so/..."
  }
}
```

#### `extract_page_content`
Extracts questions and answers from a Notion page.

**Parameters:**
- `page_id` (string): The UUID of the Notion page

**Returns:**
```json
{
  "status": "success",
  "topics": ["Topic 1", "Topic 2"],
  "content": {
    "Question 1?": "Answer 1...",
    "Question 2?": "Answer 2..."
  }
}
```

#### `generate_flashcards`
Creates Anki flashcards from extracted content.

**Parameters:**
- `page_name` (string): Name for the Anki deck
- `topics` (array): List of topics/headings from the page  
- `content` (object): Question-answer pairs

**Returns:**
```json
{
  "status": "created",
  "cards": [...],
  "message": "Created flashdeck and cards for 'Page Name' in Anki"
}
```

## 🐛 Troubleshooting

### Common Issues

**"Page not found" Error**
- Ensure the page name matches exactly (case-sensitive)
- Verify your Notion integration has access to the page
- Check that the page is in a shared workspace

**"AnkiConnect not responding" Error**
- Make sure Anki desktop is running
- Verify AnkiConnect add-on is installed and enabled
- Check that Anki isn't in review mode or showing a dialog

**"OpenAI API Error" Error**
- Verify your OpenAI API key is correct and active
- Check your API usage limits and billing
- Ensure you have access to the GPT-4 models

**Empty flashcards generated**
- Check that your Notion page uses the toggle block format
- Ensure toggle blocks contain text content
- Verify the page has actual content, not just headers

### Debug Mode
Enable debug logging by modifying `server.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Notion API](https://developers.notion.com/) for excellent documentation
- [AnkiConnect](https://github.com/FooSoft/anki-connect) for Anki integration
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP standard
- [OpenAI](https://openai.com/) for powerful language models

---

**Made with ❤️ for better learning and knowledge retention**