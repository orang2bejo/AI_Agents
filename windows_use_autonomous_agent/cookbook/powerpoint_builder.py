#!/usr/bin/env python3
"""
🎯 PowerPoint Presentation Builder Cookbook

Contoh praktis untuk membuat presentasi PowerPoint otomatis menggunakan Jarvis AI.
Script ini mendemonstrasikan pembuatan berbagai jenis presentasi dengan slide dan konten.

Author: Orangbejo
GitHub: https://github.com/Orangbejo
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from windows_use.office import PowerPointHandler
from windows_use.observability.logger import setup_logger

logger = setup_logger(__name__)

class PowerPointBuilder:
    """Builder untuk membuat berbagai jenis presentasi PowerPoint."""
    
    def __init__(self):
        self.powerpoint_handler = PowerPointHandler()
        
    async def create_business_presentation(self, presentation_data: dict, output_file: str):
        """
        Membuat presentasi bisnis dengan:
        - Title slide
        - Agenda
        - Content slides
        - Charts and graphs
        - Conclusion
        """
        try:
            logger.info(f"Membuat business presentation: {presentation_data.get('title', 'Presentation')}")
            
            # Buat presentasi baru
            presentation = await self.powerpoint_handler.create_presentation()
            
            # === SLIDE 1: TITLE SLIDE ===
            title_slide = presentation.Slides(1)
            title_slide.Layout = presentation.SlideMaster.CustomLayouts(1)  # Title slide layout
            
            # Title
            title_shape = title_slide.Shapes.Title
            title_shape.TextFrame.TextRange.Text = presentation_data.get('title', 'Business Presentation')
            title_shape.TextFrame.TextRange.Font.Size = 44
            title_shape.TextFrame.TextRange.Font.Bold = True
            
            # Subtitle
            subtitle_shape = title_slide.Shapes.Placeholders(2)
            subtitle_text = f"""{presentation_data.get('subtitle', 'Company Overview')}
{presentation_data.get('presenter', 'Presenter Name')}
{presentation_data.get('date', datetime.now().strftime('%B %d, %Y'))}"""
            subtitle_shape.TextFrame.TextRange.Text = subtitle_text
            subtitle_shape.TextFrame.TextRange.Font.Size = 24
            
            # === SLIDE 2: AGENDA ===
            agenda_slide = presentation.Slides.Add(2, 2)  # Content layout
            agenda_slide.Shapes.Title.TextFrame.TextRange.Text = "Agenda"
            
            agenda_items = presentation_data.get('agenda', [
                'Company Overview',
                'Market Analysis',
                'Financial Performance',
                'Strategic Initiatives',
                'Q&A Session'
            ])
            
            content_shape = agenda_slide.Shapes.Placeholders(2)
            agenda_text = "\n".join([f"• {item}" for item in agenda_items])
            content_shape.TextFrame.TextRange.Text = agenda_text
            content_shape.TextFrame.TextRange.Font.Size = 24
            
            # === SLIDE 3: COMPANY OVERVIEW ===
            overview_slide = presentation.Slides.Add(3, 2)
            overview_slide.Shapes.Title.TextFrame.TextRange.Text = "Company Overview"
            
            overview_content = presentation_data.get('overview', {
                'mission': 'To deliver innovative solutions that drive business success',
                'vision': 'To be the leading provider in our industry',
                'founded': '2010',
                'employees': '500+',
                'locations': '15 countries'
            })
            
            overview_text = f"""
Mission: {overview_content['mission']}

Vision: {overview_content['vision']}

Key Facts:
• Founded: {overview_content['founded']}
• Employees: {overview_content['employees']}
• Global Presence: {overview_content['locations']}
"""
            
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = overview_text
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            # === SLIDE 4: FINANCIAL PERFORMANCE ===
            financial_slide = presentation.Slides.Add(4, 2)
            financial_slide.Shapes.Title.TextFrame.TextRange.Text = "Financial Performance"
            
            financial_data = presentation_data.get('financial', {
                'revenue_2023': 50000000,
                'revenue_2022': 45000000,
                'growth_rate': 11.1,
                'profit_margin': 15.5
            })
            
            financial_text = f"""
