"""Voice Web Control Module

Provides voice-controlled web navigation and interaction capabilities
with Indonesian and English language support for the Jarvis AI system.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Union

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class VoiceCommand(Enum):
    """Voice commands for web control"""
    # Search commands
    SEARCH = "search"
    FIND = "find"
    LOOK_FOR = "look_for"
    
    # Navigation commands
    OPEN = "open"
    VISIT = "visit"
    GO_TO = "go_to"
    BACK = "back"
    FORWARD = "forward"
    REFRESH = "refresh"
    
    # Content commands
    READ = "read"
    SUMMARIZE = "summarize"
    EXTRACT = "extract"
    DOWNLOAD = "download"
    
    # Interaction commands
    CLICK = "click"
    SCROLL = "scroll"
    ZOOM = "zoom"
    
    # Control commands
    STOP = "stop"
    PAUSE = "pause"
    CONTINUE = "continue"

class Language(Enum):
    """Supported languages"""
    INDONESIAN = "id"
    ENGLISH = "en"

@dataclass
class VoiceIntent:
    """Parsed voice intent"""
    command: VoiceCommand
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    language: Language = Language.INDONESIAN
    timestamp: datetime = field(default_factory=datetime.now)
    
class VoiceWebConfig(BaseModel):
    """Voice web control configuration"""
    default_language: Language = Language.INDONESIAN
    confidence_threshold: float = 0.7
    max_results: int = 5
    voice_feedback: bool = True
    auto_summarize: bool = True
    safe_browsing: bool = True
    
class VoiceWebController:
    """Voice-controlled web navigation and interaction"""
    
    def __init__(self, config: VoiceWebConfig = None):
        self.config = config or VoiceWebConfig()
        self.command_handlers = self._setup_command_handlers()
        self.voice_patterns = self._setup_voice_patterns()
        self.current_session = None
        
    def _setup_command_handlers(self) -> Dict[VoiceCommand, Callable]:
        """Setup command handlers"""
        return {
            VoiceCommand.SEARCH: self._handle_search,
            VoiceCommand.FIND: self._handle_search,
            VoiceCommand.LOOK_FOR: self._handle_search,
            VoiceCommand.OPEN: self._handle_open,
            VoiceCommand.VISIT: self._handle_open,
            VoiceCommand.GO_TO: self._handle_open,
            VoiceCommand.READ: self._handle_read,
            VoiceCommand.SUMMARIZE: self._handle_summarize,
            VoiceCommand.EXTRACT: self._handle_extract,
            VoiceCommand.BACK: self._handle_navigation,
            VoiceCommand.FORWARD: self._handle_navigation,
            VoiceCommand.REFRESH: self._handle_navigation,
            VoiceCommand.STOP: self._handle_control,
            VoiceCommand.PAUSE: self._handle_control,
            VoiceCommand.CONTINUE: self._handle_control
        }
    
    def _setup_voice_patterns(self) -> Dict[Language, Dict[VoiceCommand, List[str]]]:
        """Setup voice command patterns for different languages"""
        return {
            Language.INDONESIAN: {
                VoiceCommand.SEARCH: [
                    r"cari\s+(.+)",
                    r"carikan\s+(.+)",
                    r"tolong\s+cari\s+(.+)",
                    r"pencarian\s+(.+)",
                    r"search\s+(.+)"
                ],
                VoiceCommand.FIND: [
                    r"temukan\s+(.+)",
                    r"temukankan\s+(.+)",
                    r"coba\s+temukan\s+(.+)"
                ],
                VoiceCommand.OPEN: [
                    r"buka\s+(.+)",
                    r"bukakan\s+(.+)",
                    r"tolong\s+buka\s+(.+)",
                    r"kunjungi\s+(.+)",
                    r"pergi\s+ke\s+(.+)",
                    r"masuk\s+ke\s+(.+)"
                ],
                VoiceCommand.READ: [
                    r"baca\s+(.+)",
                    r"bacakan\s+(.+)",
                    r"tolong\s+baca\s+(.+)",
                    r"baca\s+halaman\s+(.+)"
                ],
                VoiceCommand.SUMMARIZE: [
                    r"ringkas\s+(.+)",
                    r"ringkasan\s+(.+)",
                    r"buatkan\s+ringkasan\s+(.+)",
                    r"summarize\s+(.+)"
                ],
                VoiceCommand.BACK: [
                    r"kembali",
                    r"mundur",
                    r"back"
                ],
                VoiceCommand.FORWARD: [
                    r"maju",
                    r"forward",
                    r"lanjut"
                ],
                VoiceCommand.REFRESH: [
                    r"refresh",
                    r"muat\s+ulang",
                    r"reload"
                ],
                VoiceCommand.STOP: [
                    r"stop",
                    r"berhenti",
                    r"hentikan"
                ]
            },
            Language.ENGLISH: {
                VoiceCommand.SEARCH: [
                    r"search\s+for\s+(.+)",
                    r"search\s+(.+)",
                    r"find\s+(.+)",
                    r"look\s+for\s+(.+)",
                    r"google\s+(.+)"
                ],
                VoiceCommand.OPEN: [
                    r"open\s+(.+)",
                    r"visit\s+(.+)",
                    r"go\s+to\s+(.+)",
                    r"navigate\s+to\s+(.+)"
                ],
                VoiceCommand.READ: [
                    r"read\s+(.+)",
                    r"read\s+this\s+(.+)",
                    r"read\s+the\s+(.+)"
                ],
                VoiceCommand.SUMMARIZE: [
                    r"summarize\s+(.+)",
                    r"summary\s+of\s+(.+)",
                    r"give\s+me\s+a\s+summary\s+of\s+(.+)"
                ],
                VoiceCommand.BACK: [
                    r"go\s+back",
                    r"back",
                    r"previous\s+page"
                ],
                VoiceCommand.FORWARD: [
                    r"go\s+forward",
                    r"forward",
                    r"next\s+page"
                ],
                VoiceCommand.REFRESH: [
                    r"refresh",
                    r"reload",
                    r"refresh\s+page"
                ],
                VoiceCommand.STOP: [
                    r"stop",
                    r"halt",
                    r"cancel"
                ]
            }
        }
    
    def parse_voice_command(self, voice_text: str, language: Optional[Language] = None) -> Optional[VoiceIntent]:
        """Parse voice command into structured intent"""
        language = language or self.config.default_language
        voice_text = voice_text.lower().strip()
        
        logger.info(f"Parsing voice command: '{voice_text}' in {language.value}")
        
        patterns = self.voice_patterns.get(language, {})
        
        for command, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, voice_text, re.IGNORECASE)
                if match:
                    target = match.group(1) if match.groups() else ""
                    
                    intent = VoiceIntent(
                        command=command,
                        target=target.strip(),
                        confidence=0.9,  # High confidence for exact pattern match
                        language=language
                    )
                    
                    logger.info(f"Parsed intent: {command.value} -> '{target}'")
                    return intent
        
        # Fallback: try to extract search terms
        if voice_text:
            return VoiceIntent(
                command=VoiceCommand.SEARCH,
                target=voice_text,
                confidence=0.5,  # Lower confidence for fallback
                language=language
            )
        
        return None
    
    async def execute_voice_command(self, voice_text: str, 
                                  search_engine=None,
                                  content_extractor=None,
                                  browser_automation=None) -> Dict[str, Any]:
        """Execute voice command and return results"""
        intent = self.parse_voice_command(voice_text)
        
        if not intent:
            return {
                'success': False,
                'error': 'Could not understand voice command',
                'voice_response': 'Maaf, saya tidak mengerti perintah tersebut.' if self.config.default_language == Language.INDONESIAN else 'Sorry, I did not understand that command.'
            }
        
        if intent.confidence < self.config.confidence_threshold:
            return {
                'success': False,
                'error': 'Low confidence in voice command',
                'voice_response': 'Saya kurang yakin dengan perintah tersebut. Bisa diulangi?' if self.config.default_language == Language.INDONESIAN else 'I am not sure about that command. Could you repeat?'
            }
        
        # Execute command
        handler = self.command_handlers.get(intent.command)
        if handler:
            try:
                result = await handler(intent, search_engine, content_extractor, browser_automation)
                return result
            except Exception as e:
                logger.error(f"Error executing command {intent.command.value}: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'voice_response': f'Terjadi kesalahan: {str(e)}' if self.config.default_language == Language.INDONESIAN else f'An error occurred: {str(e)}'
                }
        else:
            return {
                'success': False,
                'error': f'No handler for command: {intent.command.value}',
                'voice_response': 'Perintah belum didukung.' if self.config.default_language == Language.INDONESIAN else 'Command not supported yet.'
            }
    
    async def _handle_search(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle search commands"""
        if not search_engine:
            return {
                'success': False,
                'error': 'Search engine not available',
                'voice_response': 'Mesin pencari tidak tersedia.' if intent.language == Language.INDONESIAN else 'Search engine not available.'
            }
        
        try:
            results = search_engine.search(intent.target, max_results=self.config.max_results)
            
            if not results:
                return {
                    'success': False,
                    'error': 'No search results found',
                    'voice_response': f'Tidak ditemukan hasil untuk "{intent.target}".' if intent.language == Language.INDONESIAN else f'No results found for "{intent.target}".'
                }
            
            # Prepare voice response
            if intent.language == Language.INDONESIAN:
                voice_response = f'Ditemukan {len(results)} hasil untuk "{intent.target}". '
                voice_response += f'Hasil teratas: {results[0].title}. {results[0].snippet[:100]}...'
            else:
                voice_response = f'Found {len(results)} results for "{intent.target}". '
                voice_response += f'Top result: {results[0].title}. {results[0].snippet[:100]}...'
            
            return {
                'success': True,
                'command': 'search',
                'query': intent.target,
                'results': [result.to_dict() for result in results],
                'voice_response': voice_response
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                'success': False,
                'error': str(e),
                'voice_response': f'Gagal melakukan pencarian: {str(e)}' if intent.language == Language.INDONESIAN else f'Search failed: {str(e)}'
            }
    
    async def _handle_open(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle open/visit commands"""
        target = intent.target
        
        # Check if target is a URL
        if not (target.startswith('http://') or target.startswith('https://')):
            # If not a URL, treat as search query and open first result
            if search_engine:
                try:
                    results = search_engine.search(target, max_results=1)
                    if results:
                        target = results[0].url
                    else:
                        return {
                            'success': False,
                            'error': 'No results found to open',
                            'voice_response': f'Tidak ditemukan hasil untuk dibuka: "{intent.target}".' if intent.language == Language.INDONESIAN else f'No results found to open: "{intent.target}".'
                        }
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'voice_response': f'Gagal mencari: {str(e)}' if intent.language == Language.INDONESIAN else f'Search failed: {str(e)}'
                    }
            else:
                # Assume it's a domain name
                target = f'https://{target}'
        
        # Extract content if content_extractor is available
        content = None
        if content_extractor:
            try:
                content = content_extractor.extract_from_url(target)
            except Exception as e:
                logger.warning(f"Failed to extract content from {target}: {e}")
        
        voice_response = f'Membuka {target}.' if intent.language == Language.INDONESIAN else f'Opening {target}.'
        
        if content and content.title:
            if intent.language == Language.INDONESIAN:
                voice_response += f' Halaman: {content.title}.'
                if self.config.auto_summarize and content.summary:
                    voice_response += f' Ringkasan: {content.summary[:200]}...'
            else:
                voice_response += f' Page: {content.title}.'
                if self.config.auto_summarize and content.summary:
                    voice_response += f' Summary: {content.summary[:200]}...'
        
        return {
            'success': True,
            'command': 'open',
            'url': target,
            'content': content.to_dict() if content else None,
            'voice_response': voice_response
        }
    
    async def _handle_read(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle read commands"""
        if not content_extractor:
            return {
                'success': False,
                'error': 'Content extractor not available',
                'voice_response': 'Ekstraksi konten tidak tersedia.' if intent.language == Language.INDONESIAN else 'Content extraction not available.'
            }
        
        target = intent.target
        
        # If target is not a URL, search for it first
        if not (target.startswith('http://') or target.startswith('https://')):
            if search_engine:
                try:
                    results = search_engine.search(target, max_results=1)
                    if results:
                        target = results[0].url
                    else:
                        return {
                            'success': False,
                            'error': 'No results found to read',
                            'voice_response': f'Tidak ditemukan hasil untuk dibaca: "{intent.target}".' if intent.language == Language.INDONESIAN else f'No results found to read: "{intent.target}".'
                        }
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'voice_response': f'Gagal mencari: {str(e)}' if intent.language == Language.INDONESIAN else f'Search failed: {str(e)}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Search engine not available for URL lookup',
                    'voice_response': 'Tidak dapat mencari URL.' if intent.language == Language.INDONESIAN else 'Cannot search for URL.'
                }
        
        try:
            content = content_extractor.extract_from_url(target)
            
            if not content.text:
                return {
                    'success': False,
                    'error': 'No readable content found',
                    'voice_response': 'Tidak ditemukan konten yang dapat dibaca.' if intent.language == Language.INDONESIAN else 'No readable content found.'
                }
            
            # Generate voice-friendly summary
            voice_summary = content.to_voice_summary(max_length=500)
            
            return {
                'success': True,
                'command': 'read',
                'url': target,
                'content': content.to_dict(),
                'voice_response': voice_summary
            }
            
        except Exception as e:
            logger.error(f"Read error: {e}")
            return {
                'success': False,
                'error': str(e),
                'voice_response': f'Gagal membaca konten: {str(e)}' if intent.language == Language.INDONESIAN else f'Failed to read content: {str(e)}'
            }
    
    async def _handle_summarize(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle summarize commands"""
        # Similar to read but focus on summary
        read_result = await self._handle_read(intent, search_engine, content_extractor, browser_automation)
        
        if not read_result['success']:
            return read_result
        
        content_dict = read_result['content']
        
        if intent.language == Language.INDONESIAN:
            voice_response = f'Ringkasan dari {content_dict["title"]}: {content_dict["summary"]}'
        else:
            voice_response = f'Summary of {content_dict["title"]}: {content_dict["summary"]}'
        
        return {
            'success': True,
            'command': 'summarize',
            'url': read_result['url'],
            'summary': content_dict['summary'],
            'voice_response': voice_response
        }
    
    async def _handle_extract(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle extract commands"""
        # Extract specific information based on target
        read_result = await self._handle_read(intent, search_engine, content_extractor, browser_automation)
        
        if not read_result['success']:
            return read_result
        
        content_dict = read_result['content']
        
        # Extract key points
        key_points = []
        if content_extractor:
            try:
                key_points = content_extractor.extract_key_points(read_result['url'])
            except Exception as e:
                logger.warning(f"Failed to extract key points: {e}")
        
        if intent.language == Language.INDONESIAN:
            voice_response = f'Poin-poin utama dari {content_dict["title"]}: '
            voice_response += '. '.join(key_points[:3]) + '.'
        else:
            voice_response = f'Key points from {content_dict["title"]}: '
            voice_response += '. '.join(key_points[:3]) + '.'
        
        return {
            'success': True,
            'command': 'extract',
            'url': read_result['url'],
            'key_points': key_points,
            'voice_response': voice_response
        }
    
    async def _handle_navigation(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle navigation commands (back, forward, refresh)"""
        if not browser_automation:
            return {
                'success': False,
                'error': 'Browser automation not available',
                'voice_response': 'Otomasi browser tidak tersedia.' if intent.language == Language.INDONESIAN else 'Browser automation not available.'
            }
        
        try:
            if intent.command == VoiceCommand.BACK:
                await browser_automation.go_back()
                voice_response = 'Kembali ke halaman sebelumnya.' if intent.language == Language.INDONESIAN else 'Going back to previous page.'
            elif intent.command == VoiceCommand.FORWARD:
                await browser_automation.go_forward()
                voice_response = 'Maju ke halaman berikutnya.' if intent.language == Language.INDONESIAN else 'Going forward to next page.'
            elif intent.command == VoiceCommand.REFRESH:
                await browser_automation.refresh()
                voice_response = 'Memuat ulang halaman.' if intent.language == Language.INDONESIAN else 'Refreshing page.'
            
            return {
                'success': True,
                'command': intent.command.value,
                'voice_response': voice_response
            }
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'voice_response': f'Gagal navigasi: {str(e)}' if intent.language == Language.INDONESIAN else f'Navigation failed: {str(e)}'
            }
    
    async def _handle_control(self, intent: VoiceIntent, search_engine, content_extractor, browser_automation) -> Dict[str, Any]:
        """Handle control commands (stop, pause, continue)"""
        if intent.command == VoiceCommand.STOP:
            voice_response = 'Menghentikan operasi.' if intent.language == Language.INDONESIAN else 'Stopping operation.'
        elif intent.command == VoiceCommand.PAUSE:
            voice_response = 'Menjeda operasi.' if intent.language == Language.INDONESIAN else 'Pausing operation.'
        elif intent.command == VoiceCommand.CONTINUE:
            voice_response = 'Melanjutkan operasi.' if intent.language == Language.INDONESIAN else 'Continuing operation.'
        
        return {
            'success': True,
            'command': intent.command.value,
            'voice_response': voice_response
        }
    
    def get_supported_commands(self, language: Optional[Language] = None) -> List[str]:
        """Get list of supported voice commands"""
        language = language or self.config.default_language
        patterns = self.voice_patterns.get(language, {})
        
        commands = []
        for command, pattern_list in patterns.items():
            # Extract example patterns
            for pattern in pattern_list[:1]:  # Take first pattern as example
                # Remove regex syntax for user-friendly display
                example = pattern.replace(r'\s+', ' ').replace('(.+)', '[target]')
                example = example.replace(r'\\', '')
                commands.append(example)
        
        return commands