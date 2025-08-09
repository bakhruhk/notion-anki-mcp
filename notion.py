import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dotenv import load_dotenv
from notion_client import AsyncClient

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

# Notion API configuration
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Validate environment variables
notion_api_key = os.getenv("NOTION_API_KEY")
if not notion_api_key:
    raise ValueError("NOTION_API_KEY environment variable is required")

notion = AsyncClient(auth=notion_api_key)

# Removed unused dummy function - using real Notion API implementation

async def search_notion_database(database_name: str) -> Optional[Dict[str, Any]]:
    """
    Searches for a Notion database by title using the Notion Search API.
    Returns the first matching database if found; otherwise returns None.
    """
    try:
        logger.info(f"Searching for database: {database_name}")
        databases = await notion.search(
            query=database_name,
            filter={"property": "object", "value": "database"}
        )
        
        if databases and databases.get('results'):
            for db in databases['results']:
                if 'title' in db and db['title']:
                    db_title = db['title'][0]['text']['content'] if db['title'][0].get('text') else ''
                    if db_title == database_name:
                        logger.info(f"Found database: {database_name}")
                        return {'result': 'Found', 'database_id': db['id'], 'link': db['url']}
        
        logger.warning(f"Database not found: {database_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error searching for database {database_name}: {str(e)}")
        raise

async def search_notion_page(page_title: str) -> str:
    """
    Searches for a Notion page by title using the Notion Search API.
    Returns the first matching page if found; otherwise returns None.
    """
    pages = await notion.search(query=page_title, filter={"property": "object", "value": "page"})
    if pages:
        for page in pages['results']:
            if 'title' in page['properties']:
                if page['properties']['title']['title'][0]['text']['content'] == page_title:
                    return {'result': "Found", 'page_id': page['id'], 'link': page['url']}
            elif 'Name' in page['properties']:
                if page['properties']['Name']['title'][0]['text']['content'] == page_title:
                    return {'result': "Found", 'page_id': page['id'], 'link': page['url']}
    return None

async def fetch_page_content(page_id: str) -> str:
    """
    Fetches the content of a Notion page using its ID.
    """
    response = await notion.blocks.children.list(page_id)
    
    blocks = response['results']
    topics, content = await analyze_blocks(blocks)

    if topics and content:
        return topics, content
    return None

async def analyze_blocks(blocks):
    """
    Analyzes the blocks of a Notion page and returns the topics and content.
    """

    topics = set()
    content = {}

    for block in blocks:
        block_type = block.get('type', '')
        
        try:
            # Extract headings as topics
            if "heading" in block_type:
                heading_data = block.get(block_type, {})
                rich_text = heading_data.get('rich_text', [])
                if rich_text and rich_text[0].get('text'):
                    heading = rich_text[0]['text']['content']
                    if heading.strip():
                        topics.add(heading.strip())
                        logger.debug(f"Found heading: {heading}")
            
            # Extract toggle blocks as Q&A pairs
            elif block_type == 'toggle':
                toggle_data = block.get('toggle', {})
                rich_text = toggle_data.get('rich_text', [])
                if rich_text and rich_text[0].get('text'):
                    question = rich_text[0]['text']['content']
                    if question.strip():
                        answer = await get_toggle_answer(block['id'])
                        if answer.strip():
                            content[question.strip()] = answer.strip()
                            logger.debug(f"Found Q&A: {question[:50]}...")
        
        except (KeyError, IndexError, TypeError) as e:
            logger.warning(f"Error processing block {block.get('id', 'unknown')}: {str(e)}")
            continue
    
    return topics, content

async def get_toggle_answer(block_id):
    """
    Fetches the answer for a toggle block using its ID.
    """
    answer = ""

    toggle_children = await notion.blocks.children.list(block_id)
    toggle_content = toggle_children['results']

    number = 1 #to keep track of numbered list items
    previous_type = None

    for block in toggle_content:
        if block['type'] == 'paragraph':
            paragraph = block['paragraph']['rich_text']
            full_text = ""
            for excerpt in paragraph:
                if 'text' in excerpt:
                    full_text += excerpt['text']['content']
            answer += full_text + "\n"
        
        elif block['type'] == 'bulleted_list_item':
            bullet_note = block['bulleted_list_item']['rich_text']
            full_bullet = "- "
            for excerpt in bullet_note:
                if 'text' in excerpt:
                    full_bullet += excerpt['text']['content']
            answer += full_bullet + "\n"

        
        elif block['type'] == 'numbered_list_item':
            
            if previous_type == 'numbered_list_item':
                number += 1
            else:
                number = 1
            
            number_item = block['numbered_list_item']['rich_text']
            full_item = f"{number}. "
            for excerpt in number_item:
                if 'text' in excerpt:
                    full_item += excerpt['text']['content']
            answer += full_item + "\n"

        previous_type = block['type']
    
    return answer


