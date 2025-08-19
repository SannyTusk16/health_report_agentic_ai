#!/usr/bin/env python3
"""
CLI for testing the multi-agent healthcare processing system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the Agent_Orchestrator to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Agent_Orchestrator'))
from multi_agent_system import MultiAgentOrchestrator

async def demo_multi_agent_processing():
    """Demo the multi-agent system with sample files."""
    print("🏥 Healthcare Multi-Agent Processing Demo")
    print("=" * 50)
    
    orchestrator = MultiAgentOrchestrator()
    
    # Check if we have sample OCR files to work with
    ocr_dir = Path("../output/OCR")
    if not ocr_dir.exists():
        print("❌ No OCR directory found. Please run OCR extraction first.")
        return
    
    txt_files = list(ocr_dir.glob("*.txt"))
    if not txt_files:
        print("❌ No text files found. Please run OCR extraction first.")
        return
    
    print(f"📄 Found {len(txt_files)} OCR text files:")
    for f in txt_files:
        print(f"   - {f.name}")
    
    # Simulate processing these as PDFs (normally they'd be PDF inputs)
    # For demo purposes, we'll use the text files directly
    
    print(f"\n🚀 Starting multi-agent processing...")
    
    # Create mock PDF paths (in real scenario these would be actual PDFs)
    pdf_paths = [str(f) for f in txt_files]
    
    try:
        result = await orchestrator.process_pdf_batch(pdf_paths, patient_id="DEMO_PATIENT")
        
        if result:
            print(f"\n✅ SUCCESS! Multi-agent processing completed")
            print(f"📄 Final report: {result}")
            
            # Show system status
            status = orchestrator.get_system_status()
            print(f"\n📊 FINAL SYSTEM STATUS:")
            print("-" * 30)
            for agent_id, agent_info in status["agents"].items():
                print(f"🤖 {agent_info['name']}")
                print(f"   Status: {agent_info['status']}")
                print(f"   Completed Tasks: {agent_info['completed_tasks']}")
            
            print(f"\n📈 TASK SUMMARY:")
            print(f"   Active Tasks: {status['active_tasks']}")
            print(f"   Completed Tasks: {status['completed_tasks']}")
            print(f"   Queued Tasks: {status['queued_tasks']}")
            
        else:
            print("❌ Multi-agent processing failed")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")

def demo_enhanced_latex_agent():
    """Demo the enhanced LaTeX agent for multi-document processing."""
    print("\n📝 Enhanced LaTeX Agent Demo")
    print("=" * 35)
    
    try:
        # Import the enhanced agent
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'LaTEX_Code_Agent'))
        from enhanced_multi_document_agent import EnhancedHealthCareLatexAgent
        
        agent = EnhancedHealthCareLatexAgent()
        
        # Process multiple documents
        ocr_dir = "../output/OCR"
        output_file = "../output/latex/enhanced_consolidated_report.tex"
        
        result = agent.process_multiple_pdfs(ocr_dir, output_file)
        print(f"✅ Enhanced consolidated report generated: {output_file}")
        
        # Show file info
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📏 File size: {file_size} bytes")
            print(f"📁 Location: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"❌ Error in enhanced LaTeX processing: {e}")

async def main():
    """Main demo function."""
    print("🎯 Choose demo mode:")
    print("1. Multi-Agent System Demo")
    print("2. Enhanced LaTeX Agent Demo") 
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        await demo_multi_agent_processing()
    
    if choice in ["2", "3"]:
        demo_enhanced_latex_agent()
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())
