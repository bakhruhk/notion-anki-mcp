import json
import urllib.request
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# AnkiConnect configuration
ANKI_CONNECT_URL = 'http://127.0.0.1:8765'

def request(action: str, **params: Any) -> Dict[str, Any]:
    """Create a request payload for AnkiConnect."""
    return {'action': action, 'params': params, 'version': 6}

def invoke(action: str, **params: Any) -> Any:
    """Invoke an AnkiConnect action and return the result."""
    try:
        request_data = request(action, **params)
        request_json = json.dumps(request_data).encode('utf-8')
        
        logger.debug(f"AnkiConnect request: {action} with params: {params}")
        
        req = urllib.request.Request(ANKI_CONNECT_URL, request_json)
        response = json.load(urllib.request.urlopen(req))
        
        # Validate response structure
        if not isinstance(response, dict) or len(response) != 2:
            raise Exception(f'Invalid response structure: expected 2 fields, got {len(response) if isinstance(response, dict) else "non-dict"}')
        
        if 'error' not in response:
            raise Exception('Response is missing required error field')
        
        if 'result' not in response:
            raise Exception('Response is missing required result field')
        
        if response['error'] is not None:
            raise Exception(f'AnkiConnect error: {response["error"]}')
        
        logger.debug(f"AnkiConnect response: {response['result']}")
        return response['result']
        
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to AnkiConnect: {str(e)}")
        raise Exception("Cannot connect to Anki. Please ensure Anki is running with AnkiConnect installed.") from e
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from AnkiConnect: {str(e)}")
        raise Exception("Invalid response from AnkiConnect") from e
    
    except Exception as e:
        logger.error(f"AnkiConnect error: {str(e)}")
        raise

async def add_card(deck_name: str, question: str, answer: str) -> Any:
    """Add a single card to an Anki deck using the GUI."""
    if not deck_name or not question or not answer:
        raise ValueError("Deck name, question, and answer are all required")
    
    note = {
        "deckName": deck_name.strip(),
        "modelName": "Basic",
        "fields": {
            "Front": question.strip(),
            "Back": answer.strip(),
        },
        "options": {
            "allowDuplicate": False
        },
        "tags": []
    }
    
    logger.info(f"Adding single card to deck '{deck_name}'")
    result = invoke('guiAddCards', note=note)
    return result 

async def add_notes(notes: List[Dict[str, Any]]) -> List[Optional[int]]:
    """Add multiple notes to Anki decks."""
    if not notes:
        logger.warning("No notes provided to add_notes")
        return []
    
    # Validate notes structure
    valid_notes = []
    for i, note in enumerate(notes):
        if not isinstance(note, dict):
            logger.warning(f"Skipping invalid note at index {i}: not a dict")
            continue
        
        required_fields = ['deckName', 'modelName', 'fields']
        if not all(field in note for field in required_fields):
            logger.warning(f"Skipping invalid note at index {i}: missing required fields")
            continue
        
        if not isinstance(note['fields'], dict) or 'Front' not in note['fields'] or 'Back' not in note['fields']:
            logger.warning(f"Skipping invalid note at index {i}: invalid fields structure")
            continue
        
        valid_notes.append(note)
    
    if not valid_notes:
        logger.error("No valid notes to add")
        return []
    
    logger.info(f"Adding {len(valid_notes)} notes to Anki")
    result = invoke('addNotes', notes=valid_notes)
    
    # Log results
    if isinstance(result, list):
        success_count = sum(1 for r in result if r is not None)
        logger.info(f"Successfully added {success_count}/{len(valid_notes)} notes")
    
    return result

async def create_deck(deck_name: str) -> Any:
    """Create a new Anki deck (or return existing deck ID if it exists)."""
    if not deck_name or not deck_name.strip():
        raise ValueError("Deck name cannot be empty")
    
    deck_name = deck_name.strip()
    logger.info(f"Creating/ensuring deck exists: '{deck_name}'")
    
    try:
        result = invoke('createDeck', deck=deck_name)
        logger.info(f"Deck '{deck_name}' created/verified successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to create deck '{deck_name}': {str(e)}")
        raise

async def sync_decks() -> None:
    """Synchronize Anki collection with AnkiWeb."""
    logger.info("Synchronizing Anki collection")
    try:
        invoke('sync')
        logger.info("Anki sync completed successfully")
    except Exception as e:
        logger.warning(f"Anki sync failed: {str(e)}")
        # Don't raise here as sync failure shouldn't break the card creation process