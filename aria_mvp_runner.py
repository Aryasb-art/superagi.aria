
#!/usr/bin/env python3
"""
Aria Robot MVP Runner
Main entry point for running Aria Robot MVP with all 7 agents
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from superagi.agents.aria_agents.aria_controller import AriaController
from superagi.models.db import connect_db
from superagi.lib.logger import logger


class AriaMVPRunner:
    """Main runner for Aria Robot MVP"""
    
    def __init__(self):
        """Initialize MVP Runner"""
        self.session = None
        self.controller = None
        
    def initialize(self) -> bool:
        """Initialize database and controller"""
        try:
            print("🔄 در حال راه‌اندازی Aria Robot MVP...")
            
            # Initialize database
            self.session = connect_db()
            print("✅ اتصال به دیتابیس برقرار شد")
            
            # Initialize controller
            self.controller = AriaController(self.session)
            print("✅ کنترلر مرکزی راه‌اندازی شد")
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی: {e}")
            return False
    
    def health_check(self) -> bool:
        """Perform health check on all agents"""
        print("\n🏥 بررسی سلامت سیستم...")
        
        try:
            # Check available agents
            available_agents = self.controller.get_available_agents()
            print(f"✅ {len(available_agents)} نوع ایجنت در دسترس است")
            
            # Check available capabilities  
            capabilities = self.controller.get_available_capabilities()
            print(f"✅ {len(capabilities)} قابلیت در دسترس است")
            
            # Try creating each agent type
            print("\n🧪 تست ایجاد ایجنت‌ها...")
            success_count = 0
            
            for agent_type in available_agents:
                try:
                    agent = self.controller.create_agent(agent_type)
                    if agent:
                        print(f"✅ {agent_type} - OK")
                        success_count += 1
                    else:
                        print(f"❌ {agent_type} - Failed to create")
                except Exception as e:
                    print(f"❌ {agent_type} - Error: {str(e)}")
            
            success_rate = (success_count / len(available_agents)) * 100
            print(f"\n📊 نرخ موفقیت: {success_rate:.1f}% ({success_count}/{len(available_agents)})")
            
            return success_rate >= 70  # At least 70% success rate
            
        except Exception as e:
            print(f"❌ خطا در بررسی سلامت: {e}")
            return False
    
    def demo_mode(self):
        """Run demonstration of all agents"""
        print("\n🎬 حالت نمایشی - تست همه ایجنت‌ها")
        print("=" * 50)
        
        demo_tasks = [
            ("خلاصه‌سازی", "لطفاً این متن را خلاصه کنید: امروز روز خوبی بود و کارهای زیادی انجام دادم"),
            ("ابزار", "چه ابزارهایی برای انجام کار در دسترس هستند؟"),
            ("حافظه", "لطفاً این اطلاعات را به خاطر بسپارید: نام من علی است"),
            ("احساسات", "احساس خوشحالی را تحلیل کنید"),
            ("هدف", "هدف من یادگیری برنامه‌نویسی است"),
            ("ابزار کمکی", "راهنمایی برای شروع یک پروژه بده"),
            ("مدیریت", "وضعیت کلی سیستم را بررسی کن")
        ]
        
        for task_name, task in demo_tasks:
            print(f"\n🎯 تست {task_name}:")
            print(f"   تسک: {task}")
            
            result = self.controller.execute_task(task)
            
            if result.get("success"):
                print(f"   ✅ انجام شد توسط: {result.get('agent_type')}")
                result_content = result.get('result', {})
                if isinstance(result_content, dict) and 'content' in result_content:
                    print(f"   📝 نتیجه: {result_content['content'][:100]}...")
            else:
                print(f"   ❌ خطا: {result.get('error')}")
    
    def interactive_test(self):
        """Interactive testing mode"""
        print("\n🎮 حالت تست تعاملی")
        print("دستورات: 'status', 'agents', 'demo', 'exit'")
        print("یا یک تسک برای اجرا وارد کنید")
        print("─" * 40)
        
        while True:
            try:
                user_input = input("\ntest> ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'status':
                    status = self.controller.get_system_status()
                    print(f"📊 ایجنت‌های فعال: {status.get('active_agents_count')}")
                elif user_input.lower() == 'agents':
                    agents = self.controller.get_available_agents()
                    print(f"📋 ایجنت‌های موجود: {', '.join(agents)}")
                elif user_input.lower() == 'demo':
                    self.demo_mode()
                elif user_input:
                    print(f"🚀 اجرای تسک: {user_input}")
                    result = self.controller.execute_task(user_input)
                    
                    if result.get("success"):
                        print(f"✅ موفق - {result.get('agent_type')}")
                        result_content = result.get('result', {})
                        print(f"📝 نتیجه: {result_content}")
                    else:
                        print(f"❌ خطا: {result.get('error')}")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ خطا: {e}")
    
    def run(self, mode: str = "interactive"):
        """Run MVP in specified mode"""
        if not self.initialize():
            return False
        
        print(f"\n🎉 Aria Robot MVP آماده است!")
        print(f"⏰ زمان راه‌اندازی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if mode == "health":
            return self.health_check()
        elif mode == "demo":
            if self.health_check():
                self.demo_mode()
            return True
        elif mode == "interactive":
            if self.health_check():
                self.interactive_test()
            return True
        else:
            print(f"❌ حالت نامشخص: {mode}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Aria Robot MVP Runner')
    parser.add_argument('--mode', default='interactive', 
                       choices=['health', 'demo', 'interactive'],
                       help='Run mode: health check, demo, or interactive')
    
    args = parser.parse_args()
    
    print("🤖 Aria Robot MVP Runner")
    print("=" * 50)
    
    runner = AriaMVPRunner()
    
    try:
        success = runner.run(args.mode)
        if success:
            print("\n✅ اجرا با موفقیت به پایان رسید")
        else:
            print("\n❌ اجرا با خطا مواجه شد")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 خروج از برنامه...")
    except Exception as e:
        print(f"\n❌ خطای سیستم: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
