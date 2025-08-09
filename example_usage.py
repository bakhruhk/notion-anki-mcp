#!/usr/bin/env python3
"""
Example usage of the Notion-Anki MCP Server.

This script demonstrates how to use the server programmatically
without MCP client integration.
"""

import asyncio
import logging
from server import search_notion_page, fetch_page_content, generate_flashcards_gpt, post_flashcards

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_flashcard_generation():
    """
    Complete demo of the flashcard generation workflow.
    
    This example shows the full process:
    1. Search for a Notion page
    2. Extract content (topics and Q&A pairs)
    3. Generate flashcards with AI
    4. Import to Anki
    """
    
    # Replace with your actual Notion page name
    page_name = "Machine Learning Fundamentals"
    
    try:
        logger.info(f"🔍 Starting demo with page: '{page_name}'")
        
        # Step 1: Search for the page
        logger.info("Step 1: Searching for Notion page...")
        page_result = await search_notion_page(page_name)
        
        if not page_result:
            logger.error(f"❌ Page '{page_name}' not found in your Notion workspace")
            logger.info("💡 Make sure:")
            logger.info("   - Page name matches exactly (case-sensitive)")
            logger.info("   - Your Notion integration has access to the page")
            logger.info("   - NOTION_API_KEY is correctly set")
            return
        
        page_id = page_result['page_id']
        logger.info(f"✅ Found page with ID: {page_id}")
        
        # Step 2: Extract content
        logger.info("Step 2: Extracting page content...")
        topics, content = await fetch_page_content(page_id)
        
        logger.info(f"📊 Extracted:")
        logger.info(f"   - {len(topics)} topics: {', '.join(list(topics)[:3])}{'...' if len(topics) > 3 else ''}")
        logger.info(f"   - {len(content)} Q&A pairs")
        
        if not content:
            logger.warning("⚠️  No Q&A content found!")
            logger.info("💡 Make sure your Notion page has toggle blocks where:")
            logger.info("   - Toggle title = Question")
            logger.info("   - Toggle content = Answer")
            return
        
        # Show first Q&A pair as example
        first_question = list(content.keys())[0]
        first_answer = content[first_question]
        logger.info(f"📝 Example Q&A:")
        logger.info(f"   Q: {first_question[:80]}{'...' if len(first_question) > 80 else ''}")
        logger.info(f"   A: {first_answer[:80]}{'...' if len(first_answer) > 80 else ''}")
        
        # Step 3: Generate flashcards
        logger.info("Step 3: Generating flashcards with AI...")
        flashcards = await generate_flashcards_gpt(page_name, topics, content)
        
        if not flashcards:
            logger.error("❌ No flashcards generated")
            logger.info("💡 Check your OpenAI API key and usage limits")
            return
        
        logger.info(f"🎯 Generated {len(flashcards)} flashcards")
        
        # Show first flashcard as example
        first_card = flashcards[0]
        logger.info(f"🃏 Example flashcard:")
        logger.info(f"   Front: {first_card['fields']['Front'][:80]}{'...' if len(first_card['fields']['Front']) > 80 else ''}")
        logger.info(f"   Back: {first_card['fields']['Back'][:80]}{'...' if len(first_card['fields']['Back']) > 80 else ''}")
        
        # Step 4: Import to Anki
        logger.info("Step 4: Importing to Anki...")
        import_result = await post_flashcards(page_name, flashcards)
        
        if import_result['status'] == 'added':
            logger.info(f"🎉 Successfully imported {len(flashcards)} flashcards to Anki deck '{page_name}'")
            logger.info("📱 Check your Anki application - the cards should be available now!")
        else:
            logger.error(f"❌ Import failed: {import_result['message']}")
            logger.info("💡 Make sure:")
            logger.info("   - Anki desktop is running")
            logger.info("   - AnkiConnect add-on is installed and enabled")
            
    except Exception as e:
        logger.error(f"💥 Demo failed with error: {str(e)}")
        logger.info("🔧 Common issues:")
        logger.info("   - Check your .env file has correct API keys")
        logger.info("   - Ensure Notion page exists and integration has access")
        logger.info("   - Verify Anki is running with AnkiConnect")


async def test_individual_components():
    """
    Test individual components separately for debugging.
    """
    logger.info("🧪 Testing individual components...")
    
    # Test 1: Notion connection
    try:
        test_page = await search_notion_page("Test Page")
        logger.info("✅ Notion API connection working")
    except Exception as e:
        logger.error(f"❌ Notion API error: {str(e)}")
    
    # Test 2: OpenAI connection  
    try:
        # This would require actual content, so we just test import
        from generate import generate_flashcards_gpt
        logger.info("✅ OpenAI module imported successfully")
    except Exception as e:
        logger.error(f"❌ OpenAI module error: {str(e)}")
    
    # Test 3: AnkiConnect
    try:
        from anki import invoke
        result = invoke('version')
        logger.info(f"✅ AnkiConnect working, version: {result}")
    except Exception as e:
        logger.error(f"❌ AnkiConnect error: {str(e)}")


if __name__ == "__main__":
    print("🚀 Notion-Anki MCP Server - Example Usage")
    print("=" * 50)
    
    # Choose which demo to run
    print("Available demos:")
    print("1. Full flashcard generation workflow")  
    print("2. Test individual components")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_flashcard_generation())
    elif choice == "2":
        asyncio.run(test_individual_components())
    else:
        print("Invalid choice. Running full demo...")
        asyncio.run(demo_flashcard_generation())
    
    print("\n🎓 Happy studying!")