Revenue Growth:
• 2023: ${financial_data['revenue_2023']:,}
• 2022: ${financial_data['revenue_2022']:,}
• Growth Rate: {financial_data['growth_rate']}%

Key Metrics:
• Profit Margin: {financial_data['profit_margin']}%
• Market Position: Strong
• Customer Satisfaction: 95%
"""
            
            financial_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = financial_text
            financial_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            # === SLIDE 5: STRATEGIC INITIATIVES ===
            strategy_slide = presentation.Slides.Add(5, 2)
            strategy_slide.Shapes.Title.TextFrame.TextRange.Text = "Strategic Initiatives"
            
            initiatives = presentation_data.get('initiatives', [
                'Digital Transformation Program',
                'Market Expansion into Asia-Pacific',
                'Sustainability and Green Operations',
                'Innovation Lab Development',
                'Strategic Partnerships'
            ])
            
            initiatives_text = "\n".join([f"• {initiative}" for initiative in initiatives])
            strategy_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = initiatives_text
            strategy_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 22
            
            # === SLIDE 6: CONCLUSION ===
            conclusion_slide = presentation.Slides.Add(6, 2)
            conclusion_slide.Shapes.Title.TextFrame.TextRange.Text = "Conclusion"
            
            conclusion_text = presentation_data.get('conclusion', """
• Strong financial performance with consistent growth
• Clear strategic direction for future expansion
• Committed to innovation and customer satisfaction
• Well-positioned for continued success

Thank you for your attention!
""")
            
            conclusion_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = conclusion_text
            conclusion_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 22
            
            # === SLIDE 7: Q&A ===
            qa_slide = presentation.Slides.Add(7, 11)  # Blank layout
            
            # Add title manually for blank layout
            qa_title = qa_slide.Shapes.AddTextbox(
                1,  # Orientation
                50,  # Left
                50,  # Top
                600,  # Width
                100   # Height
            )
            qa_title.TextFrame.TextRange.Text = "Questions & Answers"
            qa_title.TextFrame.TextRange.Font.Size = 48
            qa_title.TextFrame.TextRange.Font.Bold = True
            qa_title.TextFrame.TextRange.ParagraphFormat.Alignment = 2  # Center
            
            # Add contact info
            contact_info = qa_slide.Shapes.AddTextbox(
                1,  # Orientation
                100,  # Left
                300,  # Top
                500,  # Width
                200   # Height
            )
            
            contact_text = f"""
Contact Information:
{presentation_data.get('contact_name', 'John Doe')}
{presentation_data.get('contact_email', 'john.doe@company.com')}
{presentation_data.get('contact_phone', '+1 (555) 123-4567')}
"""
            
            contact_info.TextFrame.TextRange.Text = contact_text
            contact_info.TextFrame.TextRange.Font.Size = 20
            contact_info.TextFrame.TextRange.ParagraphFormat.Alignment = 2  # Center
            
            await self.powerpoint_handler.save_presentation(presentation, output_file)
            logger.info(f"Business presentation berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat business presentation: {e}")
            raise
    
    async def create_project_status_presentation(self, project_data: dict, output_file: str):
        """
        Membuat presentasi status proyek dengan:
        - Project overview
        - Timeline and milestones
        - Progress indicators
        - Issues and risks
        - Next steps
        """
        try:
            logger.info(f"Membuat project status presentation: {project_data.get('name', 'Project')}")
            
            presentation = await self.powerpoint_handler.create_presentation()
            
            # === SLIDE 1: TITLE ===
            title_slide = presentation.Slides(1)
            title_slide.Shapes.Title.TextFrame.TextRange.Text = f"Project Status Report\n{project_data.get('name', 'Project Name')}"
            title_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = f"""
