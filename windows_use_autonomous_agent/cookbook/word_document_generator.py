#!/usr/bin/env python3
"""
📄 Word Document Generator Cookbook

Contoh praktis untuk membuat dokumen Word otomatis menggunakan Jarvis AI.
Script ini mendemonstrasikan pembuatan berbagai jenis dokumen dengan formatting dan struktur.

Author: Orangbejo
GitHub: https://github.com/Orangbejo
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from windows_use.office import WordHandler
from windows_use.observability.logger import setup_logger

logger = setup_logger(__name__)

class WordDocumentGenerator:
    """Generator untuk membuat berbagai jenis dokumen Word."""
    
    def __init__(self):
        self.word_handler = WordHandler()
        
    async def create_business_proposal(self, client_data: dict, output_file: str):
        """
        Membuat proposal bisnis dengan:
        - Cover page
        - Executive summary
        - Project details
        - Timeline
        - Budget breakdown
        """
        try:
            logger.info(f"Membuat business proposal untuk {client_data.get('company', 'Client')}")
            
            # Buat dokumen baru
            doc = await self.word_handler.create_document()
            
            # === COVER PAGE ===
            # Title
            title_paragraph = doc.Paragraphs.Add()
            title_paragraph.Range.Text = "BUSINESS PROPOSAL"
            title_paragraph.Range.Font.Size = 24
            title_paragraph.Range.Font.Bold = True
            title_paragraph.Alignment = 1  # Center alignment
            
            # Subtitle
            subtitle_paragraph = doc.Paragraphs.Add()
            subtitle_paragraph.Range.Text = f"For {client_data.get('company', 'Your Company')}"
            subtitle_paragraph.Range.Font.Size = 16
            subtitle_paragraph.Alignment = 1
            
            # Date
            date_paragraph = doc.Paragraphs.Add()
            date_paragraph.Range.Text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
            date_paragraph.Range.Font.Size = 12
            date_paragraph.Alignment = 1
            
            # Add page break
            doc.Paragraphs.Add().Range.InsertBreak(7)  # Page break
            
            # === EXECUTIVE SUMMARY ===
            summary_heading = doc.Paragraphs.Add()
            summary_heading.Range.Text = "EXECUTIVE SUMMARY"
            summary_heading.Range.Font.Size = 16
            summary_heading.Range.Font.Bold = True
            summary_heading.SpaceAfter = 12
            
            summary_content = doc.Paragraphs.Add()
            summary_text = f"""
We are pleased to present this comprehensive proposal for {client_data.get('project_name', 'your project')}. 
Our team has extensive experience in {client_data.get('industry', 'this industry')} and we are confident 
that we can deliver exceptional results that exceed your expectations.

