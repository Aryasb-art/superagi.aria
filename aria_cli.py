
#!/usr/bin/env python3
"""
Aria Robot MVP Command Line Interface
Interactive CLI for testing and managing Aria agents
"""

import sys
import os
import argparse
import json
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from superagi.agents.aria_agents.aria_controller import AriaController
from superagi.models.db import connect_db
from superagi.lib.logger import logger


class AriaCLI:
    """Command Line Interface for Aria Robot MVP"""
    
    def __init__(self):
        """Initialize CLI with database connection"""
        try:
            # Initialize database connection
            self.session = connect_db()
            self.controller = AriaController(self.session)
            print("🤖 Aria Robot MVP CLI - آماده به کار!")
            print("=" * 50)
        except Exception as e:
            print(f"❌ Error initializing CLI: {e}")
            sys.exit(1)
    
    def show_welcome(self):
        """Show welcome message and available commands"""
        print("""
🎯 دستورات موجود:
  list-agents     - نمایش لیست ایجنت‌های موجود
  list-capabilities - نمایش قابلیت‌های موجود  
  create-agent    - ایجاد ایجنت جدید
  execute-task    - اجرای تسک
  agent-status    - نمایش وضعیت ایجنت‌ها
  system-status   - نمایش وضعیت سیستم
  broadcast       - ارسال پیام به همه ایجنت‌ها
  interactive     - حالت تعاملی
  help           - نمایش راهنما
  exit           - خروج
        """)
    
    def list_agents(self):
        """List all available agent types"""
        agents = self.controller.get_available_agents()
        print(f"\n📋 ایجنت‌های موجود ({len(agents)} عدد):")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent}")
    
    def list_capabilities(self):
        """List all available capabilities"""
        capabilities = self.controller.get_available_capabilities()
        print(f"\n🔧 قابلیت‌های موجود ({len(capabilities)} عدد):")
        for i, cap in enumerate(capabilities, 1):
            print(f"  {i}. {cap}")
    
    def create_agent(self, agent_type: str = None):
        """Create a new agent instance"""
        if not agent_type:
            self.list_agents()
            agent_type = input("\n✏️  نام ایجنت را وارد کنید: ").strip()
        
        if agent_type:
            agent = self.controller.create_agent(agent_type)
            if agent:
                print(f"✅ ایجنت {agent_type} با موفقیت ایجاد شد!")
                print(f"   Agent ID: {agent.agent_id}")
                print(f"   Agent UUID: {agent.agent_uuid}")
            else:
                print(f"❌ خطا در ایجاد ایجنت {agent_type}")
    
    def execute_task(self, task: str = None, agent_type: str = None):
        """Execute a task"""
        if not task:
            task = input("\n✏️  تسک مورد نظر را وارد کنید: ").strip()
        
        if not agent_type:
            print("ایجنت خاصی را می‌خواهید؟ (برای استفاده از هوش سیستم خالی بگذارید)")
            agent_type = input("نام ایجنت: ").strip() or None
        
        if task:
            print(f"\n🚀 در حال اجرای تسک: {task}")
            result = self.controller.execute_task(task, agent_type)
            
            print("\n📊 نتیجه:")
            if result.get("success"):
                print(f"✅ موفق - ایجنت: {result.get('agent_type')}")
                print(f"📝 نتیجه: {json.dumps(result.get('result', {}), indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ خطا: {result.get('error')}")
    
    def show_agent_status(self):
        """Show status of active agents"""
        status = self.controller.get_system_status()
        active_agents = status.get("active_agents", {})
        
        print(f"\n📊 وضعیت ایجنت‌ها ({len(active_agents)} فعال):")
        
        if not active_agents:
            print("  هیچ ایجنت فعالی وجود ندارد")
            return
        
        for key, agent_status in active_agents.items():
            if "error" in agent_status:
                print(f"  ❌ {key}: {agent_status['error']}")
            else:
                print(f"  ✅ {key}:")
                print(f"     نوع: {agent_status.get('agent_type', 'نامشخص')}")
                print(f"     وضعیت: {'فعال' if agent_status.get('is_active') else 'غیرفعال'}")
                print(f"     پیام‌ها: {agent_status.get('total_messages', 0)}")
    
    def show_system_status(self):
        """Show overall system status"""
        status = self.controller.get_system_status()
        
        print(f"\n🔍 وضعیت سیستم:")
        print(f"  Controller ID: {status.get('controller_id')}")
        print(f"  ایجنت‌های فعال: {status.get('active_agents_count')}")
        print(f"  انواع ایجنت‌ها: {len(status.get('available_agent_types', []))}")
        print(f"  قابلیت‌ها: {len(status.get('available_capabilities', []))}")
        print(f"  زمان ایجاد: {status.get('created_at')}")
    
    def broadcast_message(self):
        """Broadcast message to all agents"""
        message = input("\n✏️  پیام برای همه ایجنت‌ها: ").strip()
        if message:
            print(f"\n📢 در حال ارسال پیام به همه ایجنت‌ها...")
            result = self.controller.broadcast_message(message)
            
            print(f"✅ پیام به {result.get('recipients')} ایجنت ارسال شد")
            print(f"📝 Broadcast ID: {result.get('broadcast_id')}")
    
    def interactive_mode(self):
        """Enter interactive mode"""
        print("\n🎮 حالت تعاملی - برای خروج 'exit' تایپ کنید")
        print("─" * 40)
        
        while True:
            try:
                command = input("\naria> ").strip().lower()
                
                if command == 'exit':
                    break
                elif command == 'list-agents':
                    self.list_agents()
                elif command == 'list-capabilities':
                    self.list_capabilities()
                elif command == 'create-agent':
                    self.create_agent()
                elif command == 'execute-task':
                    self.execute_task()
                elif command == 'agent-status':
                    self.show_agent_status()
                elif command == 'system-status':
                    self.show_system_status()
                elif command == 'broadcast':
                    self.broadcast_message()
                elif command == 'help':
                    self.show_welcome()
                elif command == '':
                    continue
                else:
                    print(f"❌ دستور نامشخص: {command}")
                    print("💡 برای مشاهده دستورات 'help' تایپ کنید")
                    
            except KeyboardInterrupt:
                print("\n\n👋 خروج از حالت تعاملی...")
                break
            except Exception as e:
                print(f"❌ خطا: {e}")
    
    def run(self, args):
        """Run CLI with provided arguments"""
        if args.command == 'list-agents':
            self.list_agents()
        elif args.command == 'list-capabilities':
            self.list_capabilities()
        elif args.command == 'create-agent':
            self.create_agent(args.agent_type)
        elif args.command == 'execute-task':
            self.execute_task(args.task, args.agent_type)
        elif args.command == 'agent-status':
            self.show_agent_status()
        elif args.command == 'system-status':
            self.show_system_status()
        elif args.command == 'interactive':
            self.interactive_mode()
        else:
            self.show_welcome()
            self.interactive_mode()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Aria Robot MVP CLI')
    parser.add_argument('command', nargs='?', default='interactive',
                       choices=['list-agents', 'list-capabilities', 'create-agent',
                               'execute-task', 'agent-status', 'system-status', 'interactive'],
                       help='Command to execute')
    parser.add_argument('--agent-type', help='Agent type for create-agent command')
    parser.add_argument('--task', help='Task description for execute-task command')
    
    args = parser.parse_args()
    
    try:
        cli = AriaCLI()
        cli.run(args)
    except KeyboardInterrupt:
        print("\n\n👋 خداحافظ!")
    except Exception as e:
        print(f"❌ خطای سیستم: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
