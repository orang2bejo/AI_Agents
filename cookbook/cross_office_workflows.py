#!/usr/bin/env python3
"""
🔄 Cross-Office Workflows Cookbook

Contoh praktis untuk mengintegrasikan Excel, Word, dan PowerPoint dalam workflow otomatis.
Script ini mendemonstrasikan bagaimana data dari Excel dapat digunakan untuk membuat
dokumen Word dan presentasi PowerPoint secara otomatis.

Author: Orangbejo
GitHub: https://github.com/Orangbejo
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from windows_use.office import ExcelHandler, WordHandler, PowerPointHandler
from windows_use.observability.logger import setup_logger

logger = setup_logger(__name__)

class CrossOfficeWorkflows:
    """Workflow integrator untuk Excel, Word, dan PowerPoint."""
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.word_handler = WordHandler()
        self.powerpoint_handler = PowerPointHandler()
        
    async def sales_report_workflow(self, excel_file: str, output_dir: str):
        """
        Workflow lengkap sales report:
        1. Baca data sales dari Excel
        2. Generate Word report dengan analisis
        3. Buat PowerPoint presentation untuk management
        """
        try:
            logger.info("Memulai sales report workflow")
            
            # === STEP 1: BACA DATA DARI EXCEL ===
            workbook = await self.excel_handler.open_workbook(excel_file)
            worksheet = workbook.ActiveSheet
            
            # Baca data sales (asumsi format: A1=Header, A2:E100=Data)
            sales_data = []
            row = 2  # Mulai dari row 2 (skip header)
            
            while worksheet.Cells(row, 1).Value is not None:
                sales_record = {
                    'date': worksheet.Cells(row, 1).Value,
                    'salesperson': worksheet.Cells(row, 2).Value,
                    'product': worksheet.Cells(row, 3).Value,
                    'quantity': worksheet.Cells(row, 4).Value or 0,
                    'amount': worksheet.Cells(row, 5).Value or 0
                }
                sales_data.append(sales_record)
                row += 1
                
                if row > 1000:  # Safety limit
                    break
            
            await self.excel_handler.close_workbook(workbook)
            
            # === STEP 2: ANALISIS DATA ===
            total_sales = sum(record['amount'] for record in sales_data)
            total_quantity = sum(record['quantity'] for record in sales_data)
            unique_products = len(set(record['product'] for record in sales_data))
            unique_salespeople = len(set(record['salesperson'] for record in sales_data))
            
            # Top performers
            salesperson_totals = {}
            for record in sales_data:
                sp = record['salesperson']
                salesperson_totals[sp] = salesperson_totals.get(sp, 0) + record['amount']
            
            top_salespeople = sorted(salesperson_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Product analysis
            product_totals = {}
            for record in sales_data:
                prod = record['product']
                product_totals[prod] = product_totals.get(prod, 0) + record['amount']
            
            top_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # === STEP 3: GENERATE WORD REPORT ===
            word_doc = await self.word_handler.create_document()
            
            # Title
            title_range = word_doc.Range(0, 0)
            title_range.InsertAfter("SALES PERFORMANCE REPORT\n")
            title_range.Font.Size = 18
            title_range.Font.Bold = True
            title_range.ParagraphFormat.Alignment = 1  # Center
            
            # Report date
            date_range = word_doc.Range(word_doc.Content.End - 1, word_doc.Content.End - 1)
            date_range.InsertAfter(f"\nReport Generated: {datetime.now().strftime('%B %d, %Y')}\n\n")
            date_range.Font.Size = 12
            date_range.ParagraphFormat.Alignment = 1  # Center
            
            # Executive Summary
            summary_range = word_doc.Range(word_doc.Content.End - 1, word_doc.Content.End - 1)
            summary_text = f"""
EXECUTIVE SUMMARY

Total Sales Revenue: ${total_sales:,.2f}
Total Units Sold: {total_quantity:,}
Number of Products: {unique_products}
Active Sales Team: {unique_salespeople} people
Reporting Period: {len(sales_data)} transactions

KEY HIGHLIGHTS

Top Performing Salesperson: {top_salespeople[0][0] if top_salespeople else 'N/A'} (${top_salespeople[0][1]:,.2f if top_salespeople else 0})
Best Selling Product: {top_products[0][0] if top_products else 'N/A'} (${top_products[0][1]:,.2f if top_products else 0})