This proposal outlines our understanding of your requirements, our proposed solution, 
timeline, and investment details. We look forward to the opportunity to work with 
{client_data.get('company', 'your organization')} and contribute to your success.
"""
            summary_content.Range.Text = summary_text
            summary_content.Range.Font.Size = 11
            summary_content.SpaceAfter = 18
            
            # === PROJECT OVERVIEW ===
            overview_heading = doc.Paragraphs.Add()
            overview_heading.Range.Text = "PROJECT OVERVIEW"
            overview_heading.Range.Font.Size = 16
            overview_heading.Range.Font.Bold = True
            overview_heading.SpaceAfter = 12
            
            # Project Name
            project_name_para = doc.Paragraphs.Add()
            project_name_para.Range.Text = f"Project Name: {client_data.get('project_name', 'TBD')}"
            project_name_para.Range.Font.Bold = True
            project_name_para.SpaceAfter = 6
            
            # Project Description
            description_para = doc.Paragraphs.Add()
            description_para.Range.Text = f"Description: {client_data.get('description', 'Project description to be defined.')}"
            description_para.SpaceAfter = 6
            
            # Objectives
            objectives_para = doc.Paragraphs.Add()
            objectives_para.Range.Text = "Objectives:"
            objectives_para.Range.Font.Bold = True
            objectives_para.SpaceAfter = 6
            
            objectives = client_data.get('objectives', [
                'Deliver high-quality solution',
                'Meet project timeline',
                'Ensure client satisfaction',
                'Provide ongoing support'
            ])
            
            for objective in objectives:
                obj_para = doc.Paragraphs.Add()
                obj_para.Range.Text = f"• {objective}"
                obj_para.LeftIndent = 20
                obj_para.SpaceAfter = 3
            
            # === SCOPE OF WORK ===
            scope_heading = doc.Paragraphs.Add()
            scope_heading.Range.Text = "SCOPE OF WORK"
            scope_heading.Range.Font.Size = 16
            scope_heading.Range.Font.Bold = True
            scope_heading.SpaceAfter = 12
            scope_heading.SpaceBefore = 18
            
            scope_items = client_data.get('scope', [
                'Requirements analysis and documentation',
                'System design and architecture',
                'Development and implementation',
                'Testing and quality assurance',
                'Deployment and go-live support',
                'Training and knowledge transfer',
                'Post-implementation support'
            ])
            
            for i, item in enumerate(scope_items, 1):
                scope_para = doc.Paragraphs.Add()
                scope_para.Range.Text = f"{i}. {item}"
                scope_para.SpaceAfter = 6
            
            # === TIMELINE ===
            timeline_heading = doc.Paragraphs.Add()
            timeline_heading.Range.Text = "PROJECT TIMELINE"
            timeline_heading.Range.Font.Size = 16
            timeline_heading.Range.Font.Bold = True
            timeline_heading.SpaceAfter = 12
            timeline_heading.SpaceBefore = 18
            
            # Create timeline table
            timeline_table = doc.Tables.Add(
                doc.Paragraphs.Add().Range,
                4,  # rows
                3   # columns
            )
            
            # Table headers
            timeline_table.Cell(1, 1).Range.Text = "Phase"
            timeline_table.Cell(1, 2).Range.Text = "Duration"
            timeline_table.Cell(1, 3).Range.Text = "Deliverables"
            
            # Make headers bold
            for col in range(1, 4):
                timeline_table.Cell(1, col).Range.Font.Bold = True
            
            # Timeline data
            timeline_data = [
                ["Planning & Analysis", "2 weeks", "Requirements document, Project plan"],
                ["Development", "6 weeks", "Working system, Documentation"],
                ["Testing & Deployment", "2 weeks", "Tested system, Go-live support"]
            ]
            
            for i, (phase, duration, deliverables) in enumerate(timeline_data, 2):
                timeline_table.Cell(i, 1).Range.Text = phase
                timeline_table.Cell(i, 2).Range.Text = duration
                timeline_table.Cell(i, 3).Range.Text = deliverables
            
            # Format table
            timeline_table.AutoFitBehavior(2)  # AutoFit to contents
            
            # === INVESTMENT ===
            investment_heading = doc.Paragraphs.Add()
            investment_heading.Range.Text = "INVESTMENT"
            investment_heading.Range.Font.Size = 16
            investment_heading.Range.Font.Bold = True
            investment_heading.SpaceAfter = 12
            investment_heading.SpaceBefore = 18
            
            # Investment table
            investment_table = doc.Tables.Add(
                doc.Paragraphs.Add().Range,
                5,  # rows
                3   # columns
            )
            
            # Headers
            investment_table.Cell(1, 1).Range.Text = "Item"
            investment_table.Cell(1, 2).Range.Text = "Description"
            investment_table.Cell(1, 3).Range.Text = "Amount"
            
            # Make headers bold
            for col in range(1, 4):
                investment_table.Cell(1, col).Range.Font.Bold = True
            
            # Investment data
            budget = client_data.get('budget', {
                'development': 50000,
                'testing': 10000,
                'deployment': 5000
            })
            
            investment_data = [
                ["Development", "Core system development", f"${budget.get('development', 50000):,}"],
                ["Testing", "Quality assurance and testing", f"${budget.get('testing', 10000):,}"],
                ["Deployment", "System deployment and support", f"${budget.get('deployment', 5000):,}"],
                ["TOTAL", "", f"${sum(budget.values()):,}"]
            ]
            
            for i, (item, description, amount) in enumerate(investment_data, 2):
                investment_table.Cell(i, 1).Range.Text = item
                investment_table.Cell(i, 2).Range.Text = description
                investment_table.Cell(i, 3).Range.Text = amount
                
                if item == "TOTAL":
                    for col in range(1, 4):
                        investment_table.Cell(i, col).Range.Font.Bold = True
            
            investment_table.AutoFitBehavior(2)
            
            # === NEXT STEPS ===
            next_steps_heading = doc.Paragraphs.Add()
            next_steps_heading.Range.Text = "NEXT STEPS"
            next_steps_heading.Range.Font.Size = 16
            next_steps_heading.Range.Font.Bold = True
            next_steps_heading.SpaceAfter = 12
            next_steps_heading.SpaceBefore = 18
            
            next_steps = [
                "Review and approve this proposal",
                "Sign the project agreement",
                "Schedule kick-off meeting",
                "Begin project execution"
            ]
            
            for i, step in enumerate(next_steps, 1):
                step_para = doc.Paragraphs.Add()
                step_para.Range.Text = f"{i}. {step}"
                step_para.SpaceAfter = 6
            
            # === CONTACT INFORMATION ===
            contact_heading = doc.Paragraphs.Add()
            contact_heading.Range.Text = "CONTACT INFORMATION"
            contact_heading.Range.Font.Size = 16
            contact_heading.Range.Font.Bold = True
            contact_heading.SpaceAfter = 12
            contact_heading.SpaceBefore = 18
            
            contact_para = doc.Paragraphs.Add()
            contact_text = f"""