Status as of {datetime.now().strftime('%B %d, %Y')}
Project Manager: {project_data.get('pm', 'PM Name')}
"""
            
            # === SLIDE 2: PROJECT OVERVIEW ===
            overview_slide = presentation.Slides.Add(2, 2)
            overview_slide.Shapes.Title.TextFrame.TextRange.Text = "Project Overview"
            
            overview_text = f"""
Project: {project_data.get('name', 'Project Name')}
Start Date: {project_data.get('start_date', 'TBD')}
End Date: {project_data.get('end_date', 'TBD')}
Budget: ${project_data.get('budget', 0):,}
Team Size: {project_data.get('team_size', 'TBD')} members

Objectives:
{chr(10).join([f'• {obj}' for obj in project_data.get('objectives', ['Objective 1', 'Objective 2'])])}
"""
            
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = overview_text
            overview_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            
            # === SLIDE 3: PROGRESS STATUS ===
            progress_slide = presentation.Slides.Add(3, 2)
            progress_slide.Shapes.Title.TextFrame.TextRange.Text = "Progress Status"
            
            progress_data = project_data.get('progress', {
                'overall': 65,
                'planning': 100,
                'development': 70,
                'testing': 30,
                'deployment': 0
            })
            
            progress_text = f"""
Overall Progress: {progress_data['overall']}%

Phase Breakdown:
• Planning: {progress_data['planning']}% ✓
• Development: {progress_data['development']}% 🔄
• Testing: {progress_data['testing']}% 🔄
• Deployment: {progress_data['deployment']}% ⏳

