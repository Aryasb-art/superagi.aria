
#!/usr/bin/env python3
"""
رابط چت فارسی کامل برای تعامل با Aria MVP
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from superagi.agents.aria_agents.aria_controller import AriaController
from superagi.models.db import connect_db

class AriaChatInterface:
    """رابط چت فارسی برای Aria Robot"""
    
    def __init__(self):
        """راه‌اندازی رابط چت"""
        try:
            print("🔄 در حال راه‌اندازی Aria Robot...")
            self.session = connect_db()
            self.controller = AriaController(self.session)
            self.chat_history = []
            self.current_context = {}
            
            print("✅ Aria Robot آماده برای گفتگو!")
            self.show_welcome()
            
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی: {e}")
            sys.exit(1)
    
    def show_welcome(self):
        """نمایش پیام خوش‌آمدگویی"""
        print("\n" + "="*60)
        print("🤖 Aria Robot - دستیار هوشمند شما")
        print("="*60)
        print("""
🎯 من می‌توانم به شما کمک کنم در:
  ✅ پاسخ به سوالات عمومی
  ✅ خلاصه‌سازی متن
  ✅ تحلیل احساسات
  ✅ مدیریت اهداف و برنامه‌ریزی
  ✅ استفاده از ابزارهای مختلف
  ✅ ذخیره و بازیابی اطلاعات

💡 دستورات مفید:
  📋 'help' - راهنمای کامل
  📊 'status' - وضعیت سیستم
  🏠 'agents' - لیست ایجنت‌ها
  🧹 'clear' - پاک کردن تاریخچه
  🚪 'exit' - خروج

برای شروع، سوال یا درخواست خود را بنویسید...
        """)
    
    def show_help(self):
        """نمایش راهنمای کامل"""
        print("""
📚 راهنمای کامل Aria Robot:

🎯 انواع تسک‌های قابل انجام:
──────────────────────────────
1️⃣ سوالات عمومی:
   - "سلام، حالت چطوره؟"
   - "امروز چه روزی است؟"
   
2️⃣ خلاصه‌سازی:
   - "این متن را خلاصه کن: [متن شما]"
   - "نکات کلیدی این مطلب چیست؟"
   
3️⃣ تحلیل احساسات:
   - "احساس خوشحالی را تحلیل کن"
   - "این پیام چه حس و حالی دارد: [پیام]"
   
4️⃣ مدیریت اهداف:
   - "هدف من یادگیری برنامه‌نویسی است"
   - "برای رسیدن به این هدف چه کنم؟"
   
5️⃣ حافظه و ذخیره‌سازی:
   - "این اطلاعات را به خاطر بسپار: [اطلاعات]"
   - "اطلاعات قبلی من را یادت هست؟"
   
6️⃣ ابزارها و راهنمایی:
   - "چه ابزارهایی در دسترس هستند؟"
   - "برای انجام کار X چه توصیه‌ای داری؟"