TOP 5 SALES PERFORMERS

"""
            
            for i, (name, amount) in enumerate(top_salespeople, 1):
                summary_text += f"{i}. {name}: ${amount:,.2f}\n"
            
            summary_text += "\nTOP 5 PRODUCTS BY REVENUE\n\n"
            
            for i, (product, amount) in enumerate(top_products, 1):
                summary_text += f"{i}. {product}: ${amount:,.2f}\n"
            
            summary_range.InsertAfter(summary_text)
            summary_range.Font.Size = 11
            
            word_output = os.path.join(output_dir, "sales_report.docx")
            await self.word_handler.save_document(word_doc, word_output)
            await self.word_handler.close_document(word_doc)
            
            # === STEP 4: GENERATE POWERPOINT PRESENTATION ===
            presentation = await self.powerpoint_handler.create_presentation()
            
            # Slide 1: Title
            title_slide = presentation.Slides(1)
            title_slide.Shapes.Title.TextFrame.TextRange.Text = "Sales Performance Dashboard"
            title_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = f"""
Quarterly Sales Review
{datetime.now().strftime('%B %Y')}
Generated from live data
"""
            
            # Slide 2: Key Metrics
            metrics_slide = presentation.Slides.Add(2, 2)
            metrics_slide.Shapes.Title.TextFrame.TextRange.Text = "Key Performance Metrics"
            
            metrics_text = f"""
💰 Total Revenue: ${total_sales:,.2f}
📦 Units Sold: {total_quantity:,}
🏆 Top Performer: {top_salespeople[0][0] if top_salespeople else 'N/A'}
⭐ Best Product: {top_products[0][0] if top_products else 'N/A'}