Status: {'On Track' if progress_data['overall'] >= 60 else 'At Risk'}
"""
            
            progress_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = progress_text
            progress_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            # === SLIDE 4: MILESTONES ===
            milestones_slide = presentation.Slides.Add(4, 2)
            milestones_slide.Shapes.Title.TextFrame.TextRange.Text = "Key Milestones"
            
            milestones = project_data.get('milestones', [
                {'name': 'Project Kickoff', 'date': '2024-01-01', 'status': 'Complete'},
                {'name': 'Requirements Finalized', 'date': '2024-01-15', 'status': 'Complete'},
                {'name': 'Development Phase 1', 'date': '2024-02-28', 'status': 'In Progress'},
                {'name': 'Testing Phase', 'date': '2024-03-15', 'status': 'Upcoming'},
                {'name': 'Go-Live', 'date': '2024-04-01', 'status': 'Upcoming'}
            ])
            
            milestone_text = "\n".join([
                f"• {m['name']} - {m['date']} ({m['status']})"
                for m in milestones
            ])
            
            milestones_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = milestone_text
            milestones_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            # === SLIDE 5: ISSUES & RISKS ===
            issues_slide = presentation.Slides.Add(5, 2)
            issues_slide.Shapes.Title.TextFrame.TextRange.Text = "Issues & Risks"
            
            issues = project_data.get('issues', [
                {'type': 'Risk', 'description': 'Potential delay in third-party integration', 'impact': 'Medium'},
                {'type': 'Issue', 'description': 'Resource availability for testing phase', 'impact': 'High'},
                {'type': 'Risk', 'description': 'Budget overrun if scope increases', 'impact': 'Low'}
            ])
            
            issues_text = "\n".join([
                f"• {issue['type']}: {issue['description']} (Impact: {issue['impact']})"
                for issue in issues
            ])
            
            issues_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = issues_text
            issues_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            
            # === SLIDE 6: NEXT STEPS ===
            next_steps_slide = presentation.Slides.Add(6, 2)
            next_steps_slide.Shapes.Title.TextFrame.TextRange.Text = "Next Steps"
            
            next_steps = project_data.get('next_steps', [
                'Complete development phase 1',
                'Begin user acceptance testing',
                'Finalize deployment plan',
                'Conduct team training sessions',
                'Prepare go-live checklist'
            ])
            
            next_steps_text = "\n".join([f"• {step}" for step in next_steps])
            next_steps_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = next_steps_text
            next_steps_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 22
            
            await self.powerpoint_handler.save_presentation(presentation, output_file)
            logger.info(f"Project status presentation berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat project status presentation: {e}")
            raise
    
    async def create_training_presentation(self, training_data: dict, output_file: str):
        """
        Membuat presentasi training dengan:
        - Learning objectives
        - Course outline
        - Content modules
        - Exercises and examples
        - Summary and resources
        """
        try:
            logger.info(f"Membuat training presentation: {training_data.get('title', 'Training')}")
            
            presentation = await self.powerpoint_handler.create_presentation()
            
            # === SLIDE 1: TITLE ===
            title_slide = presentation.Slides(1)
            title_slide.Shapes.Title.TextFrame.TextRange.Text = training_data.get('title', 'Training Session')
            title_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = f"""
{training_data.get('subtitle', 'Professional Development')}
Instructor: {training_data.get('instructor', 'Instructor Name')}
Duration: {training_data.get('duration', '2 hours')}
{datetime.now().strftime('%B %d, %Y')}
"""
            
            # === SLIDE 2: LEARNING OBJECTIVES ===
            objectives_slide = presentation.Slides.Add(2, 2)
            objectives_slide.Shapes.Title.TextFrame.TextRange.Text = "Learning Objectives"
            
            objectives = training_data.get('objectives', [
                'Understand key concepts and principles',
                'Apply learned skills in practical scenarios',
                'Identify best practices and common pitfalls',
                'Develop confidence in using new tools'
            ])
            
            objectives_text = "By the end of this session, you will be able to:\n\n" + "\n".join([f"• {obj}" for obj in objectives])
            objectives_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = objectives_text
            objectives_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
            
            # === SLIDE 3: COURSE OUTLINE ===
            outline_slide = presentation.Slides.Add(3, 2)
            outline_slide.Shapes.Title.TextFrame.TextRange.Text = "Course Outline"
            
            modules = training_data.get('modules', [
                {'name': 'Introduction and Overview', 'duration': '15 min'},
                {'name': 'Core Concepts', 'duration': '30 min'},
                {'name': 'Practical Examples', 'duration': '45 min'},
                {'name': 'Hands-on Exercise', 'duration': '20 min'},
                {'name': 'Q&A and Wrap-up', 'duration': '10 min'}
            ])
            
            outline_text = "\n".join([
                f"• {module['name']} ({module['duration']})"
                for module in modules
            ])
            
            outline_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = outline_text
            outline_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 22
            
            # === CONTENT SLIDES ===
            content_sections = training_data.get('content', [
                {
                    'title': 'Introduction',
                    'content': 'Welcome to the training session. Today we will cover essential concepts and practical applications.'
                },
                {
                    'title': 'Key Concepts',
                    'content': 'Understanding the fundamental principles is crucial for successful implementation.'
                }
            ])
            
            slide_num = 4
            for section in content_sections:
                content_slide = presentation.Slides.Add(slide_num, 2)
                content_slide.Shapes.Title.TextFrame.TextRange.Text = section['title']
                content_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = section['content']
                content_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 20
                slide_num += 1
            
            # === EXERCISE SLIDE ===
            exercise_slide = presentation.Slides.Add(slide_num, 2)
            exercise_slide.Shapes.Title.TextFrame.TextRange.Text = "Hands-on Exercise"
            
            exercise_text = training_data.get('exercise', """
Exercise Instructions:

1. Form groups of 3-4 people
2. Review the provided scenario
3. Apply the concepts we've learned
4. Prepare a 5-minute presentation
5. Share your findings with the class

Time Allocated: 20 minutes
""")
            
            exercise_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = exercise_text
            exercise_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            slide_num += 1
            
            # === SUMMARY SLIDE ===
            summary_slide = presentation.Slides.Add(slide_num, 2)
            summary_slide.Shapes.Title.TextFrame.TextRange.Text = "Summary"
            
            summary_text = training_data.get('summary', """
Key Takeaways:
• Learned fundamental concepts and principles
• Practiced applying skills in real scenarios
• Identified best practices and common mistakes
• Built confidence through hands-on exercises