For any questions or clarifications regarding this proposal, please contact:

Project Manager: {client_data.get('pm_name', 'John Doe')}
Email: {client_data.get('pm_email', 'john.doe@company.com')}
Phone: {client_data.get('pm_phone', '+1 (555) 123-4567')}

We appreciate the opportunity to work with {client_data.get('company', 'your organization')} 
and look forward to your response.
"""
            contact_para.Range.Text = contact_text
            
            await self.word_handler.save_document(doc, output_file)
            logger.info(f"Business proposal berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat business proposal: {e}")
            raise
    
    async def create_meeting_minutes(self, meeting_data: dict, output_file: str):
        """
        Membuat notulen rapat dengan:
        - Meeting details
        - Attendees list
        - Agenda items
        - Action items
        - Next meeting info
        """
        try:
            logger.info(f"Membuat meeting minutes untuk {meeting_data.get('title', 'Meeting')}")
            
            doc = await self.word_handler.create_document()
            
            # === HEADER ===
            header_para = doc.Paragraphs.Add()
            header_para.Range.Text = "MEETING MINUTES"
            header_para.Range.Font.Size = 18
            header_para.Range.Font.Bold = True
            header_para.Alignment = 1  # Center
            header_para.SpaceAfter = 18
            
            # === MEETING DETAILS ===
            details_table = doc.Tables.Add(
                doc.Paragraphs.Add().Range,
                6,  # rows
                2   # columns
            )
            
            # Meeting details data
            details_data = [
                ["Meeting Title:", meeting_data.get('title', 'Regular Team Meeting')],
                ["Date:", meeting_data.get('date', datetime.now().strftime('%B %d, %Y'))],
                ["Time:", meeting_data.get('time', '10:00 AM - 11:00 AM')],
                ["Location:", meeting_data.get('location', 'Conference Room A')],
                ["Chairperson:", meeting_data.get('chairperson', 'TBD')],
                ["Secretary:", meeting_data.get('secretary', 'TBD')]
            ]
            
            for i, (label, value) in enumerate(details_data, 1):
                details_table.Cell(i, 1).Range.Text = label
                details_table.Cell(i, 1).Range.Font.Bold = True
                details_table.Cell(i, 2).Range.Text = value
            
            details_table.AutoFitBehavior(2)
            
            # === ATTENDEES ===
            attendees_heading = doc.Paragraphs.Add()
            attendees_heading.Range.Text = "ATTENDEES"
            attendees_heading.Range.Font.Size = 14
            attendees_heading.Range.Font.Bold = True
            attendees_heading.SpaceAfter = 12
            attendees_heading.SpaceBefore = 18
            
            attendees = meeting_data.get('attendees', [
                'John Doe - Project Manager',
                'Jane Smith - Developer',
                'Bob Johnson - QA Lead',
                'Alice Brown - Business Analyst'
            ])
            
            for attendee in attendees:
                attendee_para = doc.Paragraphs.Add()
                attendee_para.Range.Text = f"• {attendee}"
                attendee_para.LeftIndent = 20
                attendee_para.SpaceAfter = 3
            
            # === AGENDA & DISCUSSIONS ===
            agenda_heading = doc.Paragraphs.Add()
            agenda_heading.Range.Text = "AGENDA & DISCUSSIONS"
            agenda_heading.Range.Font.Size = 14
            agenda_heading.Range.Font.Bold = True
            agenda_heading.SpaceAfter = 12
            agenda_heading.SpaceBefore = 18
            
            agenda_items = meeting_data.get('agenda', [
                {
                    'topic': 'Project Status Update',
                    'discussion': 'Current progress is on track. All milestones met so far.',
                    'presenter': 'John Doe'
                },
                {
                    'topic': 'Budget Review',
                    'discussion': 'Budget utilization at 60%. No concerns at this time.',
                    'presenter': 'Finance Team'
                },
                {
                    'topic': 'Risk Assessment',
                    'discussion': 'Identified potential delays in testing phase. Mitigation plan discussed.',
                    'presenter': 'Risk Manager'
                }
            ])
            
            for i, item in enumerate(agenda_items, 1):
                # Topic heading
                topic_para = doc.Paragraphs.Add()
                topic_para.Range.Text = f"{i}. {item['topic']}"
                topic_para.Range.Font.Bold = True
                topic_para.Range.Font.Size = 12
                topic_para.SpaceAfter = 6
                
                # Presenter
                presenter_para = doc.Paragraphs.Add()
                presenter_para.Range.Text = f"Presenter: {item['presenter']}"
                presenter_para.Range.Font.Italic = True
                presenter_para.LeftIndent = 20
                presenter_para.SpaceAfter = 6
                
                # Discussion
                discussion_para = doc.Paragraphs.Add()
                discussion_para.Range.Text = f"Discussion: {item['discussion']}"
                discussion_para.LeftIndent = 20
                discussion_para.SpaceAfter = 12
            
            # === ACTION ITEMS ===
            actions_heading = doc.Paragraphs.Add()
            actions_heading.Range.Text = "ACTION ITEMS"
            actions_heading.Range.Font.Size = 14
            actions_heading.Range.Font.Bold = True
            actions_heading.SpaceAfter = 12
            actions_heading.SpaceBefore = 18
            
            # Action items table
            actions_table = doc.Tables.Add(
                doc.Paragraphs.Add().Range,
                len(meeting_data.get('actions', [])) + 1,  # +1 for header
                4   # columns
            )
            
            # Headers
            actions_table.Cell(1, 1).Range.Text = "Action Item"
            actions_table.Cell(1, 2).Range.Text = "Responsible"
            actions_table.Cell(1, 3).Range.Text = "Due Date"
            actions_table.Cell(1, 4).Range.Text = "Status"
            
            # Make headers bold
            for col in range(1, 5):
                actions_table.Cell(1, col).Range.Font.Bold = True
            
            # Action items data
            actions = meeting_data.get('actions', [
                {
                    'item': 'Update project timeline',
                    'responsible': 'John Doe',
                    'due_date': 'Next Friday',
                    'status': 'Pending'
                },
                {
                    'item': 'Prepare budget report',
                    'responsible': 'Finance Team',
                    'due_date': 'End of week',
                    'status': 'In Progress'
                }
            ])
            
            for i, action in enumerate(actions, 2):
                actions_table.Cell(i, 1).Range.Text = action['item']
                actions_table.Cell(i, 2).Range.Text = action['responsible']
                actions_table.Cell(i, 3).Range.Text = action['due_date']
                actions_table.Cell(i, 4).Range.Text = action['status']
            
            actions_table.AutoFitBehavior(2)
            
            # === NEXT MEETING ===
            next_meeting_heading = doc.Paragraphs.Add()
            next_meeting_heading.Range.Text = "NEXT MEETING"
            next_meeting_heading.Range.Font.Size = 14
            next_meeting_heading.Range.Font.Bold = True
            next_meeting_heading.SpaceAfter = 12
            next_meeting_heading.SpaceBefore = 18
            
            next_meeting_para = doc.Paragraphs.Add()
            next_meeting_text = f"""