Performance Indicators:
• Revenue Target: {'✅ Achieved' if total_sales > 100000 else '⚠️ Below Target'}
• Team Productivity: {'🔥 Excellent' if len(sales_data) > 50 else '📈 Good'}
• Product Diversity: {'🌟 Strong' if unique_products > 10 else '💡 Opportunity'}
"""
            
            metrics_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = metrics_text
            metrics_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            
            # Slide 3: Top Performers
            performers_slide = presentation.Slides.Add(3, 2)
            performers_slide.Shapes.Title.TextFrame.TextRange.Text = "Top Sales Performers"
            
            performers_text = "\n".join([
                f"{i}. {name}: ${amount:,.2f}"
                for i, (name, amount) in enumerate(top_salespeople, 1)
            ])
            
            performers_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = performers_text
            performers_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 24
            
            # Slide 4: Product Analysis
            products_slide = presentation.Slides.Add(4, 2)
            products_slide.Shapes.Title.TextFrame.TextRange.Text = "Top Products by Revenue"
            
            products_text = "\n".join([
                f"{i}. {product}: ${amount:,.2f}"
                for i, (product, amount) in enumerate(top_products, 1)
            ])
            
            products_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = products_text
            products_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 24
            
            ppt_output = os.path.join(output_dir, "sales_dashboard.pptx")
            await self.powerpoint_handler.save_presentation(presentation, ppt_output)
            
            logger.info(f"Sales report workflow selesai. Output: {word_output}, {ppt_output}")
            
            return {
                'word_report': word_output,
                'powerpoint_dashboard': ppt_output,
                'summary': {
                    'total_sales': total_sales,
                    'total_quantity': total_quantity,
                    'top_salesperson': top_salespeople[0] if top_salespeople else None,
                    'top_product': top_products[0] if top_products else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error dalam sales report workflow: {e}")
            raise
    
    async def employee_review_workflow(self, employee_data: dict, output_dir: str):
        """
        Workflow employee performance review:
        1. Buat Excel scorecard dengan metrics
        2. Generate Word evaluation report
        3. Buat PowerPoint presentation untuk review meeting
        """
        try:
            logger.info(f"Memulai employee review workflow untuk {employee_data.get('name', 'Employee')}")
            
            # === STEP 1: BUAT EXCEL SCORECARD ===
            workbook = await self.excel_handler.create_workbook()
            worksheet = workbook.ActiveSheet
            worksheet.Name = "Performance_Scorecard"
            
            # Headers
            headers = ['Metric', 'Target', 'Actual', 'Score (%)', 'Rating']
            for col, header in enumerate(headers, 1):
                cell = worksheet.Cells(1, col)
                cell.Value = header
                cell.Font.Bold = True
                cell.Interior.Color = 0xD3D3D3  # Light gray
            
            # Performance metrics
            metrics = employee_data.get('metrics', [
                {'name': 'Sales Target Achievement', 'target': 100000, 'actual': 120000},
                {'name': 'Customer Satisfaction', 'target': 90, 'actual': 95},
                {'name': 'Project Completion Rate', 'target': 95, 'actual': 98},
                {'name': 'Team Collaboration', 'target': 85, 'actual': 90},
                {'name': 'Professional Development', 'target': 80, 'actual': 85}
            ])
            
            total_score = 0
            for row, metric in enumerate(metrics, 2):
                worksheet.Cells(row, 1).Value = metric['name']
                worksheet.Cells(row, 2).Value = metric['target']
                worksheet.Cells(row, 3).Value = metric['actual']
                
                # Calculate score percentage
                score = min(100, (metric['actual'] / metric['target']) * 100)
                worksheet.Cells(row, 4).Value = f"{score:.1f}%"
                
                # Rating
                if score >= 95:
                    rating = "Excellent"
                elif score >= 85:
                    rating = "Good"
                elif score >= 75:
                    rating = "Satisfactory"
                else:
                    rating = "Needs Improvement"
                
                worksheet.Cells(row, 5).Value = rating
                total_score += score
            
            # Overall score
            overall_row = len(metrics) + 3
            worksheet.Cells(overall_row, 1).Value = "OVERALL SCORE"
            worksheet.Cells(overall_row, 1).Font.Bold = True
            worksheet.Cells(overall_row, 4).Value = f"{total_score / len(metrics):.1f}%"
            worksheet.Cells(overall_row, 4).Font.Bold = True
            
            # Auto-fit columns
            worksheet.Columns.AutoFit()
            
            excel_output = os.path.join(output_dir, f"{employee_data.get('name', 'employee')}_scorecard.xlsx")
            await self.excel_handler.save_workbook(workbook, excel_output)
            await self.excel_handler.close_workbook(workbook)
            
            # === STEP 2: GENERATE WORD EVALUATION REPORT ===
            word_doc = await self.word_handler.create_document()
            
            # Title
            title_range = word_doc.Range(0, 0)
            title_range.InsertAfter("EMPLOYEE PERFORMANCE EVALUATION\n")
            title_range.Font.Size = 16
            title_range.Font.Bold = True
            title_range.ParagraphFormat.Alignment = 1  # Center
            
            # Employee info
            info_range = word_doc.Range(word_doc.Content.End - 1, word_doc.Content.End - 1)
            info_text = f"""

Employee: {employee_data.get('name', 'N/A')}
Position: {employee_data.get('position', 'N/A')}
Department: {employee_data.get('department', 'N/A')}
Review Period: {employee_data.get('review_period', 'Q4 2024')}
Reviewer: {employee_data.get('reviewer', 'Manager Name')}
Date: {datetime.now().strftime('%B %d, %Y')}

PERFORMANCE SUMMARY

Overall Rating: {total_score / len(metrics):.1f}%