🔧 دستورات سیستم:
──────────────────────
• help - نمایش این راهنما
• status - وضعیت سیستم و ایجنت‌ها
• agents - لیست ایجنت‌های موجود
• history - نمایش تاریخچه گفتگو
• clear - پاک کردن تاریخچه
• save - ذخیره گفتگو در فایل
• exit - خروج از برنامه
        """)
    
    def show_status(self):
        """نمایش وضعیت سیستم"""
        try:
            status = self.controller.get_system_status()
            print("\n📊 وضعیت سیستم Aria Robot:")
            print("="*40)
            print(f"🆔 شناسه کنترلر: {status['controller_id'][:8]}...")
            print(f"⏰ زمان راه‌اندازی: {status['created_at']}")
            print(f"🤖 ایجنت‌های فعال: {status['active_agents_count']}")
            print(f"📋 انواع ایجنت موجود: {len(status['available_agent_types'])}")
            print(f"🔧 قابلیت‌های موجود: {len(status['available_capabilities'])}")
            
            if status['active_agents']:
                print("\n🟢 ایجنت‌های فعال:")
                for agent_key, agent_status in status['active_agents'].items():
                    if 'error' not in agent_status:
                        print(f"  ✅ {agent_key}")
                    else:
                        print(f"  ❌ {agent_key} - خطا")
        except Exception as e:
            print(f"❌ خطا در دریافت وضعیت: {e}")
    
    def show_agents(self):
        """نمایش لیست ایجنت‌ها"""
        try:
            agents = self.controller.get_available_agents()
            print(f"\n🤖 ایجنت‌های موجود ({len(agents)} عدد):")
            print("="*50)
            
            agent_descriptions = {
                "AriaMasterAgent": "🎯 ایجنت اصلی - هماهنگ‌کننده کلی",
                "AriaSummaryAgent": "📝 خلاصه‌ساز - خلاصه‌سازی متون",
                "AriaToolAgent": "🔧 ابزار - مدیریت ابزارها",
                "AriaMemoryAgent": "🧠 حافظه - ذخیره و بازیابی اطلاعات",
                "AriaEmotionAgent": "💭 احساسات - تحلیل احساسات",
                "AriaGoalAgent": "🎯 اهداف - مدیریت اهداف",
                "AriaUtilityAgent": "⚙️ کمکی - کارهای عمومی"
            }
            
            for i, agent in enumerate(agents, 1):
                description = agent_descriptions.get(agent, "🤖 ایجنت تخصصی")
                print(f"  {i}. {description}")
                
        except Exception as e:
            print(f"❌ خطا در دریافت لیست ایجنت‌ها: {e}")
    
    def show_history(self):
        """نمایش تاریخچه گفتگو"""
        if not self.chat_history:
            print("\n📭 تاریخچه گفتگو خالی است")
            return
        
        print(f"\n📚 تاریخچه گفتگو ({len(self.chat_history)} پیام):")
        print("="*50)
        
        for i, chat in enumerate(self.chat_history[-10:], 1):  # آخرین 10 پیام
            timestamp = chat.get('timestamp', 'نامشخص')
            user_msg = chat.get('user_message', '')[:50]
            response = chat.get('response', '')[:50]
            
            print(f"\n{i}. ⏰ {timestamp}")
            print(f"   👤 شما: {user_msg}...")
            print(f"   🤖 Aria: {response}...")
    
    def clear_history(self):
        """پاک کردن تاریخچه"""
        self.chat_history.clear()
        self.current_context.clear()
        print("\n🧹 تاریخچه گفتگو پاک شد")
    
    def save_chat(self):
        """ذخیره گفتگو در فایل"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aria_chat_history_{timestamp}.json"
            
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "total_messages": len(self.chat_history),
                "chat_history": self.chat_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 گفتگو در فایل {filename} ذخیره شد")
            
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل: {e}")
    
    def process_message(self, user_message: str) -> str:
        """پردازش پیام کاربر"""
        try:
            # اضافه کردن context از گفتگوهای قبلی
            context = {
                "chat_history_count": len(self.chat_history),
                "previous_context": self.current_context
            }
            
            print("🤔 در حال پردازش...")
            
            # ارسال به کنترلر
            result = self.controller.execute_task(user_message, context=context)
            
            if result.get("success"):
                response_data = result.get('result', {})
                agent_type = result.get('agent_type', 'نامشخص')
                
                # استخراج پاسخ از نتیجه
                if isinstance(response_data, dict):
                    if 'content' in response_data:
                        response = response_data['content']
                    elif 'response' in response_data:
                        response = response_data['response']
                    elif 'message' in response_data:
                        response = response_data['message']
                    else:
                        response = str(response_data)
                else:
                    response = str(response_data)
                
                # ذخیره در تاریخچه
                chat_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_message": user_message,
                    "response": response,
                    "agent_type": agent_type,
                    "success": True
                }
                self.chat_history.append(chat_entry)
                
                # به‌روزرسانی context
                self.current_context.update({
                    "last_agent": agent_type,
                    "last_response_type": type(response_data).__name__
                })
                
                return f"🤖 Aria ({agent_type}): {response}"
                
            else:
                error_msg = result.get('error', 'خطای نامشخص')
                chat_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_message": user_message,
                    "response": f"خطا: {error_msg}",
                    "success": False
                }
                self.chat_history.append(chat_entry)
                
                return f"❌ خطا در پردازش: {error_msg}"
                
        except Exception as e:
            error_response = f"خطای سیستم: {str(e)}"
            chat_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_message": user_message,
                "response": error_response,
                "success": False
            }
            self.chat_history.append(chat_entry)
            
            return f"❌ {error_response}"
    
    def run_chat(self):
        """اجرای حلقه اصلی چت"""
        print("\n🎉 چت آماده است! پیام خود را بنویسید:")
        print("─" * 60)
        
        while True:
            try:
                # دریافت ورودی از کاربر
                user_input = input("\n👤 شما: ").strip()
                
                # بررسی دستورات سیستم
                if user_input.lower() == 'exit':
                    print("\n👋 خداحافظ! امیدوارم مفید بوده باشم.")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                elif user_input.lower() == 'agents':
                    self.show_agents()
                    continue
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                elif user_input.lower() == 'save':
                    self.save_chat()
                    continue
                elif not user_input:
                    print("💭 لطفاً پیامی بنویسید یا 'help' تایپ کنید")
                    continue
                
                # پردازش پیام عادی
                response = self.process_message(user_input)
                print(f"\n{response}")
                
                # نمایش آمار سریع
                if len(self.chat_history) % 5 == 0 and len(self.chat_history) > 0:
                    print(f"\n📊 آمار: {len(self.chat_history)} پیام تبادل شده")
                
            except KeyboardInterrupt:
                print("\n\n🛑 میانبر کیبورد شناسایی شد")
                save_choice = input("آیا می‌خواهید گفتگو را ذخیره کنید؟ (y/n): ").lower()
                if save_choice == 'y':
                    self.save_chat()
                print("👋 خداحافظ!")
                break
            except Exception as e:
                print(f"\n❌ خطای غیرمنتظره: {e}")
                print("🔄 ادامه می‌دهیم...")

def main():
    """تابع اصلی"""
    print("🚀 راه‌اندازی رابط چت Aria Robot...")
    
    try:
        chat_interface = AriaChatInterface()
        chat_interface.run_chat()
    except Exception as e:
        print(f"❌ خطای کلی: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
