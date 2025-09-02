"""PowerPoint Handler untuk Office Automation via COM

Module ini menyediakan interface untuk mengotomatisasi Microsoft PowerPoint
menggunakan COM (Component Object Model) melalui pywin32.

Fitur yang didukung:
- Membuka/menutup PowerPoint dan presentasi
- Manipulasi slide (tambah, hapus, edit)
- Edit konten slide (judul, teks, gambar)
- Export ke PDF
- Template dan layout management
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
    logging.warning("pywin32 not available. PowerPoint automation will not work.")

@dataclass
class PowerPointResult:
    """Hasil operasi PowerPoint"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PowerPointHandler:
    """Handler untuk Microsoft PowerPoint automation"""
    
    def __init__(self, visible: bool = True, auto_save: bool = True):
        """
        Args:
            visible: Apakah PowerPoint window terlihat
            auto_save: Auto save presentation setelah operasi
        """
        if not COM_AVAILABLE:
            raise ImportError("pywin32 required for PowerPoint automation")
        
        self.visible = visible
        self.auto_save = auto_save
        self.ppt_app = None
        self.current_presentation = None
        self.current_slide = None
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize COM
        pythoncom.CoInitialize()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_powerpoint()
        pythoncom.CoUninitialize()
    
    def _ensure_ppt_app(self) -> bool:
        """Ensure PowerPoint application is running
        
        Returns:
            True if PowerPoint app is available
        """
        try:
            if self.ppt_app is None:
                self.ppt_app = win32com.client.Dispatch("PowerPoint.Application")
                if self.visible:
                    self.ppt_app.Visible = True
                self.logger.info("PowerPoint application started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start PowerPoint: {e}")
            return False
    
    async def handle_action(self, action: str, parameters: Dict[str, Any], 
                          context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Main handler untuk PowerPoint actions
        
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
                "open_powerpoint": self.open_powerpoint,
                "open_presentation": self.open_presentation,
                "create_presentation": self.create_presentation,
                "add_slide": self.add_slide,
                "delete_slide": self.delete_slide,
                "edit_title": self.edit_slide_title,
                "edit_content": self.edit_slide_content,
                "insert_image": self.insert_image,
                "export_pdf": self.export_to_pdf,
                "save_as": self.save_presentation_as,
                "save": self.save_presentation,
                "close": self.close_presentation
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
            self.logger.error(f"PowerPoint action failed: {e}")
            return {
                "message": f"PowerPoint operation failed: {str(e)}",
                "data": {"success": False}
            }
    
    def open_powerpoint(self) -> PowerPointResult:
        """Buka PowerPoint application
        
        Returns:
            PowerPointResult
        """
        if self._ensure_ppt_app():
            return PowerPointResult(
                success=True,
                message="PowerPoint berhasil dibuka",
                data={"app_visible": self.visible}
            )
        else:
            return PowerPointResult(
                success=False,
                message="Gagal membuka PowerPoint",
                error="PowerPoint application not available"
            )
    
    def open_presentation(self, filename: str) -> PowerPointResult:
        """Buka presentasi PowerPoint
        
        Args:
            filename: Path ke file PowerPoint
            
        Returns:
            PowerPointResult
        """
        if not self._ensure_ppt_app():
            return PowerPointResult(success=False, message="PowerPoint not available")
        
        try:
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            if not os.path.exists(filename):
                return PowerPointResult(
                    success=False,
                    message=f"File tidak ditemukan: {filename}"
                )
            
            self.current_presentation = self.ppt_app.Presentations.Open(filename)
            
            # Set current slide to first slide
            if self.current_presentation.Slides.Count > 0:
                self.current_slide = self.current_presentation.Slides(1)
            
            return PowerPointResult(
                success=True,
                message=f"Presentasi {os.path.basename(filename)} berhasil dibuka",
                data={
                    "filename": filename,
                    "slide_count": self.current_presentation.Slides.Count
                }
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message=f"Gagal membuka presentasi: {filename}",
                error=str(e)
            )
    
    def create_presentation(self, template: Optional[str] = None) -> PowerPointResult:
        """Buat presentasi baru
        
        Args:
            template: Path ke template (optional)
            
        Returns:
            PowerPointResult
        """
        if not self._ensure_ppt_app():
            return PowerPointResult(success=False, message="PowerPoint not available")
        
        try:
            if template and os.path.exists(template):
                # Create from template
                self.current_presentation = self.ppt_app.Presentations.Open(template)
            else:
                # Create blank presentation
                self.current_presentation = self.ppt_app.Presentations.Add()
            
            # Set current slide to first slide
            if self.current_presentation.Slides.Count > 0:
                self.current_slide = self.current_presentation.Slides(1)
            
            return PowerPointResult(
                success=True,
                message="Presentasi baru berhasil dibuat",
                data={"slide_count": self.current_presentation.Slides.Count}
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal membuat presentasi baru",
                error=str(e)
            )
    
    def add_slide(self, layout: str = "title_content", position: Optional[int] = None) -> PowerPointResult:
        """Tambah slide baru
        
        Args:
            layout: Layout slide ('title_only', 'title_content', 'blank', 'title_slide')
            position: Posisi slide (default: di akhir)
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            # Layout mapping
            layout_map = {
                "title_slide": 1,      # ppLayoutTitle
                "title_content": 2,    # ppLayoutText
                "title_only": 5,       # ppLayoutTitleOnly
                "blank": 12,           # ppLayoutBlank
                "two_content": 3       # ppLayoutTwoColumnText
            }
            
            layout_id = layout_map.get(layout, 2)  # Default to title_content
            
            if position is None:
                position = self.current_presentation.Slides.Count + 1
            
            # Add slide
            new_slide = self.current_presentation.Slides.Add(position, layout_id)
            self.current_slide = new_slide
            
            if self.auto_save:
                self.current_presentation.Save()
            
            return PowerPointResult(
                success=True,
                message=f"Slide baru berhasil ditambahkan di posisi {position}",
                data={
                    "slide_number": position,
                    "layout": layout,
                    "total_slides": self.current_presentation.Slides.Count
                }
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal menambah slide",
                error=str(e)
            )
    
    def delete_slide(self, slide_number: Optional[int] = None) -> PowerPointResult:
        """Hapus slide
        
        Args:
            slide_number: Nomor slide yang akan dihapus (default: current slide)
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            if slide_number is None:
                if not self.current_slide:
                    return PowerPointResult(success=False, message="No current slide")
                target_slide = self.current_slide
                slide_number = target_slide.SlideIndex
            else:
                if slide_number < 1 or slide_number > self.current_presentation.Slides.Count:
                    return PowerPointResult(
                        success=False,
                        message=f"Slide number {slide_number} tidak valid"
                    )
                target_slide = self.current_presentation.Slides(slide_number)
            
            # Check if it's the last slide
            if self.current_presentation.Slides.Count <= 1:
                return PowerPointResult(
                    success=False,
                    message="Tidak bisa menghapus slide terakhir"
                )
            
            target_slide.Delete()
            
            # Update current slide
            if self.current_presentation.Slides.Count > 0:
                new_index = min(slide_number, self.current_presentation.Slides.Count)
                self.current_slide = self.current_presentation.Slides(new_index)
            else:
                self.current_slide = None
            
            if self.auto_save:
                self.current_presentation.Save()
            
            return PowerPointResult(
                success=True,
                message=f"Slide {slide_number} berhasil dihapus",
                data={"deleted_slide": slide_number}
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal menghapus slide",
                error=str(e)
            )
    
    def edit_slide_title(self, title: str, slide_number: Optional[int] = None) -> PowerPointResult:
        """Edit judul slide
        
        Args:
            title: Judul baru
            slide_number: Nomor slide (default: current slide)
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            if slide_number is None:
                target_slide = self.current_slide
            else:
                if slide_number < 1 or slide_number > self.current_presentation.Slides.Count:
                    return PowerPointResult(
                        success=False,
                        message=f"Slide number {slide_number} tidak valid"
                    )
                target_slide = self.current_presentation.Slides(slide_number)
            
            if not target_slide:
                return PowerPointResult(success=False, message="No slide selected")
            
            # Find title placeholder
            title_shape = None
            for shape in target_slide.Shapes:
                if shape.Type == 14:  # msoPlaceholder
                    if shape.PlaceholderFormat.Type in [1, 3]:  # ppPlaceholderTitle or ppPlaceholderCenterTitle
                        title_shape = shape
                        break
            
            if title_shape:
                title_shape.TextFrame.TextRange.Text = title
            else:
                # Add title text box if no placeholder found
                title_shape = target_slide.Shapes.AddTextbox(
                    1,  # msoTextOrientationHorizontal
                    50, 50, 600, 100  # Left, Top, Width, Height
                )
                title_shape.TextFrame.TextRange.Text = title
                title_shape.TextFrame.TextRange.Font.Size = 32
                title_shape.TextFrame.TextRange.Font.Bold = True
            
            if self.auto_save:
                self.current_presentation.Save()
            
            return PowerPointResult(
                success=True,
                message=f"Judul slide berhasil diubah menjadi '{title}'",
                data={"title": title, "slide_number": target_slide.SlideIndex}
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal mengubah judul slide",
                error=str(e)
            )
    
    def edit_slide_content(self, content: str, slide_number: Optional[int] = None) -> PowerPointResult:
        """Edit konten slide
        
        Args:
            content: Konten baru
            slide_number: Nomor slide (default: current slide)
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            if slide_number is None:
                target_slide = self.current_slide
            else:
                if slide_number < 1 or slide_number > self.current_presentation.Slides.Count:
                    return PowerPointResult(
                        success=False,
                        message=f"Slide number {slide_number} tidak valid"
                    )
                target_slide = self.current_presentation.Slides(slide_number)
            
            if not target_slide:
                return PowerPointResult(success=False, message="No slide selected")
            
            # Find content placeholder
            content_shape = None
            for shape in target_slide.Shapes:
                if shape.Type == 14:  # msoPlaceholder
                    if shape.PlaceholderFormat.Type in [2, 7]:  # ppPlaceholderBody or ppPlaceholderObject
                        content_shape = shape
                        break
            
            if content_shape:
                content_shape.TextFrame.TextRange.Text = content
            else:
                # Add content text box if no placeholder found
                content_shape = target_slide.Shapes.AddTextbox(
                    1,  # msoTextOrientationHorizontal
                    50, 150, 600, 400  # Left, Top, Width, Height
                )
                content_shape.TextFrame.TextRange.Text = content
                content_shape.TextFrame.TextRange.Font.Size = 18
            
            if self.auto_save:
                self.current_presentation.Save()
            
            return PowerPointResult(
                success=True,
                message=f"Konten slide berhasil diubah",
                data={"content": content[:50] + "...", "slide_number": target_slide.SlideIndex}
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal mengubah konten slide",
                error=str(e)
            )
    
    def insert_image(self, image_path: str, slide_number: Optional[int] = None, 
                    left: int = 100, top: int = 100, width: int = 300, height: int = 200) -> PowerPointResult:
        """Insert gambar ke slide
        
        Args:
            image_path: Path ke file gambar
            slide_number: Nomor slide (default: current slide)
            left, top, width, height: Posisi dan ukuran gambar
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            if not os.path.exists(image_path):
                return PowerPointResult(
                    success=False,
                    message=f"File gambar tidak ditemukan: {image_path}"
                )
            
            if slide_number is None:
                target_slide = self.current_slide
            else:
                if slide_number < 1 or slide_number > self.current_presentation.Slides.Count:
                    return PowerPointResult(
                        success=False,
                        message=f"Slide number {slide_number} tidak valid"
                    )
                target_slide = self.current_presentation.Slides(slide_number)
            
            if not target_slide:
                return PowerPointResult(success=False, message="No slide selected")
            
            # Insert image
            picture = target_slide.Shapes.AddPicture(
                FileName=os.path.abspath(image_path),
                LinkToFile=False,
                SaveWithDocument=True,
                Left=left,
                Top=top,
                Width=width,
                Height=height
            )
            
            if self.auto_save:
                self.current_presentation.Save()
            
            return PowerPointResult(
                success=True,
                message=f"Gambar berhasil ditambahkan ke slide",
                data={
                    "image_path": image_path,
                    "slide_number": target_slide.SlideIndex,
                    "position": {"left": left, "top": top, "width": width, "height": height}
                }
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal menambahkan gambar",
                error=str(e)
            )
    
    def export_to_pdf(self, filename: Optional[str] = None) -> PowerPointResult:
        """Export presentasi ke PDF
        
        Args:
            filename: Nama file PDF (optional)
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            if not filename:
                # Generate filename based on presentation name
                pres_name = self.current_presentation.Name
                if pres_name.lower().endswith(('.pptx', '.ppt')):
                    filename = pres_name.rsplit('.', 1)[0] + '.pdf'
                else:
                    filename = pres_name + '.pdf'
            
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            # Ensure .pdf extension
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            # Export as PDF
            self.current_presentation.ExportAsFixedFormat(
                Path=filename,
                FixedFormatType=2,  # ppFixedFormatTypePDF
                Intent=1,  # ppFixedFormatIntentPrint
                FrameSlides=False,
                HandoutOrder=1,  # ppPrintHandoutHorizontalFirst
                OutputType=1,  # ppPrintOutputSlides
                PrintHiddenSlides=False,
                PrintRange=None,
                RangeType=1,  # ppPrintAll
                SlideShowName="",
                IncludeDocProps=True,
                KeepIRMSettings=True,
                DocStructureTags=True,
                BitmapMissingFonts=True,
                UseDocumentTitle=True
            )
            
            return PowerPointResult(
                success=True,
                message=f"Presentasi berhasil diekspor ke PDF: {os.path.basename(filename)}",
                data={"filename": filename}
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal mengekspor ke PDF",
                error=str(e)
            )
    
    def save_presentation(self) -> PowerPointResult:
        """Simpan presentasi
        
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            self.current_presentation.Save()
            
            return PowerPointResult(
                success=True,
                message="Presentasi berhasil disimpan"
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal menyimpan presentasi",
                error=str(e)
            )
    
    def save_presentation_as(self, filename: str) -> PowerPointResult:
        """Simpan presentasi dengan nama baru
        
        Args:
            filename: New filename
            
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            # Ensure .pptx extension
            if not filename.lower().endswith(('.pptx', '.ppt')):
                filename += '.pptx'
            
            self.current_presentation.SaveAs(filename)
            
            return PowerPointResult(
                success=True,
                message=f"Presentasi berhasil disimpan sebagai {os.path.basename(filename)}",
                data={"filename": filename}
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message=f"Gagal menyimpan presentasi sebagai {filename}",
                error=str(e)
            )
    
    def close_presentation(self) -> PowerPointResult:
        """Tutup presentasi
        
        Returns:
            PowerPointResult
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            self.current_presentation.Close()
            self.current_presentation = None
            self.current_slide = None
            
            return PowerPointResult(
                success=True,
                message="Presentasi berhasil ditutup"
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal menutup presentasi",
                error=str(e)
            )
    
    def get_presentation_info(self) -> PowerPointResult:
        """Get informasi presentasi
        
        Returns:
            PowerPointResult with presentation info
        """
        if not self.current_presentation:
            return PowerPointResult(success=False, message="No presentation open")
        
        try:
            info = {
                "name": self.current_presentation.Name,
                "path": self.current_presentation.FullName,
                "slide_count": self.current_presentation.Slides.Count,
                "current_slide": self.current_slide.SlideIndex if self.current_slide else None,
                "saved": self.current_presentation.Saved
            }
            
            return PowerPointResult(
                success=True,
                message="Informasi presentasi berhasil diambil",
                data=info
            )
            
        except Exception as e:
            return PowerPointResult(
                success=False,
                message="Gagal mengambil informasi presentasi",
                error=str(e)
            )
    
    def close_powerpoint(self):
        """Tutup PowerPoint application"""
        try:
            if self.current_presentation:
                self.current_presentation.Close()
            
            if self.ppt_app:
                self.ppt_app.Quit()
                self.ppt_app = None
            
            self.current_presentation = None
            self.current_slide = None
            
            self.logger.info("PowerPoint application closed")
            
        except Exception as e:
            self.logger.error(f"Error closing PowerPoint: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_powerpoint_handler():
        """Test PowerPoint handler functionality"""
        
        if not COM_AVAILABLE:
            print("pywin32 not available. Cannot test PowerPoint handler.")
            return
        
        print("=== PowerPoint Handler Test ===")
        
        with PowerPointHandler(visible=True) as ppt:
            # Test opening PowerPoint
            result = ppt.open_powerpoint()
            print(f"Open PowerPoint: {result.message}")
            
            # Test creating presentation
            result = ppt.create_presentation()
            print(f"Create Presentation: {result.message}")
            
            # Test editing title
            result = ppt.edit_slide_title("Presentasi Q3 2024")
            print(f"Edit Title: {result.message}")
            
            # Test adding slide
            result = ppt.add_slide("title_content")
            print(f"Add Slide: {result.message}")
            
            # Test editing content
            result = ppt.edit_slide_content("• Poin 1\n• Poin 2\n• Poin 3")
            print(f"Edit Content: {result.message}")
            
            # Test via handler interface
            handler_result = await ppt.handle_action(
                "edit_title", 
                {"title": "Kesimpulan"}, 
                {}
            )
            print(f"Handler Edit Title: {handler_result['message']}")
            
            # Test presentation info
            result = ppt.get_presentation_info()
            print(f"Presentation Info: {result.message}")
            if result.success:
                print(f"  Slides: {result.data['slide_count']}")
                print(f"  Current: {result.data['current_slide']}")
    
    # Run test
    asyncio.run(test_powerpoint_handler())