STRENGTHS:
"""
            
            strengths = employee_data.get('strengths', [
                'Consistently exceeds sales targets',
                'Excellent customer relationship management',
                'Strong team collaboration skills',
                'Proactive in professional development'
            ])
            
            for strength in strengths:
                info_text += f"• {strength}\n"
            
            info_text += "\nAREAS FOR IMPROVEMENT:\n"
            
            improvements = employee_data.get('improvements', [
                'Time management during peak periods',
                'Documentation and reporting consistency',
                'Cross-functional project leadership'
            ])
            
            for improvement in improvements:
                info_text += f"• {improvement}\n"
            
            info_text += "\nDEVELOPMENT GOALS FOR NEXT PERIOD:\n"
            
            goals = employee_data.get('goals', [
                'Complete advanced sales training certification',
                'Lead at least one cross-departmental project',
                'Mentor junior team members',
                'Improve customer retention rate by 5%'
            ])
            
            for goal in goals:
                info_text += f"• {goal}\n"
            
            info_range.InsertAfter(info_text)
            info_range.Font.Size = 11
            
            word_output = os.path.join(output_dir, f"{employee_data.get('name', 'employee')}_evaluation.docx")
            await self.word_handler.save_document(word_doc, word_output)
            await self.word_handler.close_document(word_doc)
            
            # === STEP 3: GENERATE POWERPOINT PRESENTATION ===
            presentation = await self.powerpoint_handler.create_presentation()
            
            # Slide 1: Title
            title_slide = presentation.Slides(1)
            title_slide.Shapes.Title.TextFrame.TextRange.Text = f"Performance Review\n{employee_data.get('name', 'Employee Name')}"
            title_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = f"""
{employee_data.get('position', 'Position')}
{employee_data.get('review_period', 'Review Period')}
{datetime.now().strftime('%B %Y')}
"""
            
            # Slide 2: Performance Overview
            overview_slide = presentation.Slides.Add(2, 2)
            overview_slide.Shapes.Title.TextFrame.TextRange.Text = "Performance Overview"
            
            overview_text = f"""
Overall Score: {total_score / len(metrics):.1f}%

Key Achievements:
• {strengths[0] if strengths else 'Strong performance'}
• {strengths[1] if len(strengths) > 1 else 'Consistent results'}
• {strengths[2] if len(strengths) > 2 else 'Team contribution'}

Rating: {'Excellent' if total_score / len(metrics) >= 95 else 'Good' if total_score / len(metrics) >= 85 else 'Satisfactory'}
"""
            
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = overview_text
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            # Slide 3: Development Plan
            development_slide = presentation.Slides.Add(3, 2)
            development_slide.Shapes.Title.TextFrame.TextRange.Text = "Development Plan"
            
            development_text = "Goals for Next Period:\n\n" + "\n".join([f"• {goal}" for goal in goals])
            development_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = development_text
            development_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            ppt_output = os.path.join(output_dir, f"{employee_data.get('name', 'employee')}_review.pptx")
            await self.powerpoint_handler.save_presentation(presentation, ppt_output)
            
            logger.info(f"Employee review workflow selesai. Output: {excel_output}, {word_output}, {ppt_output}")
            
            return {
                'excel_scorecard': excel_output,
                'word_evaluation': word_output,
                'powerpoint_review': ppt_output,
                'overall_score': total_score / len(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error dalam employee review workflow: {e}")
            raise
    
    async def project_documentation_workflow(self, project_data: dict, output_dir: str):
        """
        Workflow dokumentasi proyek lengkap:
        1. Buat Excel project tracker dengan timeline
        2. Generate Word project documentation
        3. Buat PowerPoint project presentation
        """
        try:
            logger.info(f"Memulai project documentation workflow untuk {project_data.get('name', 'Project')}")
            
            # === STEP 1: BUAT EXCEL PROJECT TRACKER ===
            workbook = await self.excel_handler.create_workbook()
            
            # Sheet 1: Project Overview
            overview_sheet = workbook.ActiveSheet
            overview_sheet.Name = "Project_Overview"
            
            # Project details
            overview_sheet.Cells(1, 1).Value = "Project Name"
            overview_sheet.Cells(1, 2).Value = project_data.get('name', 'Project Name')
            overview_sheet.Cells(2, 1).Value = "Start Date"
            overview_sheet.Cells(2, 2).Value = project_data.get('start_date', '2024-01-01')
            overview_sheet.Cells(3, 1).Value = "End Date"
            overview_sheet.Cells(3, 2).Value = project_data.get('end_date', '2024-12-31')
            overview_sheet.Cells(4, 1).Value = "Budget"
            overview_sheet.Cells(4, 2).Value = f"${project_data.get('budget', 0):,}"
            overview_sheet.Cells(5, 1).Value = "Status"
            overview_sheet.Cells(5, 2).Value = project_data.get('status', 'In Progress')
            
            # Sheet 2: Task Tracker
            task_sheet = workbook.Worksheets.Add()
            task_sheet.Name = "Task_Tracker"
            
            # Headers
            task_headers = ['Task ID', 'Task Name', 'Assigned To', 'Start Date', 'Due Date', 'Status', 'Progress %']
            for col, header in enumerate(task_headers, 1):
                cell = task_sheet.Cells(1, col)
                cell.Value = header
                cell.Font.Bold = True
                cell.Interior.Color = 0xD3D3D3
            
            # Sample tasks
            tasks = project_data.get('tasks', [
                {'id': 'T001', 'name': 'Requirements Analysis', 'assignee': 'John Doe', 'start': '2024-01-01', 'due': '2024-01-15', 'status': 'Complete', 'progress': 100},
                {'id': 'T002', 'name': 'System Design', 'assignee': 'Jane Smith', 'start': '2024-01-16', 'due': '2024-02-01', 'status': 'Complete', 'progress': 100},
                {'id': 'T003', 'name': 'Development Phase 1', 'assignee': 'Dev Team', 'start': '2024-02-01', 'due': '2024-03-15', 'status': 'In Progress', 'progress': 75},
                {'id': 'T004', 'name': 'Testing', 'assignee': 'QA Team', 'start': '2024-03-01', 'due': '2024-03-30', 'status': 'Pending', 'progress': 0}
            ])
            
            for row, task in enumerate(tasks, 2):
                task_sheet.Cells(row, 1).Value = task['id']
                task_sheet.Cells(row, 2).Value = task['name']
                task_sheet.Cells(row, 3).Value = task['assignee']
                task_sheet.Cells(row, 4).Value = task['start']
                task_sheet.Calls(row, 5).Value = task['due']
                task_sheet.Cells(row, 6).Value = task['status']
                task_sheet.Cells(row, 7).Value = f"{task['progress']}%"
            
            # Auto-fit columns
            task_sheet.Columns.AutoFit()
            
            excel_output = os.path.join(output_dir, f"{project_data.get('name', 'project').replace(' ', '_')}_tracker.xlsx")
            await self.excel_handler.save_workbook(workbook, excel_output)
            await self.excel_handler.close_workbook(workbook)
            
            # === STEP 2: GENERATE WORD DOCUMENTATION ===
            word_doc = await self.word_handler.create_document()
            
            # Title
            title_range = word_doc.Range(0, 0)
            title_range.InsertAfter(f"PROJECT DOCUMENTATION\n{project_data.get('name', 'Project Name')}\n")
            title_range.Font.Size = 16
            title_range.Font.Bold = True
            title_range.ParagraphFormat.Alignment = 1
            
            # Content
            content_range = word_doc.Range(word_doc.Content.End - 1, word_doc.Content.End - 1)
            content_text = f"""