Date: {meeting_data.get('next_date', 'TBD')}
Time: {meeting_data.get('next_time', 'TBD')}
Location: {meeting_data.get('next_location', 'TBD')}
Agenda: {meeting_data.get('next_agenda', 'To be determined')}
"""
            next_meeting_para.Range.Text = next_meeting_text
            
            # === FOOTER ===
            footer_para = doc.Paragraphs.Add()
            footer_para.Range.Text = f"\nMinutes prepared by: {meeting_data.get('secretary', 'Secretary')}\nDate: {datetime.now().strftime('%B %d, %Y')}"
            footer_para.SpaceBefore = 18
            footer_para.Range.Font.Italic = True
            
            await self.word_handler.save_document(doc, output_file)
            logger.info(f"Meeting minutes berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat meeting minutes: {e}")
            raise
    
    async def create_contract_template(self, contract_data: dict, output_file: str):
        """
        Membuat template kontrak dengan:
        - Contract header
        - Parties information
        - Terms and conditions
        - Signature section
        """
        try:
            logger.info(f"Membuat contract template: {contract_data.get('type', 'General Contract')}")
            
            doc = await self.word_handler.create_document()
            
            # === HEADER ===
            header_para = doc.Paragraphs.Add()
            header_para.Range.Text = contract_data.get('type', 'SERVICE AGREEMENT').upper()
            header_para.Range.Font.Size = 18
            header_para.Range.Font.Bold = True
            header_para.Alignment = 1  # Center
            header_para.SpaceAfter = 18
            
            # === PARTIES ===
            parties_heading = doc.Paragraphs.Add()
            parties_heading.Range.Text = "PARTIES"
            parties_heading.Range.Font.Size = 14
            parties_heading.Range.Font.Bold = True
            parties_heading.SpaceAfter = 12
            
            parties_para = doc.Paragraphs.Add()
            parties_text = f"""
