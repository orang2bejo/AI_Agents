"""Grammar Parser untuk Bahasa Indonesia

Module ini menyediakan parsing grammar untuk perintah bahasa Indonesia
yang dapat dipetakan langsung ke aksi tanpa perlu LLM processing.

Contoh perintah yang didukung:
- Office: "buka excel", "tambah sheet", "hapus slide", "ganti semua X jadi Y"
- System: "buka aplikasi", "tutup jendela", "screenshot"
- File: "buka file", "simpan sebagai", "copy file"
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

class IntentType(Enum):
    """Jenis intent yang didukung"""
    OFFICE_EXCEL = "office_excel"
    OFFICE_WORD = "office_word"
    OFFICE_POWERPOINT = "office_powerpoint"
    SYSTEM_APP = "system_app"
    SYSTEM_WINDOW = "system_window"
    FILE_OPERATION = "file_operation"
    UNKNOWN = "unknown"

@dataclass
class ParsedIntent:
    """Hasil parsing intent"""
    intent_type: IntentType
    action: str
    parameters: Dict[str, Any]
    confidence: float
    original_text: str
    fast_path: bool = True  # Apakah bisa langsung dieksekusi tanpa LLM

class GrammarParserID:
    """Parser grammar untuk bahasa Indonesia"""
    
    def __init__(self):
        self.patterns = self._build_patterns()
        self.synonyms = self._build_synonyms()
        
    def _build_synonyms(self) -> Dict[str, List[str]]:
        """Build synonym dictionary untuk normalisasi"""
        return {
            # Aksi umum
            "buka": ["buka", "jalankan", "start", "mulai", "aktifkan"],
            "tutup": ["tutup", "close", "keluar", "exit", "matikan"],
            "tambah": ["tambah", "buat", "add", "create", "bikin"],
            "hapus": ["hapus", "delete", "remove", "buang", "hilangkan"],
            "ganti": ["ganti", "ubah", "replace", "change", "edit"],
            "simpan": ["simpan", "save", "store"],
            "copy": ["copy", "salin", "duplicate"],
            
            # Aplikasi Office
            "excel": ["excel", "spreadsheet", "lembar kerja"],
            "word": ["word", "dokumen", "document"],
            "powerpoint": ["powerpoint", "ppt", "presentasi", "slide"],
            
            # Elemen Office
            "sheet": ["sheet", "lembar", "tab", "worksheet"],
            "slide": ["slide", "halaman"],
            "cell": ["cell", "sel", "kotak"],
            "chart": ["chart", "grafik", "diagram"],
            
            # File operations
            "file": ["file", "berkas", "dokumen"],
            "folder": ["folder", "direktori", "map"],
        }
    
    def _build_patterns(self) -> Dict[IntentType, List[Tuple[str, str, Dict]]]:
        """Build regex patterns untuk setiap intent type
        
        Returns:
            Dict mapping IntentType ke list of (pattern, action, default_params)
        """
        patterns = {
            IntentType.OFFICE_EXCEL: [
                # Excel operations
                (r"(?:buka|jalankan|start)\s+excel", "open_excel", {}),
                (r"(?:tambah|buat|add)\s+(?:sheet|lembar)(?:\s+['\"]([^'\"]+)['\"])?", "add_sheet", {"name": None}),
                (r"(?:hapus|delete)\s+(?:sheet|lembar)(?:\s+['\"]([^'\"]+)['\"])?", "delete_sheet", {"name": None}),
                (r"(?:tulis|isi|write)\s+(?:cell|sel)\s+([A-Z]+\d+)\s+['\"]([^'\"]+)['\"]?", "write_cell", {"cell": None, "value": None}),
                (r"(?:format|atur)\s+(?:kolom|column)\s+([A-Z]+)\s+(?:sebagai\s+)?(\w+)", "format_column", {"column": None, "format": None}),
                (r"(?:buat|tambah|insert)\s+(?:chart|grafik)", "insert_chart", {}),
                (r"(?:simpan|save)\s+(?:sebagai|as)\s+['\"]([^'\"]+)['\"]?", "save_as", {"filename": None}),
            ],
            
            IntentType.OFFICE_WORD: [
                # Word operations
                (r"(?:buka|jalankan|start)\s+word", "open_word", {}),
                (r"(?:ganti|replace)\s+(?:semua\s+)?['\"]([^'\"]+)['\"]\s+(?:jadi|dengan|to)\s+['\"]([^'\"]+)['\"]?", "replace_all", {"find": None, "replace": None}),
                (r"(?:tambah|insert)\s+(?:judul|heading)\s+['\"]([^'\"]+)['\"]?", "insert_heading", {"text": None}),
                (r"(?:export|simpan)\s+(?:sebagai\s+)?pdf", "save_as_pdf", {}),
                (r"(?:simpan|save)\s+(?:sebagai|as)\s+['\"]([^'\"]+)['\"]?", "save_as", {"filename": None}),
            ],
            
            IntentType.OFFICE_POWERPOINT: [
                # PowerPoint operations
                (r"(?:buka|jalankan|start)\s+(?:powerpoint|ppt)", "open_powerpoint", {}),
                (r"(?:tambah|add)\s+slide", "add_slide", {}),
                (r"(?:edit|ubah)\s+(?:judul|title)\s+['\"]([^'\"]+)['\"]?", "edit_title", {"title": None}),
                (r"(?:export|simpan)\s+(?:sebagai\s+)?pdf", "export_pdf", {}),
                (r"(?:hapus|delete)\s+slide(?:\s+(\d+))?", "delete_slide", {"slide_number": None}),
            ],
            
            IntentType.SYSTEM_APP: [
                # System app operations
                (r"(?:buka|jalankan|start)\s+(?:aplikasi\s+)?['\"]([^'\"]+)['\"]?", "open_app", {"app_name": None}),
                (r"(?:install|pasang)\s+['\"]([^'\"]+)['\"]?", "install_app", {"app_name": None}),
                (r"(?:uninstall|hapus)\s+(?:aplikasi\s+)?['\"]([^'\"]+)['\"]?", "uninstall_app", {"app_name": None}),
            ],
            
            IntentType.SYSTEM_WINDOW: [
                # Window operations
                (r"(?:tutup|close)\s+(?:jendela|window)", "close_window", {}),
                (r"(?:minimize|kecilkan)\s+(?:jendela|window)", "minimize_window", {}),
                (r"(?:maximize|besarkan)\s+(?:jendela|window)", "maximize_window", {}),
                (r"(?:screenshot|tangkap\s+layar)", "screenshot", {}),
            ],
            
            IntentType.FILE_OPERATION: [
                # File operations
                (r"(?:buka|open)\s+(?:file|berkas)\s+['\"]([^'\"]+)['\"]?", "open_file", {"filename": None}),
                (r"(?:copy|salin)\s+(?:file|berkas)\s+['\"]([^'\"]+)['\"]?\s+(?:ke|to)\s+['\"]([^'\"]+)['\"]?", "copy_file", {"source": None, "destination": None}),
                (r"(?:hapus|delete)\s+(?:file|berkas)\s+['\"]([^'\"]+)['\"]?", "delete_file", {"filename": None}),
                (r"(?:buat|create)\s+(?:folder|direktori)\s+['\"]([^'\"]+)['\"]?", "create_folder", {"folder_name": None}),
            ],
        }
        
        return patterns
    
    def normalize_text(self, text: str) -> str:
        """Normalize input text
        
        Args:
            text: Raw input text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Apply synonyms
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Find synonym
            found_synonym = False
            for canonical, synonyms in self.synonyms.items():
                if word in synonyms:
                    normalized_words.append(canonical)
                    found_synonym = True
                    break
            
            if not found_synonym:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def parse(self, text: str) -> ParsedIntent:
        """Parse input text menjadi intent
        
        Args:
            text: Input text dari user
            
        Returns:
            ParsedIntent object
        """
        original_text = text
        normalized_text = self.normalize_text(text)
        
        # Try to match patterns
        for intent_type, pattern_list in self.patterns.items():
            for pattern, action, default_params in pattern_list:
                match = re.search(pattern, normalized_text)
                if match:
                    # Extract parameters dari regex groups
                    parameters = default_params.copy()
                    groups = match.groups()
                    
                    # Map groups ke parameter names berdasarkan action
                    param_mapping = self._get_param_mapping(action)
                    for i, group in enumerate(groups):
                        if i < len(param_mapping) and group is not None:
                            parameters[param_mapping[i]] = group
                    
                    # Calculate confidence berdasarkan match quality
                    confidence = self._calculate_confidence(match, normalized_text)
                    
                    return ParsedIntent(
                        intent_type=intent_type,
                        action=action,
                        parameters=parameters,
                        confidence=confidence,
                        original_text=original_text,
                        fast_path=True
                    )
        
        # No pattern matched
        return ParsedIntent(
            intent_type=IntentType.UNKNOWN,
            action="unknown",
            parameters={},
            confidence=0.0,
            original_text=original_text,
            fast_path=False
        )
    
    def _get_param_mapping(self, action: str) -> List[str]:
        """Get parameter mapping untuk action
        
        Args:
            action: Action name
            
        Returns:
            List parameter names dalam urutan regex groups
        """
        mappings = {
            "add_sheet": ["name"],
            "delete_sheet": ["name"],
            "write_cell": ["cell", "value"],
            "format_column": ["column", "format"],
            "save_as": ["filename"],
            "replace_all": ["find", "replace"],
            "insert_heading": ["text"],
            "edit_title": ["title"],
            "delete_slide": ["slide_number"],
            "open_app": ["app_name"],
            "install_app": ["app_name"],
            "uninstall_app": ["app_name"],
            "open_file": ["filename"],
            "copy_file": ["source", "destination"],
            "delete_file": ["filename"],
            "create_folder": ["folder_name"],
        }
        
        return mappings.get(action, [])
    
    def _calculate_confidence(self, match: re.Match, text: str) -> float:
        """Calculate confidence score untuk match
        
        Args:
            match: Regex match object
            text: Normalized text
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence dari match length ratio
        match_length = len(match.group(0))
        text_length = len(text)
        length_ratio = match_length / text_length if text_length > 0 else 0
        
        # Bonus untuk exact matches
        exact_bonus = 0.2 if match_length == text_length else 0
        
        # Bonus untuk parameter extraction
        param_bonus = 0.1 * len([g for g in match.groups() if g is not None])
        
        confidence = min(1.0, 0.6 + (length_ratio * 0.2) + exact_bonus + param_bonus)
        return confidence
    
    def get_supported_commands(self) -> Dict[str, List[str]]:
        """Get list supported commands untuk help
        
        Returns:
            Dictionary mapping intent types ke example commands
        """
        examples = {
            "Excel": [
                "buka excel",
                "tambah sheet 'Laporan'",
                "hapus sheet 'Data Lama'",
                "tulis cell A1 'Pendapatan'",
                "format kolom B persen",
                "buat chart",
                "simpan sebagai 'laporan.xlsx'"
            ],
            "Word": [
                "buka word",
                "ganti semua 'lama' jadi 'baru'",
                "tambah judul 'Laporan Bulanan'",
                "export pdf",
                "simpan sebagai 'dokumen.docx'"
            ],
            "PowerPoint": [
                "buka powerpoint",
                "tambah slide",
                "edit judul 'Presentasi Q3'",
                "hapus slide 5",
                "export pdf"
            ],
            "System": [
                "buka aplikasi 'notepad'",
                "install '7-zip'",
                "tutup jendela",
                "screenshot"
            ],
            "File": [
                "buka file 'dokumen.txt'",
                "copy file 'source.txt' ke 'backup.txt'",
                "hapus file 'temp.txt'",
                "buat folder 'Project Baru'"
            ]
        }
        
        return examples


# Testing dan example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = GrammarParserID()
    
    # Test cases
    test_commands = [
        "buka excel",
        "tambah sheet 'Laporan Q3'",
        "tulis cell A1 'Total Pendapatan'",
        "ganti semua 'Q2' jadi 'Q3' di word",
        "buka aplikasi notepad",
        "screenshot",
        "copy file 'data.xlsx' ke 'backup.xlsx'",
        "perintah yang tidak dikenal"
    ]
    
    print("=== Grammar Parser Test ===")
    for cmd in test_commands:
        result = parser.parse(cmd)
        print(f"\nInput: {cmd}")
        print(f"Intent: {result.intent_type.value}")
        print(f"Action: {result.action}")
        print(f"Parameters: {result.parameters}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Fast Path: {result.fast_path}")
    
    print("\n=== Supported Commands ===")
    commands = parser.get_supported_commands()
    for category, examples in commands.items():
        print(f"\n{category}:")
        for example in examples:
            print(f"  - {example}")