PROJECT OVERVIEW

Project Name: {project_data.get('name', 'N/A')}
Project Manager: {project_data.get('manager', 'N/A')}
Start Date: {project_data.get('start_date', 'N/A')}
End Date: {project_data.get('end_date', 'N/A')}
Budget: ${project_data.get('budget', 0):,}
Current Status: {project_data.get('status', 'N/A')}

PROJECT OBJECTIVES

"""
            
            objectives = project_data.get('objectives', [
                'Deliver high-quality solution on time and within budget',
                'Improve operational efficiency by 25%',
                'Enhance user experience and satisfaction',
                'Ensure scalability for future growth'
            ])
            
            for obj in objectives:
                content_text += f"• {obj}\n"
            
            content_text += "\nPROJECT SCOPE\n\n"
            content_text += project_data.get('scope', 'Project scope description goes here.')
            
            content_text += "\n\nKEY DELIVERABLES\n\n"
            
            deliverables = project_data.get('deliverables', [
                'Requirements Documentation',
                'System Architecture Design',
                'Application Development',
                'Testing and Quality Assurance',
                'User Training and Documentation',
                'Production Deployment'
            ])
            
            for deliverable in deliverables:
                content_text += f"• {deliverable}\n"
            
            content_range.InsertAfter(content_text)
            content_range.Font.Size = 11
            
            word_output = os.path.join(output_dir, f"{project_data.get('name', 'project').replace(' ', '_')}_documentation.docx")
            await self.word_handler.save_document(word_doc, word_output)
            await self.word_handler.close_document(word_doc)
            
            # === STEP 3: GENERATE POWERPOINT PRESENTATION ===
            presentation = await self.powerpoint_handler.create_presentation()
            
            # Slide 1: Title
            title_slide = presentation.Slides(1)
            title_slide.Shapes.Title.TextFrame.TextRange.Text = f"Project Presentation\n{project_data.get('name', 'Project Name')}"
            title_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = f"""
