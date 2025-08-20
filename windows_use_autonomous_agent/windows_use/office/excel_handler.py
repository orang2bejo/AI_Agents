"""Excel Handler untuk Office Automation via COM

Module ini menyediakan interface untuk mengotomatisasi Microsoft Excel
menggunakan COM (Component Object Model) melalui pywin32.

Fitur yang didukung:
- Membuka/menutup Excel dan workbook
- Manipulasi worksheet (tambah, hapus, rename)
- Operasi cell (tulis, baca, format)
- Chart dan grafik
- Export ke berbagai format
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
    logging.warning("pywin32 not available. Excel automation will not work.")

@dataclass
class ExcelResult:
    """Hasil operasi Excel"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ExcelHandler:
    """Handler untuk Microsoft Excel automation"""
    
    def __init__(self, visible: bool = True, auto_save: bool = True):
        """
        Args:
            visible: Apakah Excel window terlihat
            auto_save: Auto save workbook setelah operasi
        """
        if not COM_AVAILABLE:
            raise ImportError("pywin32 required for Excel automation")
        
        self.visible = visible
        self.auto_save = auto_save
        self.excel_app = None
        self.current_workbook = None
        self.current_worksheet = None
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize COM
        pythoncom.CoInitialize()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_excel()
        pythoncom.CoUninitialize()
    
    def _ensure_excel_app(self) -> bool:
        """Ensure Excel application is running
        
        Returns:
            True if Excel app is available
        """
        try:
            if self.excel_app is None:
                self.excel_app = win32com.client.Dispatch("Excel.Application")
                self.excel_app.Visible = self.visible
                self.excel_app.DisplayAlerts = False  # Disable alerts
                self.logger.info("Excel application started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Excel: {e}")
            return False
    
    async def handle_action(self, action: str, parameters: Dict[str, Any], 
                          context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Main handler untuk Excel actions
        
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
                "open_excel": self.open_excel,
                "open_workbook": self.open_workbook,
                "create_workbook": self.create_workbook,
                "add_sheet": self.add_worksheet,
                "delete_sheet": self.delete_worksheet,
                "write_cell": self.write_cell,
                "read_cell": self.read_cell,
                "format_column": self.format_column,
                "insert_chart": self.insert_chart,
                "save_as": self.save_workbook_as,
                "save": self.save_workbook,
                "close": self.close_workbook
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
            self.logger.error(f"Excel action failed: {e}")
            return {
                "message": f"Excel operation failed: {str(e)}",
                "data": {"success": False}
            }
    
    def open_excel(self) -> ExcelResult:
        """Buka Excel application
        
        Returns:
            ExcelResult
        """
        if self._ensure_excel_app():
            return ExcelResult(
                success=True,
                message="Excel berhasil dibuka",
                data={"app_visible": self.visible}
            )
        else:
            return ExcelResult(
                success=False,
                message="Gagal membuka Excel",
                error="Excel application not available"
            )
    
    def open_workbook(self, filename: str) -> ExcelResult:
        """Buka workbook Excel
        
        Args:
            filename: Path ke file Excel
            
        Returns:
            ExcelResult
        """
        if not self._ensure_excel_app():
            return ExcelResult(success=False, message="Excel not available")
        
        try:
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            if not os.path.exists(filename):
                return ExcelResult(
                    success=False,
                    message=f"File tidak ditemukan: {filename}"
                )
            
            self.current_workbook = self.excel_app.Workbooks.Open(filename)
            self.current_worksheet = self.current_workbook.ActiveSheet
            
            return ExcelResult(
                success=True,
                message=f"Workbook {os.path.basename(filename)} berhasil dibuka",
                data={
                    "filename": filename,
                    "sheets": [sheet.Name for sheet in self.current_workbook.Sheets]
                }
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message=f"Gagal membuka workbook: {filename}",
                error=str(e)
            )
    
    def create_workbook(self) -> ExcelResult:
        """Buat workbook baru
        
        Returns:
            ExcelResult
        """
        if not self._ensure_excel_app():
            return ExcelResult(success=False, message="Excel not available")
        
        try:
            self.current_workbook = self.excel_app.Workbooks.Add()
            self.current_worksheet = self.current_workbook.ActiveSheet
            
            return ExcelResult(
                success=True,
                message="Workbook baru berhasil dibuat",
                data={"sheets": ["Sheet1"]}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message="Gagal membuat workbook baru",
                error=str(e)
            )
    
    def add_worksheet(self, name: Optional[str] = None) -> ExcelResult:
        """Tambah worksheet baru
        
        Args:
            name: Nama worksheet (optional)
            
        Returns:
            ExcelResult
        """
        if not self.current_workbook:
            return ExcelResult(success=False, message="No workbook open")
        
        try:
            new_sheet = self.current_workbook.Sheets.Add()
            
            if name:
                # Check if name already exists
                existing_names = [sheet.Name for sheet in self.current_workbook.Sheets]
                if name in existing_names:
                    name = f"{name}_{int(time.time())}"
                
                new_sheet.Name = name
            
            sheet_name = new_sheet.Name
            
            return ExcelResult(
                success=True,
                message=f"Sheet '{sheet_name}' berhasil ditambahkan",
                data={"sheet_name": sheet_name}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message="Gagal menambah worksheet",
                error=str(e)
            )
    
    def delete_worksheet(self, name: Optional[str] = None) -> ExcelResult:
        """Hapus worksheet
        
        Args:
            name: Nama worksheet to delete (default: active sheet)
            
        Returns:
            ExcelResult
        """
        if not self.current_workbook:
            return ExcelResult(success=False, message="No workbook open")
        
        try:
            if name:
                # Find sheet by name
                target_sheet = None
                for sheet in self.current_workbook.Sheets:
                    if sheet.Name == name:
                        target_sheet = sheet
                        break
                
                if not target_sheet:
                    return ExcelResult(
                        success=False,
                        message=f"Sheet '{name}' tidak ditemukan"
                    )
            else:
                target_sheet = self.current_worksheet
                name = target_sheet.Name
            
            # Check if it's the last sheet
            if self.current_workbook.Sheets.Count <= 1:
                return ExcelResult(
                    success=False,
                    message="Tidak bisa menghapus sheet terakhir"
                )
            
            target_sheet.Delete()
            
            # Update current worksheet if deleted
            if target_sheet == self.current_worksheet:
                self.current_worksheet = self.current_workbook.ActiveSheet
            
            return ExcelResult(
                success=True,
                message=f"Sheet '{name}' berhasil dihapus"
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message="Gagal menghapus worksheet",
                error=str(e)
            )
    
    def write_cell(self, cell: str, value: Union[str, int, float]) -> ExcelResult:
        """Tulis nilai ke cell
        
        Args:
            cell: Cell address (e.g., 'A1', 'B5')
            value: Value to write
            
        Returns:
            ExcelResult
        """
        if not self.current_worksheet:
            return ExcelResult(success=False, message="No worksheet active")
        
        try:
            self.current_worksheet.Range(cell).Value = value
            
            if self.auto_save and self.current_workbook:
                self.current_workbook.Save()
            
            return ExcelResult(
                success=True,
                message=f"Cell {cell} berhasil diisi dengan '{value}'",
                data={"cell": cell, "value": value}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message=f"Gagal menulis ke cell {cell}",
                error=str(e)
            )
    
    def read_cell(self, cell: str) -> ExcelResult:
        """Baca nilai dari cell
        
        Args:
            cell: Cell address (e.g., 'A1', 'B5')
            
        Returns:
            ExcelResult with cell value
        """
        if not self.current_worksheet:
            return ExcelResult(success=False, message="No worksheet active")
        
        try:
            value = self.current_worksheet.Range(cell).Value
            
            return ExcelResult(
                success=True,
                message=f"Cell {cell} berisi: {value}",
                data={"cell": cell, "value": value}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message=f"Gagal membaca cell {cell}",
                error=str(e)
            )
    
    def format_column(self, column: str, format_type: str) -> ExcelResult:
        """Format kolom
        
        Args:
            column: Column letter (e.g., 'A', 'B')
            format_type: Format type ('currency', 'percent', 'date', 'number')
            
        Returns:
            ExcelResult
        """
        if not self.current_worksheet:
            return ExcelResult(success=False, message="No worksheet active")
        
        try:
            # Format mapping
            format_map = {
                "currency": "_($* #,##0.00_);_($* (#,##0.00);_($* \"-\"??_);_(@_)",
                "percent": "0.00%",
                "date": "dd/mm/yyyy",
                "number": "#,##0.00",
                "text": "@"
            }
            
            if format_type not in format_map:
                return ExcelResult(
                    success=False,
                    message=f"Format type '{format_type}' tidak didukung"
                )
            
            # Apply format to entire column
            column_range = f"{column}:{column}"
            self.current_worksheet.Range(column_range).NumberFormat = format_map[format_type]
            
            if self.auto_save and self.current_workbook:
                self.current_workbook.Save()
            
            return ExcelResult(
                success=True,
                message=f"Kolom {column} berhasil diformat sebagai {format_type}",
                data={"column": column, "format": format_type}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message=f"Gagal memformat kolom {column}",
                error=str(e)
            )
    
    def insert_chart(self, chart_type: str = "column", data_range: Optional[str] = None) -> ExcelResult:
        """Insert chart/grafik
        
        Args:
            chart_type: Type of chart ('column', 'line', 'pie')
            data_range: Data range for chart (e.g., 'A1:B10')
            
        Returns:
            ExcelResult
        """
        if not self.current_worksheet:
            return ExcelResult(success=False, message="No worksheet active")
        
        try:
            # Default data range if not provided
            if not data_range:
                # Try to find data automatically
                used_range = self.current_worksheet.UsedRange
                if used_range.Rows.Count > 1 and used_range.Columns.Count > 1:
                    data_range = used_range.Address
                else:
                    data_range = "A1:B10"  # Default range
            
            # Chart type mapping
            chart_type_map = {
                "column": 51,  # xlColumnClustered
                "line": 4,     # xlLine
                "pie": 5       # xlPie
            }
            
            chart_type_code = chart_type_map.get(chart_type, 51)
            
            # Create chart
            chart_objects = self.current_worksheet.ChartObjects()
            chart = chart_objects.Add(100, 50, 400, 300)  # Left, Top, Width, Height
            
            chart.Chart.SetSourceData(self.current_worksheet.Range(data_range))
            chart.Chart.ChartType = chart_type_code
            
            if self.auto_save and self.current_workbook:
                self.current_workbook.Save()
            
            return ExcelResult(
                success=True,
                message=f"Chart {chart_type} berhasil ditambahkan",
                data={"chart_type": chart_type, "data_range": data_range}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message="Gagal menambahkan chart",
                error=str(e)
            )
    
    def save_workbook(self) -> ExcelResult:
        """Simpan workbook
        
        Returns:
            ExcelResult
        """
        if not self.current_workbook:
            return ExcelResult(success=False, message="No workbook open")
        
        try:
            self.current_workbook.Save()
            
            return ExcelResult(
                success=True,
                message="Workbook berhasil disimpan"
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message="Gagal menyimpan workbook",
                error=str(e)
            )
    
    def save_workbook_as(self, filename: str) -> ExcelResult:
        """Simpan workbook dengan nama baru
        
        Args:
            filename: New filename
            
        Returns:
            ExcelResult
        """
        if not self.current_workbook:
            return ExcelResult(success=False, message="No workbook open")
        
        try:
            # Convert to absolute path
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            
            # Ensure .xlsx extension
            if not filename.lower().endswith(('.xlsx', '.xls')):
                filename += '.xlsx'
            
            self.current_workbook.SaveAs(filename)
            
            return ExcelResult(
                success=True,
                message=f"Workbook berhasil disimpan sebagai {os.path.basename(filename)}",
                data={"filename": filename}
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message=f"Gagal menyimpan workbook sebagai {filename}",
                error=str(e)
            )
    
    def close_workbook(self) -> ExcelResult:
        """Tutup workbook
        
        Returns:
            ExcelResult
        """
        if not self.current_workbook:
            return ExcelResult(success=False, message="No workbook open")
        
        try:
            self.current_workbook.Close(SaveChanges=self.auto_save)
            self.current_workbook = None
            self.current_worksheet = None
            
            return ExcelResult(
                success=True,
                message="Workbook berhasil ditutup"
            )
            
        except Exception as e:
            return ExcelResult(
                success=False,
                message="Gagal menutup workbook",
                error=str(e)
            )
    
    def close_excel(self):
        """Tutup Excel application"""
        try:
            if self.current_workbook:
                self.current_workbook.Close(SaveChanges=self.auto_save)
            
            if self.excel_app:
                self.excel_app.Quit()
                self.excel_app = None
            
            self.current_workbook = None
            self.current_worksheet = None
            
            self.logger.info("Excel application closed")
            
        except Exception as e:
            self.logger.error(f"Error closing Excel: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_excel_handler():
        """Test Excel handler functionality"""
        
        if not COM_AVAILABLE:
            print("pywin32 not available. Cannot test Excel handler.")
            return
        
        print("=== Excel Handler Test ===")
        
        with ExcelHandler(visible=True) as excel:
            # Test opening Excel
            result = excel.open_excel()
            print(f"Open Excel: {result.message}")
            
            # Test creating workbook
            result = excel.create_workbook()
            print(f"Create Workbook: {result.message}")
            
            # Test writing to cell
            result = excel.write_cell("A1", "Total Pendapatan")
            print(f"Write Cell: {result.message}")
            
            # Test adding worksheet
            result = excel.add_worksheet("Laporan Q3")
            print(f"Add Sheet: {result.message}")
            
            # Test formatting
            result = excel.format_column("B", "currency")
            print(f"Format Column: {result.message}")
            
            # Test via handler interface
            handler_result = await excel.handle_action(
                "write_cell", 
                {"cell": "B1", "value": 1000000}, 
                {}
            )
            print(f"Handler Write: {handler_result['message']}")
    
    # Run test
    asyncio.run(test_excel_handler())