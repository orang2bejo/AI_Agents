"""Word Handler untuk Office Automation via COM

Module ini menyediakan interface untuk mengotomatisasi Microsoft Word
menggunakan COM (Component Object Model) melalui pywin32.

Fitur yang didukung:
- Membuka/menutup Word dan dokumen
- Manipulasi teks (tulis, ganti, format)
- Heading dan struktur dokumen
- Export ke PDF
- Find and replace operations
"""

import logging
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import time

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    logging.warning("pywin32 not available. Word automation will not work.")

@dataclass
class WordResult:
    """Hasil operasi Word"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WordHandler:
    """Handler untuk Microsoft Word automation"""
    
    def __init__(self, visible: bool = True, auto_save: bool = True):
        """
        Args:
            visible: Apakah Word window terlihat
            auto_save: Auto save document setelah operasi
        """
        if not COM_AVAILABLE:
            raise ImportError("pywin32 required for Word automation")
        
        self.visible = visible
        self.auto_save = auto_save
        self.word_app = None
        self.current_document = None
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize COM
        pythoncom.CoInitialize()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_word()
        pythoncom.CoUninitialize()
    
    def _ensure_word_app(self) -> bool:
        """Ensure Word application is running
        
        Returns:
            True if Word app is available
        """
        try:
            if self.word_app is None:
                self.word_app = win32com.client.Dispatch("Word.Application")
                self.word_app.Visible = self.visible
                self.word_app.DisplayAlerts = 0  # Disable alerts
                self.logger.info("Word application started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Word: {e}")
            return False
    
    async def handle_action(self, action: str, parameters: Dict[str, Any], 
                          context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Main handler untuk Word actions
        
        Args:
            action: Action to perform
            parameters: Action parameters
            context: Execution context
            **kwargs: Additional arguments
            
        Returns:
            Result dictionary
        """
        try:
            # Map actions to methods
            action_map = {
                "open_word": self.open_word,
                "open_document": self.open_document,
                "create_document": self.create_document,
                "write_text": self.write_text,
                "replace_all": self.replace_all,
                "insert_heading": self.insert_heading,
                "format_text": self.format_text,
                "save_as_pdf": self.save_as_pdf,
                "save_as": self.save_document_as,
                "save": self.save_document,
                "close": self.close_document
            }
            
            if action not in action_map:
                return {
                    "message": f"Unsupported action: {action}",
                    "data": {"success": False}
                }
            
            # Execute action
            result = action_map[action](**parameters)
            
            if result.success:
                return {
                    "message": result.message,
                    "data": result.data or {"success": True}
                }
            else:
                return {
                    "message": f"Failed: {result.error or result.message}",
                    "data": {"success": False}
                }
                
        except Exception as e:
            self.logger.error(f"Word action failed: {e}")
            return {
                "message": f"Word operation failed: {str(e)}",
                "data": {"success": False}
            }
    
    def open_word(self) -> WordResult:
        """Buka Word application
        
        Returns:
            WordResult
        """
        if self._ensure_word_app():
            return WordResult(
                success=True,
                message="Word berhasil dibuka",
                data={"app_visible": self.visible}
            )
        else:
            return WordResult(
                success=False,
                message="Gagal membuka Word",
                error="Word application not available"
            )
    
    def open_document(self, filename: str) -> WordResult:
        """Buka dokumen Word
        
        Args:
            filename: Path ke file Word
            
        Returns:
            WordResult
        """
        if not self._ensure_word_app():
            return WordResult(success=False, message="Word not available")
        
        try:
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            if not os.path.exists(filename):
                return WordResult(
                    success=False,
                    message=f"File tidak ditemukan: {filename}"
                )
            
            self.current_document = self.word_app.Documents.Open(filename)
            
            return WordResult(
                success=True,
                message=f"Dokumen {os.path.basename(filename)} berhasil dibuka",
                data={
                    "filename": filename,
                    "word_count": self.current_document.Words.Count,
                    "page_count": self.current_document.Range().Information(4)  # wdNumberOfPagesInDocument
                }
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message=f"Gagal membuka dokumen: {filename}",
                error=str(e)
            )
    
    def create_document(self) -> WordResult:
        """Buat dokumen baru
        
        Returns:
            WordResult
        """
        if not self._ensure_word_app():
            return WordResult(success=False, message="Word not available")
        
        try:
            self.current_document = self.word_app.Documents.Add()
            
            return WordResult(
                success=True,
                message="Dokumen baru berhasil dibuat"
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal membuat dokumen baru",
                error=str(e)
            )
    
    def write_text(self, text: str, position: str = "end") -> WordResult:
        """Tulis teks ke dokumen
        
        Args:
            text: Teks yang akan ditulis
            position: Posisi penulisan ('start', 'end', 'cursor')
            
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            if position == "start":
                # Insert at beginning
                range_obj = self.current_document.Range(0, 0)
            elif position == "end":
                # Insert at end
                range_obj = self.current_document.Range()
                range_obj.Collapse(0)  # wdCollapseEnd
            else:  # cursor position
                range_obj = self.word_app.Selection.Range
            
            range_obj.Text = text
            
            if self.auto_save:
                self.current_document.Save()
            
            return WordResult(
                success=True,
                message=f"Teks berhasil ditulis di posisi {position}",
                data={"text": text, "position": position}
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal menulis teks",
                error=str(e)
            )
    
    def replace_all(self, find: str, replace: str) -> WordResult:
        """Ganti semua kemunculan teks
        
        Args:
            find: Teks yang dicari
            replace: Teks pengganti
            
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            # Use Find and Replace
            find_obj = self.current_document.Content.Find
            find_obj.ClearFormatting()
            find_obj.Replacement.ClearFormatting()
            
            find_obj.Text = find
            find_obj.Replacement.Text = replace
            
            # Execute replace all
            count = 0
            while find_obj.Execute(Replace=2):  # wdReplaceAll
                count += 1
                if count > 1000:  # Safety limit
                    break
            
            if self.auto_save:
                self.current_document.Save()
            
            return WordResult(
                success=True,
                message=f"Berhasil mengganti '{find}' dengan '{replace}'",
                data={"find": find, "replace": replace, "replacements": count}
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message=f"Gagal mengganti '{find}' dengan '{replace}'",
                error=str(e)
            )
    
    def insert_heading(self, text: str, level: int = 1) -> WordResult:
        """Insert heading
        
        Args:
            text: Teks heading
            level: Level heading (1-6)
            
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            # Validate level
            if not 1 <= level <= 6:
                level = 1
            
            # Insert at current position
            selection = self.word_app.Selection
            selection.TypeText(text)
            
            # Apply heading style
            heading_style = f"Heading {level}"
            selection.Style = heading_style
            
            # Move to next line
            selection.TypeParagraph()
            
            if self.auto_save:
                self.current_document.Save()
            
            return WordResult(
                success=True,
                message=f"Heading level {level} '{text}' berhasil ditambahkan",
                data={"text": text, "level": level}
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal menambahkan heading",
                error=str(e)
            )
    
    def format_text(self, text: str, format_type: str) -> WordResult:
        """Format teks tertentu
        
        Args:
            text: Teks yang akan diformat
            format_type: Jenis format ('bold', 'italic', 'underline')
            
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            # Find the text
            find_obj = self.current_document.Content.Find
            find_obj.ClearFormatting()
            find_obj.Text = text
            
            count = 0
            while find_obj.Execute():
                # Apply formatting
                if format_type == "bold":
                    find_obj.Parent.Bold = True
                elif format_type == "italic":
                    find_obj.Parent.Italic = True
                elif format_type == "underline":
                    find_obj.Parent.Underline = True
                
                count += 1
                if count > 100:  # Safety limit
                    break
            
            if self.auto_save:
                self.current_document.Save()
            
            return WordResult(
                success=True,
                message=f"Format {format_type} diterapkan pada '{text}' ({count} kemunculan)",
                data={"text": text, "format": format_type, "count": count}
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message=f"Gagal memformat teks '{text}'",
                error=str(e)
            )
    
    def save_as_pdf(self, filename: Optional[str] = None) -> WordResult:
        """Export dokumen ke PDF
        
        Args:
            filename: Nama file PDF (optional)
            
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            if not filename:
                # Generate filename based on document name
                doc_name = self.current_document.Name
                if doc_name.lower().endswith(('.docx', '.doc')):
                    filename = doc_name.rsplit('.', 1)[0] + '.pdf'
                else:
                    filename = doc_name + '.pdf'
            
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            # Ensure .pdf extension
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            # Export as PDF
            self.current_document.ExportAsFixedFormat(
                OutputFileName=filename,
                ExportFormat=17,  # wdExportFormatPDF
                OpenAfterExport=False,
                OptimizeFor=0,  # wdExportOptimizeForPrint
                BitmapMissingFonts=True,
                DocStructureTags=True,
                CreateBookmarks=0,  # wdExportCreateNoBookmarks
                UseDocumentTitle=True
            )
            
            return WordResult(
                success=True,
                message=f"Dokumen berhasil diekspor ke PDF: {os.path.basename(filename)}",
                data={"filename": filename}
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal mengekspor ke PDF",
                error=str(e)
            )
    
    def save_document(self) -> WordResult:
        """Simpan dokumen
        
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            self.current_document.Save()
            
            return WordResult(
                success=True,
                message="Dokumen berhasil disimpan"
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal menyimpan dokumen",
                error=str(e)
            )
    
    def save_document_as(self, filename: str) -> WordResult:
        """Simpan dokumen dengan nama baru
        
        Args:
            filename: New filename
            
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            # Ensure .docx extension
            if not filename.lower().endswith(('.docx', '.doc')):
                filename += '.docx'
            
            self.current_document.SaveAs2(filename)
            
            return WordResult(
                success=True,
                message=f"Dokumen berhasil disimpan sebagai {os.path.basename(filename)}",
                data={"filename": filename}
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message=f"Gagal menyimpan dokumen sebagai {filename}",
                error=str(e)
            )
    
    def close_document(self) -> WordResult:
        """Tutup dokumen
        
        Returns:
            WordResult
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            self.current_document.Close(SaveChanges=-1 if self.auto_save else 0)  # wdSaveChanges or wdDoNotSaveChanges
            self.current_document = None
            
            return WordResult(
                success=True,
                message="Dokumen berhasil ditutup"
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal menutup dokumen",
                error=str(e)
            )
    
    def get_document_info(self) -> WordResult:
        """Get informasi dokumen
        
        Returns:
            WordResult with document info
        """
        if not self.current_document:
            return WordResult(success=False, message="No document open")
        
        try:
            info = {
                "name": self.current_document.Name,
                "path": self.current_document.FullName,
                "word_count": self.current_document.Words.Count,
                "character_count": self.current_document.Characters.Count,
                "paragraph_count": self.current_document.Paragraphs.Count,
                "page_count": self.current_document.Range().Information(4),  # wdNumberOfPagesInDocument
                "saved": self.current_document.Saved
            }
            
            return WordResult(
                success=True,
                message="Informasi dokumen berhasil diambil",
                data=info
            )
            
        except Exception as e:
            return WordResult(
                success=False,
                message="Gagal mengambil informasi dokumen",
                error=str(e)
            )
    
    def close_word(self):
        """Tutup Word application"""
        try:
            if self.current_document:
                self.current_document.Close(SaveChanges=-1 if self.auto_save else 0)
            
            if self.word_app:
                self.word_app.Quit()
                self.word_app = None
            
            self.current_document = None
            
            self.logger.info("Word application closed")
            
        except Exception as e:
            self.logger.error(f"Error closing Word: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_word_handler():
        """Test Word handler functionality"""
        
        if not COM_AVAILABLE:
            print("pywin32 not available. Cannot test Word handler.")
            return
        
        print("=== Word Handler Test ===")
        
        with WordHandler(visible=True) as word:
            # Test opening Word
            result = word.open_word()
            print(f"Open Word: {result.message}")
            
            # Test creating document
            result = word.create_document()
            print(f"Create Document: {result.message}")
            
            # Test writing text
            result = word.write_text("Laporan Bulanan\n\n", "start")
            print(f"Write Text: {result.message}")
            
            # Test inserting heading
            result = word.insert_heading("Pendahuluan", 1)
            print(f"Insert Heading: {result.message}")
            
            # Test writing more text
            result = word.write_text("Ini adalah contoh dokumen yang dibuat secara otomatis menggunakan Python dan COM.\n\n")
            print(f"Write Content: {result.message}")
            
            # Test replace all
            result = word.replace_all("contoh", "sampel")
            print(f"Replace All: {result.message}")
            
            # Test via handler interface
            handler_result = await word.handle_action(
                "insert_heading", 
                {"text": "Kesimpulan", "level": 2}, 
                {}
            )
            print(f"Handler Insert Heading: {handler_result['message']}")
            
            # Test document info
            result = word.get_document_info()
            print(f"Document Info: {result.message}")
            if result.success:
                print(f"  Words: {result.data['word_count']}")
                print(f"  Pages: {result.data['page_count']}")
    
    # Run test
    asyncio.run(test_word_handler())