Project Manager: {project_data.get('manager', 'Manager Name')}
{datetime.now().strftime('%B %Y')}
"""
            
            # Slide 2: Project Overview
            overview_slide = presentation.Slides.Add(2, 2)
            overview_slide.Shapes.Title.TextFrame.TextRange.Text = "Project Overview"
            
            overview_text = f"""
Duration: {project_data.get('start_date', 'Start')} - {project_data.get('end_date', 'End')}
Budget: ${project_data.get('budget', 0):,}
Status: {project_data.get('status', 'In Progress')}

Key Objectives:
• {objectives[0] if objectives else 'Primary objective'}
• {objectives[1] if len(objectives) > 1 else 'Secondary objective'}
• {objectives[2] if len(objectives) > 2 else 'Additional objective'}
"""
            
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = overview_text
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            
            # Slide 3: Progress Status
            progress_slide = presentation.Slides.Add(3, 2)
            progress_slide.Shapes.Title.TextFrame.TextRange.Text = "Current Progress"
            
            completed_tasks = len([t for t in tasks if t['status'] == 'Complete'])
            total_tasks = len(tasks)
            progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            
            progress_text = f"""
Overall Progress: {progress_percentage:.0f}%

Task Status:
• Completed: {completed_tasks} tasks
• In Progress: {len([t for t in tasks if t['status'] == 'In Progress'])} tasks
• Pending: {len([t for t in tasks if t['status'] == 'Pending'])} tasks

Next Milestones:
• {tasks[2]['name'] if len(tasks) > 2 else 'Upcoming milestone'}
• {tasks[3]['name'] if len(tasks) > 3 else 'Future milestone'}
"""
            
            progress_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = progress_text
            progress_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            
            ppt_output = os.path.join(output_dir, f"{project_data.get('name', 'project').replace(' ', '_')}_presentation.pptx")
            await self.powerpoint_handler.save_presentation(presentation, ppt_output)
            
            logger.info(f"Project documentation workflow selesai. Output: {excel_output}, {word_output}, {ppt_output}")
            
            return {
                'excel_tracker': excel_output,
                'word_documentation': word_output,
                'powerpoint_presentation': ppt_output,
                'progress_percentage': progress_percentage
            }
            
        except Exception as e:
            logger.error(f"Error dalam project documentation workflow: {e}")
            raise

# Contoh penggunaan
async def main():
    """Contoh penggunaan Cross-Office Workflows."""
    workflows = CrossOfficeWorkflows()
    
    # Pastikan output directory ada
    output_dir = "workflow_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Cross-Office Workflows Cookbook siap digunakan!")
    print("\nContoh workflows yang tersedia:")
    print("1. sales_report_workflow() - Analisis sales dari Excel ke Word & PowerPoint")
    print("2. employee_review_workflow() - Performance review lengkap")
    print("3. project_documentation_workflow() - Dokumentasi proyek komprehensif")
    print("\nUncomment contoh di bawah untuk menjalankan workflow.")
    
    # Contoh employee review
    # employee_data = {
    #     'name': 'John Smith',
    #     'position': 'Senior Sales Manager',
    #     'department': 'Sales',
    #     'review_period': 'Q4 2024',
    #     'reviewer': 'Sarah Johnson',
    #     'metrics': [
    #         {'name': 'Sales Target Achievement', 'target': 150000, 'actual': 175000},
    #         {'name': 'Customer Satisfaction', 'target': 90, 'actual': 94},
    #         {'name': 'Team Leadership', 'target': 85, 'actual': 92}
    #     ],
    #     'strengths': [
    #         'Consistently exceeds sales targets',
    #         'Excellent customer relationship management',
    #         'Strong mentoring skills for junior staff'
    #     ],
    #     'goals': [
    #         'Complete advanced leadership training',
    #         'Expand client base by 20%',
    #         'Implement new CRM processes'
    #     ]
    # }
    # 
    # result = await workflows.employee_review_workflow(employee_data, output_dir)
    # print(f"Employee review completed: {result}")

if __name__ == "__main__":
    asyncio.run(main())