This agreement is entered into on {contract_data.get('date', datetime.now().strftime('%B %d, %Y'))} between:

PARTY A (Service Provider):
{contract_data.get('party_a', 'Company Name')}
{contract_data.get('party_a_address', 'Address')}

PARTY B (Client):
{contract_data.get('party_b', 'Client Name')}
{contract_data.get('party_b_address', 'Client Address')}
"""
            parties_para.Range.Text = parties_text
            parties_para.SpaceAfter = 18
            
            # === TERMS ===
            terms_heading = doc.Paragraphs.Add()
            terms_heading.Range.Text = "TERMS AND CONDITIONS"
            terms_heading.Range.Font.Size = 14
            terms_heading.Range.Font.Bold = True
            terms_heading.SpaceAfter = 12
            
            terms = contract_data.get('terms', [
                'Scope of Work: Services to be provided as outlined in attached specifications.',
                'Duration: This agreement shall remain in effect for the specified project duration.',
                'Payment Terms: Payment shall be made according to the agreed schedule.',
                'Confidentiality: Both parties agree to maintain confidentiality of sensitive information.',
                'Termination: Either party may terminate this agreement with written notice.',
                'Governing Law: This agreement shall be governed by applicable local laws.'
            ])
            
            for i, term in enumerate(terms, 1):
                term_para = doc.Paragraphs.Add()
                term_para.Range.Text = f"{i}. {term}"
                term_para.SpaceAfter = 12
            
            # === SIGNATURES ===
            signature_heading = doc.Paragraphs.Add()
            signature_heading.Range.Text = "SIGNATURES"
            signature_heading.Range.Font.Size = 14
            signature_heading.Range.Font.Bold = True
            signature_heading.SpaceAfter = 12
            signature_heading.SpaceBefore = 24
            
            # Signature table
            sig_table = doc.Tables.Add(
                doc.Paragraphs.Add().Range,
                3,  # rows
                2   # columns
            )
            
            sig_table.Cell(1, 1).Range.Text = "PARTY A"
            sig_table.Cell(1, 2).Range.Text = "PARTY B"
            
            sig_table.Cell(2, 1).Range.Text = "\n\n_________________________\nSignature"
            sig_table.Cell(2, 2).Range.Text = "\n\n_________________________\nSignature"
            
            sig_table.Cell(3, 1).Range.Text = f"Date: _______________"
            sig_table.Cell(3, 2).Range.Text = f"Date: _______________"
            
            # Make headers bold
            sig_table.Cell(1, 1).Range.Font.Bold = True
            sig_table.Cell(1, 2).Range.Font.Bold = True
            
            sig_table.AutoFitBehavior(2)
            
            await self.word_handler.save_document(doc, output_file)
            logger.info(f"Contract template berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat contract template: {e}")
            raise

# Contoh penggunaan
async def main():
    """Contoh penggunaan Word Document Generator."""
    generator = WordDocumentGenerator()
    
    # Contoh 1: Business Proposal
    client_data = {
        'company': 'ABC Corporation',
        'project_name': 'Digital Transformation Initiative',
        'description': 'Modernize legacy systems and implement cloud-based solutions',
        'industry': 'manufacturing',
        'objectives': [
            'Reduce operational costs by 30%',
            'Improve system efficiency',
            'Enable remote work capabilities',
            'Enhance data security'
        ],
        'budget': {
            'development': 75000,
            'testing': 15000,
            'deployment': 10000
        },
        'pm_name': 'Sarah Johnson',
        'pm_email': 'sarah.johnson@company.com',
        'pm_phone': '+1 (555) 987-6543'
    }
    
    # await generator.create_business_proposal(
    #     client_data,
    #     "documents/business_proposal.docx"
    # )
    
    # Contoh 2: Meeting Minutes
    meeting_data = {
        'title': 'Weekly Project Review',
        'date': 'January 15, 2024',
        'time': '2:00 PM - 3:00 PM',
        'location': 'Conference Room B',
        'chairperson': 'John Smith',
        'secretary': 'Mary Wilson',
        'attendees': [
            'John Smith - Project Manager',
            'Sarah Davis - Lead Developer',
            'Mike Brown - QA Manager',
            'Lisa Chen - Business Analyst'
        ],
        'actions': [
            {
                'item': 'Review test results',
                'responsible': 'Mike Brown',
                'due_date': 'January 20, 2024',
                'status': 'Pending'
            },
            {
                'item': 'Update documentation',
                'responsible': 'Sarah Davis',
                'due_date': 'January 18, 2024',
                'status': 'In Progress'
            }
        ],
        'next_date': 'January 22, 2024',
        'next_time': '2:00 PM',
        'next_location': 'Conference Room B'
    }
    
    # await generator.create_meeting_minutes(
    #     meeting_data,
    #     "documents/meeting_minutes.docx"
    # )
    
    # Contoh 3: Contract Template
    contract_data = {
        'type': 'Software Development Agreement',
        'party_a': 'TechSolutions Inc.\n123 Tech Street\nSan Francisco, CA 94105',
        'party_b': 'Client Company\n456 Business Ave\nNew York, NY 10001',
        'date': 'January 15, 2024'
    }
    
    # await generator.create_contract_template(
    #     contract_data,
    #     "documents/contract_template.docx"
    # )
    
    print("Word Document Generator Cookbook siap digunakan!")
    print("Uncomment contoh di atas untuk menjalankan generator.")

if __name__ == "__main__":
    asyncio.run(main())