"""Complete demonstration of all implemented features.

This example showcases:
- Voice Input & TTS
- Indonesian Language Processing
- Office Automation
- Windows System Tools
- Self-Evolving Agent
- Security & Observability
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Voice and TTS
from windows_use.tools.voice_input import VoiceInput
from windows_use.tools.tts_piper import TTSPiper

# Indonesian Language Processing
# from windows_use.tools.grammar_id import IndonesianGrammar
# from windows_use.tools.router import CommandRouter

# Office Automation
from windows_use.office.excel_handler import ExcelHandler
from windows_use.office.word_handler import WordHandler
from windows_use.office.powerpoint_handler import PowerPointHandler

# Windows System Tools
from windows_use.tools.winget import WingetManager
from windows_use.tools.ps_shell import PowerShellManager
from windows_use.tools.process import ProcessManager
from windows_use.tools.net import NetworkManager

# Self-Evolving Agent
from windows_use.evolution import EvolutionEngine
from windows_use.evolution.memory import ExperienceType
from windows_use.evolution.config import ConfigManager

# Security & Observability
from windows_use.tools.guardrails import GuardrailsEngine
from windows_use.tools.hitl import HITLManager
from windows_use.tools.logger import setup_logger
from windows_use.tools.screenshot import ScreenshotManager


class CompleteDemo:
    """Comprehensive demonstration of all features."""
    
    def __init__(self):
        # Setup logging
        self.logger = setup_logger("complete_demo")
        
        # Initialize components
        self.voice_input = VoiceInput()
        self.tts = TTSPiper()
        self.grammar = IndonesianGrammar()
        self.router = CommandRouter()
        
        # Office automation
        self.excel = ExcelHandler()
        self.word = WordHandler()
        self.powerpoint = PowerPointHandler()
        
        # System tools
        self.winget = WingetManager()
        self.powershell = PowerShellManager()
        self.process_mgr = ProcessManager()
        self.network = NetworkManager()
        
        # Security & Observability
        self.guardrails = GuardrailsEngine()
        self.hitl = HITLManager()
        self.screenshot = ScreenshotManager()
        
        # Evolution engine
        self.config_mgr = ConfigManager()
        self.evolution_config = self.config_mgr.load_config()
        self.evolution_engine = EvolutionEngine(self.evolution_config)
        
    async def run_complete_demo(self):
        """Run the complete demonstration."""
        self.logger.info("Starting complete feature demonstration")
        
        try:
            # Start evolution engine
            await self.evolution_engine.start()
            
            # Demo sections
            await self.demo_voice_and_tts()
            await self.demo_indonesian_processing()
            await self.demo_office_automation()
            await self.demo_system_tools()
            await self.demo_security_features()
            await self.demo_evolution_features()
            
            # Final insights
            await self.show_evolution_insights()
            
        except Exception as e:
            self.logger.error(f"Demo failed: {e}")
        finally:
            await self.evolution_engine.stop()
    
    async def demo_voice_and_tts(self):
        """Demonstrate voice input and text-to-speech features."""
        self.logger.info("=== Voice Input & TTS Demo ===")
        
        # TTS greeting
        greeting = "Selamat datang di demonstrasi lengkap Windows Use Agent"
        self.tts.speak(greeting)
        
        # Setup voice input
        self.voice_input.setup_push_to_talk(key='space')
        
        # Record experience
        await self.evolution_engine.record_experience(
            experience_type=ExperienceType.USER_INTERACTION,
            context="Voice and TTS demo",
            action="Played greeting and setup voice input",
            outcome="Successfully initialized voice components",
            success=True,
            confidence=0.9,
            tags=["voice", "tts", "demo"]
        )
        
        print("Voice input ready. Press SPACE to speak (or skip this demo)...")
        
        # Optional voice input (skip if no microphone)
        try:
            # text = self.voice_input.listen_with_push_to_talk(timeout=5)
            # if text:
            #     self.logger.info(f"Voice input received: {text}")
            #     self.tts.speak(f"Anda mengatakan: {text}")
            pass
        except Exception as e:
            self.logger.warning(f"Voice input skipped: {e}")
    
    async def demo_indonesian_processing(self):
        """Demonstrate Indonesian language processing."""
        self.logger.info("=== Indonesian Language Processing Demo ===")
        
        test_commands = [
            "buka excel",
            "tutup aplikasi",
            "cari file dokumen",
            "install aplikasi notepad",
            "tampilkan proses yang berjalan"
        ]
        
        for command in test_commands:
            try:
                # Parse command
                parsed = self.grammar.parse_command(command)
                self.logger.info(f"Command: '{command}' -> {parsed}")
                
                # Route command
                route_result = self.router.route_command(parsed)
                self.logger.info(f"Routed to: {route_result}")
                
                # Record experience
                await self.evolution_engine.record_experience(
                    experience_type=ExperienceType.COMMAND_PROCESSING,
                    context=f"Indonesian command: {command}",
                    action=f"Parsed and routed command",
                    outcome=f"Successfully processed: {route_result}",
                    success=True,
                    confidence=0.8,
                    tags=["indonesian", "nlp", "command"]
                )
                
            except Exception as e:
                self.logger.error(f"Failed to process command '{command}': {e}")
                
                await self.evolution_engine.record_experience(
                    experience_type=ExperienceType.COMMAND_PROCESSING,
                    context=f"Indonesian command: {command}",
                    action=f"Attempted to parse command",
                    outcome=f"Failed: {str(e)}",
                    success=False,
                    confidence=0.3,
                    tags=["indonesian", "nlp", "error"]
                )
    
    async def demo_office_automation(self):
        """Demonstrate Office automation features."""
        self.logger.info("=== Office Automation Demo ===")
        
        demo_dir = Path("demo_output")
        demo_dir.mkdir(exist_ok=True)
        
        try:
            # Excel demo
            self.logger.info("Creating Excel workbook...")
            self.excel.open_excel()
            workbook = self.excel.create_workbook()
            
            # Add sample data
            data = [
                ["Product", "Sales", "Profit"],
                ["Laptop", 1000, 200],
                ["Mouse", 500, 50],
                ["Keyboard", 300, 30]
            ]
            
            for row, row_data in enumerate(data, 1):
                for col, value in enumerate(row_data, 1):
                    self.excel.write_cell(workbook, 'Sheet1', f'{chr(64+col)}{row}', value)
            
            # Add chart
            self.excel.insert_chart(workbook, 'Sheet1', 'E2', 'A1:C4', 'Column')
            
            excel_file = demo_dir / "demo_sales.xlsx"
            self.excel.save_workbook(workbook, str(excel_file))
            self.excel.close_workbook(workbook)
            
            # Word demo
            self.logger.info("Creating Word document...")
            self.word.open_word()
            doc = self.word.create_document()
            
            self.word.write_text(doc, "Laporan Penjualan\n\n")
            self.word.format_text(doc, "Laporan Penjualan", bold=True, size=16)
            self.word.write_text(doc, "Dokumen ini dibuat secara otomatis menggunakan Windows Use Agent.\n")
            self.word.write_text(doc, "Data penjualan telah dianalisis dan disimpan dalam file Excel terlampir.")
            
            word_file = demo_dir / "demo_report.docx"
            self.word.save_document(doc, str(word_file))
            self.word.close_document(doc)
            
            # PowerPoint demo
            self.logger.info("Creating PowerPoint presentation...")
            self.powerpoint.open_powerpoint()
            pres = self.powerpoint.create_presentation()
            
            # Add title slide
            slide1 = self.powerpoint.add_slide(pres, 'Title')
            self.powerpoint.add_text_to_slide(slide1, "Demonstrasi Windows Use Agent", "title")
            self.powerpoint.add_text_to_slide(slide1, "Otomasi Office dengan AI", "subtitle")
            
            # Add content slide
            slide2 = self.powerpoint.add_slide(pres, 'Content')
            self.powerpoint.add_text_to_slide(slide2, "Fitur Utama", "title")
            content = "• Voice Input & TTS\n• Indonesian Language Processing\n• Office Automation\n• System Tools\n• Self-Evolving Agent"
            self.powerpoint.add_text_to_slide(slide2, content, "content")
            
            ppt_file = demo_dir / "demo_presentation.pptx"
            self.powerpoint.save_presentation(pres, str(ppt_file))
            self.powerpoint.close_presentation(pres)
            
            # Record success
            await self.evolution_engine.record_experience(
                experience_type=ExperienceType.TASK_EXECUTION,
                context="Office automation demo",
                action="Created Excel, Word, and PowerPoint files",
                outcome=f"Successfully created 3 office documents in {demo_dir}",
                success=True,
                confidence=0.95,
                tags=["office", "automation", "excel", "word", "powerpoint"]
            )
            
            self.logger.info(f"Office documents created in: {demo_dir}")
            
        except Exception as e:
            self.logger.error(f"Office automation demo failed: {e}")
            
            await self.evolution_engine.record_experience(
                experience_type=ExperienceType.TASK_EXECUTION,
                context="Office automation demo",
                action="Attempted to create office documents",
                outcome=f"Failed: {str(e)}",
                success=False,
                confidence=0.2,
                tags=["office", "automation", "error"]
            )
    
    async def demo_system_tools(self):
        """Demonstrate Windows system tools."""
        self.logger.info("=== Windows System Tools Demo ===")
        
        try:
            # Package management
            self.logger.info("Searching for packages...")
            packages = self.winget.search_package("notepad")
            self.logger.info(f"Found {len(packages)} packages matching 'notepad'")
            
            # PowerShell operations
            self.logger.info("Getting system information...")
            system_info = self.powershell.get_system_info()
            self.logger.info(f"System: {system_info.get('OS', 'Unknown')}")
            
            # Process management
            self.logger.info("Listing top processes...")
            top_processes = self.process_mgr.get_top_processes_by_cpu(limit=5)
            for proc in top_processes:
                self.logger.info(f"Process: {proc.name} (PID: {proc.pid}, CPU: {proc.cpu_percent}%)")
            
            # Network operations
            self.logger.info("Testing network connectivity...")
            ping_result = self.network.ping("8.8.8.8")
            self.logger.info(f"Ping to 8.8.8.8: {ping_result['success']} ({ping_result['avg_time']}ms)")
            
            # Record success
            await self.evolution_engine.record_experience(
                experience_type=ExperienceType.SYSTEM_OPERATION,
                context="System tools demo",
                action="Executed package search, system info, process list, network test",
                outcome="All system operations completed successfully",
                success=True,
                confidence=0.9,
                tags=["system", "tools", "winget", "powershell", "network"]
            )
            
        except Exception as e:
            self.logger.error(f"System tools demo failed: {e}")
            
            await self.evolution_engine.record_experience(
                experience_type=ExperienceType.SYSTEM_OPERATION,
                context="System tools demo",
                action="Attempted system operations",
                outcome=f"Failed: {str(e)}",
                success=False,
                confidence=0.3,
                tags=["system", "tools", "error"]
            )
    
    async def demo_security_features(self):
        """Demonstrate security and observability features."""
        self.logger.info("=== Security & Observability Demo ===")
        
        try:
            # Test guardrails
            safe_action = {
                "type": "file_operation",
                "action": "create_file",
                "target": "demo_file.txt"
            }
            
            dangerous_action = {
                "type": "system_operation",
                "action": "delete_system_file",
                "target": "C:\\Windows\\System32\\important.dll"
            }
            
            # Test safe action
            safe_result = self.guardrails.validate_action(safe_action)
            self.logger.info(f"Safe action validation: {safe_result['allowed']}")
            
            # Test dangerous action
            dangerous_result = self.guardrails.validate_action(dangerous_action)
            self.logger.info(f"Dangerous action validation: {dangerous_result['allowed']}")
            
            # Take screenshot for observability
            screenshot_path = self.screenshot.capture_screenshot("demo_security")
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Record security demo
            await self.evolution_engine.record_experience(
                experience_type=ExperienceType.SECURITY_CHECK,
                context="Security features demo",
                action="Tested guardrails and observability",
                outcome=f"Safe action: {safe_result['allowed']}, Dangerous action: {dangerous_result['allowed']}",
                success=True,
                confidence=0.95,
                tags=["security", "guardrails", "observability"]
            )
            
        except Exception as e:
            self.logger.error(f"Security demo failed: {e}")
    
    async def demo_evolution_features(self):
        """Demonstrate self-evolution capabilities."""
        self.logger.info("=== Self-Evolution Demo ===")
        
        try:
            # Simulate some task executions with varying success
            tasks = [
                ("file_search", "search for documents", "found 15 files", True, 2.3),
                ("app_launch", "open calculator", "calculator opened", True, 1.1),
                ("web_search", "search for information", "timeout error", False, 10.0),
                ("data_analysis", "analyze sales data", "completed analysis", True, 5.2),
                ("email_send", "send notification", "email sent", True, 3.1)
            ]
            
            for task_id, expected, actual, success, exec_time in tasks:
                await self.evolution_engine.evaluate_performance(
                    task_id=task_id,
                    expected_outcome=expected,
                    actual_outcome=actual,
                    execution_time=exec_time,
                    success=success
                )
            
            # Trigger evolution cycle
            self.logger.info("Triggering evolution cycle...")
            evolution_result = await self.evolution_engine.evolve()
            
            self.logger.info(f"Evolution completed:")
            self.logger.info(f"- Reflections: {len(evolution_result['reflections'])}")
            self.logger.info(f"- Mutations: {len(evolution_result['mutations'])}")
            
            if evolution_result['performance_summary']:
                perf = evolution_result['performance_summary']
                self.logger.info(f"- Success rate: {perf['success_rate']:.2%}")
                self.logger.info(f"- Average execution time: {perf['avg_execution_time']:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Evolution demo failed: {e}")
    
    async def show_evolution_insights(self):
        """Show current evolution insights and recommendations."""
        self.logger.info("=== Evolution Insights ===")
        
        try:
            insights = await self.evolution_engine.get_insights()
            
            self.logger.info("Performance Summary:")
            perf = insights['performance']
            self.logger.info(f"- Success Rate: {perf['success_rate']:.2%}")
            self.logger.info(f"- Accuracy: {perf['accuracy']:.2%}")
            self.logger.info(f"- Efficiency: {perf['efficiency']:.2%}")
            self.logger.info(f"- Total Tasks: {perf['total_tasks']}")
            
            self.logger.info("\nTop Insights:")
            for i, insight in enumerate(insights['insights'][:3], 1):
                self.logger.info(f"{i}. {insight['insight']} (Confidence: {insight['confidence']:.2%})")
            
            self.logger.info("\nRecommendations:")
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                self.logger.info(f"{i}. {rec}")
                
        except Exception as e:
            self.logger.error(f"Failed to get insights: {e}")


async def main():
    """Main demonstration function."""
    print("🪟 Windows Use Autonomous Agent - Complete Feature Demo")
    print("=" * 60)
    
    demo = CompleteDemo()
    await demo.run_complete_demo()
    
    print("\n" + "=" * 60)
    print("Demo completed! Check the logs and demo_output folder for results.")


if __name__ == "__main__":
    asyncio.run(main())