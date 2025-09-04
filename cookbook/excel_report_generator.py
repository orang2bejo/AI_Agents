#!/usr/bin/env python3
"""
📈 Excel Report Generator Cookbook

Contoh praktis untuk membuat laporan Excel otomatis menggunakan Jarvis AI.
Script ini mendemonstrasikan pembuatan berbagai jenis laporan dengan chart dan formatting.

Author: Orangbejo
GitHub: https://github.com/Orangbejo
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from windows_use.office import ExcelHandler
from windows_use.observability.logger import setup_logger

logger = setup_logger(__name__)

class ExcelReportGenerator:
    """Generator untuk membuat berbagai jenis laporan Excel."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        
    async def create_sales_dashboard(self, data_file: str, output_file: str):
        """
        Membuat dashboard penjualan dengan:
        - Summary metrics
        - Chart penjualan per bulan
        - Top products
        - Performance indicators
        """
        try:
            logger.info(f"Membuat sales dashboard dari {data_file}")
            
            # Buka data source
            source_workbook = await self.excel_handler.open_workbook(data_file)
            source_sheet = source_workbook.ActiveSheet
            
            # Buat workbook baru untuk dashboard
            dashboard_workbook = await self.excel_handler.create_workbook()
            dashboard_sheet = dashboard_workbook.ActiveSheet
            dashboard_sheet.Name = "Sales_Dashboard"
            
            # Baca data dari source
            last_row = source_sheet.Cells(source_sheet.Rows.Count, 1).End(-4162).Row
            
            # Asumsi kolom: A=Date, B=Product, C=Quantity, D=Price, E=Total
            sales_data = []
            for row in range(2, last_row + 1):
                date_val = source_sheet.Cells(row, 1).Value
                product = source_sheet.Cells(row, 2).Value
                quantity = source_sheet.Cells(row, 3).Value or 0
                price = source_sheet.Cells(row, 4).Value or 0
                total = source_sheet.Cells(row, 5).Value or (quantity * price)
                
                sales_data.append({
                    'date': date_val,
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'total': total
                })
            
            # === SECTION 1: KEY METRICS ===
            dashboard_sheet.Cells(1, 1).Value = "SALES DASHBOARD"
            dashboard_sheet.Cells(1, 1).Font.Size = 16
            dashboard_sheet.Cells(1, 1).Font.Bold = True
            
            # Total Sales
            total_sales = sum(item['total'] for item in sales_data)
            dashboard_sheet.Cells(3, 1).Value = "Total Sales:"
            dashboard_sheet.Cells(3, 2).Value = total_sales
            dashboard_sheet.Cells(3, 2).NumberFormat = "#,##0.00"
            
            # Total Transactions
            total_transactions = len(sales_data)
            dashboard_sheet.Cells(4, 1).Value = "Total Transactions:"
            dashboard_sheet.Cells(4, 2).Value = total_transactions
            
            # Average Transaction
            avg_transaction = total_sales / total_transactions if total_transactions > 0 else 0
            dashboard_sheet.Cells(5, 1).Value = "Average Transaction:"
            dashboard_sheet.Cells(5, 2).Value = avg_transaction
            dashboard_sheet.Cells(5, 2).NumberFormat = "#,##0.00"
            
            # === SECTION 2: TOP PRODUCTS ===
            dashboard_sheet.Cells(7, 1).Value = "TOP PRODUCTS"
            dashboard_sheet.Cells(7, 1).Font.Bold = True
            
            # Hitung total per produk
            product_totals = {}
            for item in sales_data:
                product = item['product']
                if product in product_totals:
                    product_totals[product] += item['total']
                else:
                    product_totals[product] = item['total']
            
            # Sort dan ambil top 5
            top_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            dashboard_sheet.Cells(8, 1).Value = "Product"
            dashboard_sheet.Cells(8, 2).Value = "Total Sales"
            
            for i, (product, total) in enumerate(top_products, 9):
                dashboard_sheet.Cells(i, 1).Value = product
                dashboard_sheet.Cells(i, 2).Value = total
                dashboard_sheet.Cells(i, 2).NumberFormat = "#,##0.00"
            
            # === SECTION 3: MONTHLY TREND ===
            dashboard_sheet.Cells(7, 4).Value = "MONTHLY TREND"
            dashboard_sheet.Cells(7, 4).Font.Bold = True
            
            # Hitung total per bulan
            monthly_totals = {}
            for item in sales_data:
                if item['date']:
                    try:
                        if isinstance(item['date'], datetime):
                            month_key = item['date'].strftime('%Y-%m')
                        else:
                            # Coba parse string date
                            date_obj = datetime.strptime(str(item['date']), '%Y-%m-%d')
                            month_key = date_obj.strftime('%Y-%m')
                        
                        if month_key in monthly_totals:
                            monthly_totals[month_key] += item['total']
                        else:
                            monthly_totals[month_key] = item['total']
                    except:
                        continue
            
            # Sort months
            sorted_months = sorted(monthly_totals.items())
            
            dashboard_sheet.Cells(8, 4).Value = "Month"
            dashboard_sheet.Cells(8, 5).Value = "Sales"
            
            for i, (month, total) in enumerate(sorted_months, 9):
                dashboard_sheet.Cells(i, 4).Value = month
                dashboard_sheet.Cells(i, 5).Value = total
                dashboard_sheet.Cells(i, 5).NumberFormat = "#,##0.00"
            
            # === FORMATTING ===
            # Auto-fit columns
            dashboard_sheet.Columns("A:E").AutoFit()
            
            # Add borders to key sections
            metrics_range = dashboard_sheet.Range("A3:B5")
            metrics_range.Borders.LineStyle = 1
            
            products_range = dashboard_sheet.Range(f"A8:B{8 + len(top_products)}")
            products_range.Borders.LineStyle = 1
            
            monthly_range = dashboard_sheet.Range(f"D8:E{8 + len(sorted_months)}")
            monthly_range.Borders.LineStyle = 1
            
            # Close source workbook
            source_workbook.Close()
            
            # Save dashboard
            await self.excel_handler.save_workbook(dashboard_workbook, output_file)
            logger.info(f"Sales dashboard berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat sales dashboard: {e}")
            raise
    
    async def create_financial_report(self, data_file: str, output_file: str):
        """
        Membuat laporan keuangan dengan:
        - Income statement
        - Balance sheet summary
        - Cash flow indicators
        """
        try:
            logger.info(f"Membuat financial report dari {data_file}")
            
            # Buat workbook baru
            workbook = await self.excel_handler.create_workbook()
            
            # === INCOME STATEMENT SHEET ===
            income_sheet = workbook.ActiveSheet
            income_sheet.Name = "Income_Statement"
            
            # Header
            income_sheet.Cells(1, 1).Value = "INCOME STATEMENT"
            income_sheet.Cells(1, 1).Font.Size = 14
            income_sheet.Cells(1, 1).Font.Bold = True
            
            current_date = datetime.now()
            income_sheet.Cells(2, 1).Value = f"Period: {current_date.strftime('%B %Y')}"
            
            # Revenue section
            income_sheet.Cells(4, 1).Value = "REVENUE"
            income_sheet.Cells(4, 1).Font.Bold = True
            income_sheet.Cells(5, 1).Value = "Sales Revenue"
            income_sheet.Cells(5, 2).Value = 1500000  # Sample data
            income_sheet.Cells(6, 1).Value = "Service Revenue"
            income_sheet.Cells(6, 2).Value = 300000
            income_sheet.Cells(7, 1).Value = "Total Revenue"
            income_sheet.Cells(7, 2).Formula = "=SUM(B5:B6)"
            income_sheet.Cells(7, 1).Font.Bold = True
            
            # Expenses section
            income_sheet.Cells(9, 1).Value = "EXPENSES"
            income_sheet.Cells(9, 1).Font.Bold = True
            income_sheet.Cells(10, 1).Value = "Cost of Goods Sold"
            income_sheet.Cells(10, 2).Value = 800000
            income_sheet.Cells(11, 1).Value = "Operating Expenses"
            income_sheet.Cells(11, 2).Value = 400000
            income_sheet.Cells(12, 1).Value = "Administrative Expenses"
            income_sheet.Cells(12, 2).Value = 150000
            income_sheet.Cells(13, 1).Value = "Total Expenses"
            income_sheet.Cells(13, 2).Formula = "=SUM(B10:B12)"
            income_sheet.Cells(13, 1).Font.Bold = True
            
            # Net Income
            income_sheet.Cells(15, 1).Value = "NET INCOME"
            income_sheet.Cells(15, 2).Formula = "=B7-B13"
            income_sheet.Cells(15, 1).Font.Bold = True
            income_sheet.Cells(15, 2).Font.Bold = True
            
            # Format currency
            currency_range = income_sheet.Range("B5:B15")
            currency_range.NumberFormat = "#,##0.00"
            
            # === BALANCE SHEET ===
            balance_sheet = workbook.Worksheets.Add()
            balance_sheet.Name = "Balance_Sheet"
            
            # Header
            balance_sheet.Cells(1, 1).Value = "BALANCE SHEET"
            balance_sheet.Cells(1, 1).Font.Size = 14
            balance_sheet.Cells(1, 1).Font.Bold = True
            balance_sheet.Cells(2, 1).Value = f"As of {current_date.strftime('%B %d, %Y')}"
            
            # Assets
            balance_sheet.Cells(4, 1).Value = "ASSETS"
            balance_sheet.Cells(4, 1).Font.Bold = True
            balance_sheet.Cells(5, 1).Value = "Current Assets"
            balance_sheet.Cells(6, 1).Value = "  Cash"
            balance_sheet.Cells(6, 2).Value = 500000
            balance_sheet.Cells(7, 1).Value = "  Accounts Receivable"
            balance_sheet.Cells(7, 2).Value = 300000
            balance_sheet.Cells(8, 1).Value = "  Inventory"
            balance_sheet.Cells(8, 2).Value = 200000
            balance_sheet.Cells(9, 1).Value = "Total Current Assets"
            balance_sheet.Cells(9, 2).Formula = "=SUM(B6:B8)"
            balance_sheet.Cells(9, 1).Font.Bold = True
            
            balance_sheet.Cells(11, 1).Value = "Fixed Assets"
            balance_sheet.Cells(12, 1).Value = "  Equipment"
            balance_sheet.Cells(12, 2).Value = 800000
            balance_sheet.Cells(13, 1).Value = "  Buildings"
            balance_sheet.Cells(13, 2).Value = 1200000
            balance_sheet.Cells(14, 1).Value = "Total Fixed Assets"
            balance_sheet.Cells(14, 2).Formula = "=SUM(B12:B13)"
            balance_sheet.Cells(14, 1).Font.Bold = True
            
            balance_sheet.Cells(16, 1).Value = "TOTAL ASSETS"
            balance_sheet.Cells(16, 2).Formula = "=B9+B14"
            balance_sheet.Cells(16, 1).Font.Bold = True
            balance_sheet.Cells(16, 2).Font.Bold = True
            
            # Liabilities & Equity
            balance_sheet.Cells(18, 1).Value = "LIABILITIES & EQUITY"
            balance_sheet.Cells(18, 1).Font.Bold = True
            balance_sheet.Cells(19, 1).Value = "Current Liabilities"
            balance_sheet.Cells(20, 1).Value = "  Accounts Payable"
            balance_sheet.Cells(20, 2).Value = 150000
            balance_sheet.Cells(21, 1).Value = "  Short-term Debt"
            balance_sheet.Cells(21, 2).Value = 100000
            balance_sheet.Cells(22, 1).Value = "Total Current Liabilities"
            balance_sheet.Cells(22, 2).Formula = "=SUM(B20:B21)"
            balance_sheet.Cells(22, 1).Font.Bold = True
            
            balance_sheet.Cells(24, 1).Value = "Long-term Debt"
            balance_sheet.Cells(24, 2).Value = 500000
            
            balance_sheet.Cells(26, 1).Value = "Owner's Equity"
            balance_sheet.Cells(26, 2).Formula = "=B16-B22-B24"
            balance_sheet.Cells(26, 1).Font.Bold = True
            
            balance_sheet.Cells(28, 1).Value = "TOTAL LIABILITIES & EQUITY"
            balance_sheet.Cells(28, 2).Formula = "=B22+B24+B26"
            balance_sheet.Cells(28, 1).Font.Bold = True
            balance_sheet.Cells(28, 2).Font.Bold = True
            
            # Format currency
            balance_currency_range = balance_sheet.Range("B6:B28")
            balance_currency_range.NumberFormat = "#,##0.00"
            
            # === CASH FLOW SHEET ===
            cashflow_sheet = workbook.Worksheets.Add()
            cashflow_sheet.Name = "Cash_Flow"
            
            # Header
            cashflow_sheet.Cells(1, 1).Value = "CASH FLOW STATEMENT"
            cashflow_sheet.Cells(1, 1).Font.Size = 14
            cashflow_sheet.Cells(1, 1).Font.Bold = True
            cashflow_sheet.Cells(2, 1).Value = f"Period: {current_date.strftime('%B %Y')}"
            
            # Operating Activities
            cashflow_sheet.Cells(4, 1).Value = "OPERATING ACTIVITIES"
            cashflow_sheet.Cells(4, 1).Font.Bold = True
            cashflow_sheet.Cells(5, 1).Value = "Net Income"
            cashflow_sheet.Cells(5, 2).Formula = "=Income_Statement.B15"
            cashflow_sheet.Cells(6, 1).Value = "Depreciation"
            cashflow_sheet.Cells(6, 2).Value = 50000
            cashflow_sheet.Cells(7, 1).Value = "Changes in Working Capital"
            cashflow_sheet.Cells(7, 2).Value = -25000
            cashflow_sheet.Cells(8, 1).Value = "Net Cash from Operations"
            cashflow_sheet.Cells(8, 2).Formula = "=SUM(B5:B7)"
            cashflow_sheet.Cells(8, 1).Font.Bold = True
            
            # Investing Activities
            cashflow_sheet.Cells(10, 1).Value = "INVESTING ACTIVITIES"
            cashflow_sheet.Cells(10, 1).Font.Bold = True
            cashflow_sheet.Cells(11, 1).Value = "Equipment Purchase"
            cashflow_sheet.Cells(11, 2).Value = -100000
            cashflow_sheet.Cells(12, 1).Value = "Net Cash from Investing"
            cashflow_sheet.Cells(12, 2).Value = -100000
            cashflow_sheet.Cells(12, 1).Font.Bold = True
            
            # Financing Activities
            cashflow_sheet.Cells(14, 1).Value = "FINANCING ACTIVITIES"
            cashflow_sheet.Cells(14, 1).Font.Bold = True
            cashflow_sheet.Cells(15, 1).Value = "Loan Proceeds"
            cashflow_sheet.Cells(15, 2).Value = 200000
            cashflow_sheet.Cells(16, 1).Value = "Loan Payments"
            cashflow_sheet.Cells(16, 2).Value = -50000
            cashflow_sheet.Cells(17, 1).Value = "Net Cash from Financing"
            cashflow_sheet.Cells(17, 2).Formula = "=SUM(B15:B16)"
            cashflow_sheet.Cells(17, 1).Font.Bold = True
            
            # Net Change in Cash
            cashflow_sheet.Cells(19, 1).Value = "NET CHANGE IN CASH"
            cashflow_sheet.Cells(19, 2).Formula = "=B8+B12+B17"
            cashflow_sheet.Cells(19, 1).Font.Bold = True
            cashflow_sheet.Cells(19, 2).Font.Bold = True
            
            # Format currency
            cashflow_currency_range = cashflow_sheet.Range("B5:B19")
            cashflow_currency_range.NumberFormat = "#,##0.00"
            
            # Auto-fit all columns
            for sheet in [income_sheet, balance_sheet, cashflow_sheet]:
                sheet.Columns("A:B").AutoFit()
            
            await self.excel_handler.save_workbook(workbook, output_file)
            logger.info(f"Financial report berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat financial report: {e}")
            raise
    
    async def create_inventory_report(self, data_file: str, output_file: str):
        """
        Membuat laporan inventory dengan:
        - Stock levels
        - Reorder alerts
        - Valuation summary
        """
        try:
            logger.info(f"Membuat inventory report dari {data_file}")
            
            # Buka data source
            source_workbook = await self.excel_handler.open_workbook(data_file)
            source_sheet = source_workbook.ActiveSheet
            
            # Buat workbook baru
            report_workbook = await self.excel_handler.create_workbook()
            report_sheet = report_workbook.ActiveSheet
            report_sheet.Name = "Inventory_Report"
            
            # Header
            report_sheet.Cells(1, 1).Value = "INVENTORY REPORT"
            report_sheet.Cells(1, 1).Font.Size = 14
            report_sheet.Cells(1, 1).Font.Bold = True
            report_sheet.Cells(2, 1).Value = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Copy headers
            report_sheet.Cells(4, 1).Value = "Product Code"
            report_sheet.Cells(4, 2).Value = "Product Name"
            report_sheet.Cells(4, 3).Value = "Current Stock"
            report_sheet.Cells(4, 4).Value = "Minimum Stock"
            report_sheet.Cells(4, 5).Value = "Unit Price"
            report_sheet.Cells(4, 6).Value = "Total Value"
            report_sheet.Cells(4, 7).Value = "Status"
            
            # Make headers bold
            header_range = report_sheet.Range("A4:G4")
            header_range.Font.Bold = True
            
            # Read and process data
            last_row = source_sheet.Cells(source_sheet.Rows.Count, 1).End(-4162).Row
            total_value = 0
            low_stock_count = 0
            
            for row in range(2, last_row + 1):
                # Copy data
                for col in range(1, 6):  # A to E
                    value = source_sheet.Cells(row, col).Value
                    report_sheet.Cells(row + 3, col).Value = value
                
                # Calculate total value
                current_stock = source_sheet.Cells(row, 3).Value or 0
                unit_price = source_sheet.Cells(row, 5).Value or 0
                item_value = current_stock * unit_price
                report_sheet.Cells(row + 3, 6).Value = item_value
                report_sheet.Cells(row + 3, 6).NumberFormat = "#,##0.00"
                total_value += item_value
                
                # Determine status
                min_stock = source_sheet.Cells(row, 4).Value or 0
                if current_stock <= min_stock:
                    status = "LOW STOCK"
                    low_stock_count += 1
                    # Highlight low stock rows
                    status_range = report_sheet.Range(f"A{row + 3}:G{row + 3}")
                    status_range.Interior.Color = 255  # Red background
                elif current_stock <= min_stock * 1.5:
                    status = "REORDER SOON"
                    status_range = report_sheet.Range(f"A{row + 3}:G{row + 3}")
                    status_range.Interior.Color = 65535  # Yellow background
                else:
                    status = "OK"
                
                report_sheet.Cells(row + 3, 7).Value = status
            
            # Summary section
            summary_row = last_row + 5
            report_sheet.Cells(summary_row, 1).Value = "SUMMARY"
            report_sheet.Cells(summary_row, 1).Font.Bold = True
            report_sheet.Cells(summary_row, 1).Font.Size = 12
            
            report_sheet.Cells(summary_row + 1, 1).Value = "Total Items:"
            report_sheet.Cells(summary_row + 1, 2).Value = last_row - 1
            
            report_sheet.Cells(summary_row + 2, 1).Value = "Total Inventory Value:"
            report_sheet.Cells(summary_row + 2, 2).Value = total_value
            report_sheet.Cells(summary_row + 2, 2).NumberFormat = "#,##0.00"
            
            report_sheet.Cells(summary_row + 3, 1).Value = "Low Stock Items:"
            report_sheet.Cells(summary_row + 3, 2).Value = low_stock_count
            
            # Auto-fit columns
            report_sheet.Columns("A:G").AutoFit()
            
            # Add borders
            data_range = report_sheet.Range(f"A4:G{last_row + 3}")
            data_range.Borders.LineStyle = 1
            
            source_workbook.Close()
            await self.excel_handler.save_workbook(report_workbook, output_file)
            logger.info(f"Inventory report berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat inventory report: {e}")
            raise

# Contoh penggunaan
async def main():
    """Contoh penggunaan Excel Report Generator."""
    generator = ExcelReportGenerator()
    
    # Contoh 1: Sales Dashboard
    # await generator.create_sales_dashboard(
    #     "data/sales_data.xlsx",
    #     "reports/sales_dashboard.xlsx"
    # )
    
    # Contoh 2: Financial Report
    # await generator.create_financial_report(
    #     "data/financial_data.xlsx",
    #     "reports/financial_report.xlsx"
    # )
    
    # Contoh 3: Inventory Report
    # await generator.create_inventory_report(
    #     "data/inventory_data.xlsx",
    #     "reports/inventory_report.xlsx"
    # )
    
    print("Excel Report Generator Cookbook siap digunakan!")
    print("Uncomment contoh di atas untuk menjalankan generator.")

if __name__ == "__main__":
    asyncio.run(main())