#!/usr/bin/env python3
"""
📊 Excel Data Processing Cookbook

Contoh praktis untuk mengolah data Excel menggunakan Jarvis AI.
Script ini mendemonstrasikan berbagai operasi data processing yang umum digunakan.

Author: Orangbejo
GitHub: https://github.com/Orangbejo
"""

import asyncio
import os
from pathlib import Path
from windows_use.office import ExcelHandler
from windows_use.observability.logger import setup_logger

logger = setup_logger(__name__)

class ExcelDataProcessor:
    """Processor untuk mengolah data Excel dengan berbagai operasi."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        
    async def process_sales_data(self, input_file: str, output_file: str):
        """
        Mengolah data penjualan dengan operasi:
        - Menghitung total penjualan per produk
        - Membuat pivot table
        - Menambahkan chart
        """
        try:
            logger.info(f"Memproses data penjualan dari {input_file}")
            
            # Buka file Excel
            workbook = await self.excel_handler.open_workbook(input_file)
            worksheet = workbook.ActiveSheet
            
            # Baca data penjualan (asumsi kolom A=Produk, B=Jumlah, C=Harga)
            last_row = worksheet.Cells(worksheet.Rows.Count, 1).End(-4162).Row  # xlUp
            
            # Tambahkan kolom Total (D = B * C)
            worksheet.Cells(1, 4).Value = "Total"
            for row in range(2, last_row + 1):
                formula = f"=B{row}*C{row}"
                worksheet.Cells(row, 4).Formula = formula
            
            # Buat summary di sheet baru
            summary_sheet = workbook.Worksheets.Add()
            summary_sheet.Name = "Summary"
            
            # Header untuk summary
            summary_sheet.Cells(1, 1).Value = "Produk"
            summary_sheet.Cells(1, 2).Value = "Total Penjualan"
            summary_sheet.Cells(1, 3).Value = "Rata-rata Harga"
            
            # Gunakan pivot table untuk summary (simplified version)
            products = {}
            for row in range(2, last_row + 1):
                product = worksheet.Cells(row, 1).Value
                quantity = worksheet.Cells(row, 2).Value or 0
                price = worksheet.Cells(row, 3).Value or 0
                total = quantity * price
                
                if product in products:
                    products[product]['total'] += total
                    products[product]['count'] += 1
                    products[product]['price_sum'] += price
                else:
                    products[product] = {
                        'total': total,
                        'count': 1,
                        'price_sum': price
                    }
            
            # Tulis summary
            row_num = 2
            for product, data in products.items():
                summary_sheet.Cells(row_num, 1).Value = product
                summary_sheet.Cells(row_num, 2).Value = data['total']
                summary_sheet.Cells(row_num, 3).Value = data['price_sum'] / data['count']
                row_num += 1
            
            # Format sebagai tabel
            summary_range = summary_sheet.Range(f"A1:C{row_num-1}")
            summary_range.Select()
            
            # Simpan file
            await self.excel_handler.save_workbook(workbook, output_file)
            logger.info(f"Data berhasil diproses dan disimpan ke {output_file}")
            
        except Exception as e:
            logger.error(f"Error memproses data: {e}")
            raise
    
    async def clean_customer_data(self, input_file: str, output_file: str):
        """
        Membersihkan data customer dengan operasi:
        - Menghapus duplikasi
        - Standardisasi format
        - Validasi email dan phone
        """
        try:
            logger.info(f"Membersihkan data customer dari {input_file}")
            
            workbook = await self.excel_handler.open_workbook(input_file)
            worksheet = workbook.ActiveSheet
            
            last_row = worksheet.Cells(worksheet.Rows.Count, 1).End(-4162).Row
            
            # Asumsi kolom: A=Nama, B=Email, C=Phone, D=Alamat
            cleaned_data = []
            seen_emails = set()
            
            # Header
            headers = []
            for col in range(1, 5):
                headers.append(worksheet.Cells(1, col).Value)
            
            # Proses setiap baris
            for row in range(2, last_row + 1):
                name = str(worksheet.Cells(row, 1).Value or "").strip().title()
                email = str(worksheet.Cells(row, 2).Value or "").strip().lower()
                phone = str(worksheet.Cells(row, 3).Value or "").strip()
                address = str(worksheet.Cells(row, 4).Value or "").strip()
                
                # Skip jika email duplikat atau kosong
                if not email or email in seen_emails:
                    continue
                
                # Validasi email sederhana
                if "@" not in email or "." not in email:
                    continue
                
                # Standardisasi phone (hapus karakter non-digit)
                phone = ''.join(filter(str.isdigit, phone))
                if phone and not phone.startswith('0'):
                    phone = '0' + phone
                
                seen_emails.add(email)
                cleaned_data.append([name, email, phone, address])
            
            # Buat sheet baru untuk data bersih
            clean_sheet = workbook.Worksheets.Add()
            clean_sheet.Name = "Clean_Data"
            
            # Tulis header
            for col, header in enumerate(headers, 1):
                clean_sheet.Cells(1, col).Value = header
            
            # Tulis data bersih
            for row_idx, row_data in enumerate(cleaned_data, 2):
                for col_idx, value in enumerate(row_data, 1):
                    clean_sheet.Cells(row_idx, col_idx).Value = value
            
            # Format sebagai tabel
            if cleaned_data:
                table_range = clean_sheet.Range(f"A1:D{len(cleaned_data)+1}")
                table_range.Select()
            
            await self.excel_handler.save_workbook(workbook, output_file)
            logger.info(f"Data customer berhasil dibersihkan: {len(cleaned_data)} records valid")
            
        except Exception as e:
            logger.error(f"Error membersihkan data: {e}")
            raise
    
    async def generate_monthly_report(self, data_folder: str, output_file: str):
        """
        Menggabungkan multiple file Excel menjadi laporan bulanan.
        """
        try:
            logger.info(f"Membuat laporan bulanan dari folder {data_folder}")
            
            # Buat workbook baru
            workbook = await self.excel_handler.create_workbook()
            summary_sheet = workbook.ActiveSheet
            summary_sheet.Name = "Monthly_Summary"
            
            # Header summary
            summary_sheet.Cells(1, 1).Value = "File"
            summary_sheet.Cells(1, 2).Value = "Total Records"
            summary_sheet.Cells(1, 3).Value = "Total Amount"
            summary_sheet.Cells(1, 4).Value = "Average"
            
            row_num = 2
            grand_total = 0
            total_records = 0
            
            # Proses setiap file Excel di folder
            data_path = Path(data_folder)
            for excel_file in data_path.glob("*.xlsx"):
                if excel_file.name.startswith("~"):  # Skip temporary files
                    continue
                    
                try:
                    file_workbook = await self.excel_handler.open_workbook(str(excel_file))
                    file_worksheet = file_workbook.ActiveSheet
                    
                    # Hitung statistik file
                    last_row = file_worksheet.Cells(file_worksheet.Rows.Count, 1).End(-4162).Row
                    file_records = last_row - 1  # Minus header
                    
                    # Asumsi kolom amount di kolom D
                    file_total = 0
                    for row in range(2, last_row + 1):
                        amount = file_worksheet.Cells(row, 4).Value or 0
                        if isinstance(amount, (int, float)):
                            file_total += amount
                    
                    file_average = file_total / file_records if file_records > 0 else 0
                    
                    # Tulis ke summary
                    summary_sheet.Cells(row_num, 1).Value = excel_file.name
                    summary_sheet.Cells(row_num, 2).Value = file_records
                    summary_sheet.Cells(row_num, 3).Value = file_total
                    summary_sheet.Cells(row_num, 4).Value = file_average
                    
                    grand_total += file_total
                    total_records += file_records
                    row_num += 1
                    
                    file_workbook.Close()
                    
                except Exception as e:
                    logger.warning(f"Error memproses file {excel_file}: {e}")
                    continue
            
            # Tambahkan total
            summary_sheet.Cells(row_num + 1, 1).Value = "TOTAL"
            summary_sheet.Cells(row_num + 1, 2).Value = total_records
            summary_sheet.Cells(row_num + 1, 3).Value = grand_total
            summary_sheet.Cells(row_num + 1, 4).Value = grand_total / total_records if total_records > 0 else 0
            
            # Format tabel
            if row_num > 2:
                table_range = summary_sheet.Range(f"A1:D{row_num+1}")
                table_range.Select()
            
            await self.excel_handler.save_workbook(workbook, output_file)
            logger.info(f"Laporan bulanan berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat laporan bulanan: {e}")
            raise

# Contoh penggunaan
async def main():
    """Contoh penggunaan Excel Data Processor."""
    processor = ExcelDataProcessor()
    
    # Contoh 1: Proses data penjualan
    # await processor.process_sales_data(
    #     "data/sales_raw.xlsx",
    #     "output/sales_processed.xlsx"
    # )
    
    # Contoh 2: Bersihkan data customer
    # await processor.clean_customer_data(
    #     "data/customers_raw.xlsx",
    #     "output/customers_clean.xlsx"
    # )
    
    # Contoh 3: Buat laporan bulanan
    # await processor.generate_monthly_report(
    #     "data/monthly_files/",
    #     "output/monthly_report.xlsx"
    # )
    
    print("Excel Data Processing Cookbook siap digunakan!")
    print("Uncomment contoh di atas untuk menjalankan operasi.")

if __name__ == "__main__":
    asyncio.run(main())