Next Steps:
• Practice with provided materials
• Apply concepts in your daily work
• Reach out for additional support if needed
""")
            
            summary_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = summary_text
            summary_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            slide_num += 1
            
            # === RESOURCES SLIDE ===
            resources_slide = presentation.Slides.Add(slide_num, 2)
            resources_slide.Shapes.Title.TextFrame.TextRange.Text = "Additional Resources"
            
            resources = training_data.get('resources', [
                'Training materials: Available on company portal',
                'Reference guide: Attached to this presentation',
                'Online tutorials: Links provided in handout',
                'Support contact: training@company.com',
                'Follow-up session: Scheduled for next month'
            ])
            
            resources_text = "\n".join([f"• {resource}" for resource in resources])
            resources_slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = resources_text
            resources_slide.Shapes.Placeholders(2).TextFrame.TextRange.Font.Size = 18
            
            await self.powerpoint_handler.save_presentation(presentation, output_file)
            logger.info(f"Training presentation berhasil dibuat: {output_file}")
            
        except Exception as e:
            logger.error(f"Error membuat training presentation: {e}")
            raise

# Contoh penggunaan
async def main():
    """Contoh penggunaan PowerPoint Builder."""
    builder = PowerPointBuilder()
    
    # Contoh 1: Business Presentation
    business_data = {
        'title': 'Annual Business Review 2024',
        'subtitle': 'Growth, Innovation, and Future Outlook',
        'presenter': 'CEO John Smith',
        'date': 'March 15, 2024',
        'agenda': [
            'Company Performance Overview',
            'Market Position Analysis',
            'Financial Highlights',
            'Strategic Initiatives 2024',
            'Future Growth Plans'
        ],
        'overview': {
            'mission': 'To deliver innovative technology solutions that transform businesses',
            'vision': 'To be the global leader in digital transformation',
            'founded': '2015',
            'employees': '1,200+',
            'locations': '25 countries'
        },
        'financial': {
            'revenue_2023': 125000000,
            'revenue_2022': 98000000,
            'growth_rate': 27.6,
            'profit_margin': 18.2
        },
        'contact_name': 'Sarah Johnson',
        'contact_email': 'sarah.johnson@company.com',
        'contact_phone': '+1 (555) 987-6543'
    }
    
    # await builder.create_business_presentation(
    #     business_data,
    #     "presentations/business_review_2024.pptx"
    # )
    
    # Contoh 2: Project Status
    project_data = {
        'name': 'Digital Platform Modernization',
        'pm': 'Alice Chen',
        'start_date': '2024-01-01',
        'end_date': '2024-06-30',
        'budget': 500000,
        'team_size': 12,
        'objectives': [
            'Modernize legacy systems',
            'Improve user experience',
            'Enhance system performance',
            'Reduce operational costs'
        ],
        'progress': {
            'overall': 75,
            'planning': 100,
            'development': 85,
            'testing': 60,
            'deployment': 20
        }
    }
    
    # await builder.create_project_status_presentation(
    #     project_data,
    #     "presentations/project_status.pptx"
    # )
    
    # Contoh 3: Training Session
    training_data = {
        'title': 'Advanced Excel Techniques',
        'subtitle': 'Data Analysis and Automation',
        'instructor': 'Dr. Maria Rodriguez',
        'duration': '3 hours',
        'objectives': [
            'Master advanced Excel formulas and functions',
            'Create dynamic charts and dashboards',
            'Automate repetitive tasks with macros',
            'Implement data validation and error checking'
        ],
        'content': [
            {
                'title': 'Advanced Formulas',
                'content': 'Learn VLOOKUP, INDEX/MATCH, array formulas, and conditional functions for complex data analysis.'
            },
            {
                'title': 'Data Visualization',
                'content': 'Create compelling charts, pivot tables, and interactive dashboards to present data effectively.'
            }
        ]
    }
    
    # await builder.create_training_presentation(
    #     training_data,
    #     "presentations/excel_training.pptx"
    # )
    
    print("PowerPoint Builder Cookbook siap digunakan!")
    print("Uncomment contoh di atas untuk menjalankan builder.")

if __name__ == "__main__":
    asyncio.run(main())