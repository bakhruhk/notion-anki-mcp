import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from mcp.server.fastmcp import FastMCP, Context
from generate import generate_flashcards_gpt
from notion import search_notion_page, fetch_page_content
from anki import create_deck, add_notes, sync_decks

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("Notion Page Analyzer")

@mcp.tool()
async def search_page(page_name: str, ctx: Context) -> Dict[str, Any]:
    """Search for a Notion page by name."""
    if not page_name or not page_name.strip():
        await ctx.session.send_log_message(level="error", data="Empty page name provided")
        return {"status": "error", "message": "Page name cannot be empty."}
    
    try:
        page = await search_notion_page(page_name.strip())
        if page:
            await ctx.session.send_log_message(level="info", data=f"Found page: {page_name}")
            return {"status": "success", "page_name": page_name, "result": page}
        else:
            await ctx.session.send_log_message(level="warning", data=f"Page not found: {page_name}")
            return {"status": "error", "page_name": page_name, "message": "Page not found."}
    except Exception as e:
        await ctx.session.send_log_message(level="error", data=f"Error searching for page {page_name}: {str(e)}")
        return {"status": "error", "page_name": page_name, "message": f"Search failed: {str(e)}"}

@mcp.tool()
async def extract_page_content(page_id: str, ctx: Context) -> Dict[str, Any]:
    """Extract topics and content from a Notion page."""
    if not page_id or not page_id.strip():
        await ctx.session.send_log_message(level="error", data="Empty page ID provided")
        return {"status": "error", "topics": [], "content": {}, "message": "Page ID cannot be empty."}
    
    try:
        topics, content = await fetch_page_content(page_id.strip())
        if not topics and not content:
            await ctx.session.send_log_message(level="warning", data=f"No content extracted from page {page_id}")
            return {"status": "error", "topics": [], "content": {}, "message": "No extractable content found in the page."}
        
        await ctx.session.send_log_message(level="info", data=f"Extracted {len(topics)} topics and {len(content)} Q&A pairs from page {page_id}")
        return {"status": "success", "topics": list(topics), "content": content, "message": f"Extracted topics and content from page ID: {page_id}"}
    except Exception as e:
        await ctx.session.send_log_message(level="error", data=f"Error extracting content from page {page_id}: {str(e)}")
        return {"status": "error", "topics": [], "content": {}, "message": f"Content extraction failed: {str(e)}"}

async def post_flashcards(page_name: str, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Add flashcards to Anki deck."""
    try:
        logger.info(f"Creating deck: {page_name}")
        await create_deck(page_name)
        
        logger.info(f"Adding {len(cards)} notes to deck")
        result = await add_notes(cards)
        
        logger.info("Syncing Anki decks")
        await sync_decks()
        
        logger.info(f"Successfully added {len(cards)} flashcards to deck '{page_name}'")
        return {"status": "added", "result": result, "message": f"Added {len(cards)} flashcards to Anki deck '{page_name}'"}
    except Exception as e:
        logger.error(f"Error adding flashcards to Anki: {str(e)}")
        return {"status": "error", "result": [], "message": f"Failed to add flashcards: {str(e)}"}

@mcp.tool()
async def generate_flashcards(page_name: str, topics: List[str], content: Dict[str, str], ctx: Context) -> Dict[str, Any]:
    """Generate flashcards from topics and content, then add to Anki."""
    # Validate inputs
    if not page_name or not page_name.strip():
        await ctx.session.send_log_message(level="error", data="Empty page name provided for flashcard generation")
        return {"status": "failed", "cards": [], "message": "Page name cannot be empty"}
    
    if not topics and not content:
        await ctx.session.send_log_message(level="error", data="No topics or content provided for flashcard generation")
        return {"status": "failed", "cards": [], "message": "No topics or content provided"}
    
    if not content:
        await ctx.session.send_log_message(level="warning", data="No content (Q&A pairs) found for flashcard generation")
        return {"status": "failed", "cards": [], "message": "No question-answer content found to generate flashcards"}
    
    try:
        await ctx.session.send_log_message(level="info", data=f"Generating flashcards for '{page_name}' with {len(topics)} topics and {len(content)} Q&A pairs")
        llm_cards = await generate_flashcards_gpt(page_name, topics, content)
        
        if not llm_cards:
            await ctx.session.send_log_message(level="warning", data="No flashcards generated by LLM")
            return {"status": "failed", "cards": [], "message": "No flashcards were generated"}
        
        await ctx.session.send_log_message(level="info", data=f"Generated {len(llm_cards)} flashcards, adding to Anki")
        publish_result = await post_flashcards(page_name, llm_cards)
        
        if publish_result["status"] == "added":
            return {"status": "created", "cards": llm_cards, "message": f"Created {len(llm_cards)} flashcards for '{page_name}' in Anki"}
        else:
            return {"status": "failed", "cards": llm_cards, "message": f"Generated cards but failed to add to Anki: {publish_result['message']}"}
    
    except Exception as e:
        await ctx.session.send_log_message(level="error", data=f"Error generating flashcards for '{page_name}': {str(e)}")
        return {"status": "failed", "cards": [], "message": f"Flashcard generation failed: {str(e)}"}

# Future feature: Add additional cards to existing deck
# async def add_cards_to_existing_deck(page_name: str, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """Add additional cards to an existing Anki deck."""
#     pass


async def demo_usage() -> None:
    """Demo function showing typical usage workflow."""
    page_name = "Backtracking II"
    logger.info(f"Starting demo with page: {page_name}")
    
    try:
        # Search for page
        page_result = await search_notion_page(page_name)
        if not page_result:
            logger.error(f"Demo page '{page_name}' not found")
            return
        
        page_id = page_result['page_id']
        logger.info(f"Found page with ID: {page_id}")
        
        # Extract content
        topics, content = await fetch_page_content(page_id)
        if not content:
            logger.warning("No content extracted for demo")
            return
        
        # Generate and add flashcards
        await create_deck(page_name)
        llm_cards = await generate_flashcards_gpt(page_name, topics, content)
        await add_notes(llm_cards)
        
        logger.info(f"Demo completed successfully: {len(llm_cards)} cards created")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting Notion-Anki MCP Server")
    try:
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise