
#!/usr/bin/env python3
"""
گزارش جامع وضعیت Aria Robot
"""

import sys
import os
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_aria_agents_status():
    """بررسی وضعیت ایجنت‌های Aria"""
    print("🤖 وضعیت ایجنت‌های Aria Robot")
    print("=" * 50)
    
    try:
        from superagi.agents.aria_agents.aria_controller import AriaController
        from superagi.models.db import connect_db
        
        # اتصال به دیتابیس
        session = connect_db()
        controller = AriaController(session)
        
        # دریافت ایجنت‌های موجود
        available_agents = controller.get_available_agents()
        capabilities = controller.get_available_capabilities()
        
        print(f"✅ تعداد انواع ایجنت موجود: {len(available_agents)}")
        print(f"✅ تعداد قابلیت‌های موجود: {len(capabilities)}")
        
        print("\n📋 لیست ایجنت‌های موجود:")
        for i, agent in enumerate(available_agents, 1):
            print(f"   {i}. {agent}")
        
        # تست ایجاد ایجنت‌ها
        print("\n🧪 تست ایجاد ایجنت‌ها:")
        success_count = 0
        failed_agents = []
        
        for agent_type in available_agents:
            try:
                agent = controller.create_agent(agent_type)
                if agent:
                    print(f"   ✅ {agent_type} - موفق")
                    success_count += 1
                else:
                    print(f"   ❌ {agent_type} - خطا در ایجاد")
                    failed_agents.append(agent_type)
            except Exception as e:
                print(f"   ❌ {agent_type} - {str(e)[:50]}...")
                failed_agents.append(agent_type)
        
        success_rate = (success_count / len(available_agents)) * 100
        print(f"\n📊 نرخ موفقیت: {success_rate:.1f}% ({success_count}/{len(available_agents)})")
        
        return {
            "total_agents": len(available_agents),
            "successful": success_count,
            "failed": failed_agents,
            "success_rate": success_rate,
            "capabilities": len(capabilities)
        }
        
    except Exception as e:
        print(f"❌ خطا در بررسی ایجنت‌ها: {e}")
        return {"error": str(e)}

def check_system_dependencies():
    """بررسی وابستگی‌های سیستم"""
    print("\n📦 وضعیت وابستگی‌های سیستم")
    print("=" * 50)
    
    dependencies = [
        "openai",
        "slack_sdk", 
        "pydantic",
        "sqlalchemy",
        "uvicorn",
        "fastapi",
        "reportlab"
    ]
    
    installed = []
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - نصب شده")
            installed.append(dep)
        except ImportError:
            print(f"❌ {dep} - نصب نشده")
            missing.append(dep)
    
    return {
        "installed": installed,
        "missing": missing,
        "total": len(dependencies)
    }

def check_database_connection():
    """بررسی اتصال دیتابیس"""
    print("\n🗄️  وضعیت دیتابیس")
    print("=" * 50)
    
    try:
        from superagi.models.db import connect_db
        session = connect_db()
        print("✅ اتصال به دیتابیس برقرار است")
        return {"status": "connected"}
    except Exception as e:
        print(f"❌ خطا در اتصال دیتابیس: {e}")
        return {"status": "error", "error": str(e)}

def check_server_status():
    """بررسی وضعیت سرورها"""
    print("\n🌐 وضعیت سرورها")
    print("=" * 50)
    
    import subprocess
    import requests
    
    # بررسی Persian UI Server
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print("✅ Persian UI Server - در حال اجرا")
        ui_status = "running"
    except:
        print("❌ Persian UI Server - غیر فعال")
        ui_status = "stopped"
    
    return {
        "persian_ui": ui_status
    }

def check_file_integrity():
    """بررسی سلامت فایل‌های مهم"""
    print("\n📁 بررسی فایل‌های مهم")
    print("=" * 50)
    
    important_files = [
        "aria_mvp_runner.py",
        "main.py",
        "superagi/agents/aria_agents/aria_controller.py",
        "superagi/agents/aria_agents/base_aria_agent.py",
        "superagi/tools/base_tool.py"
    ]
    
    existing = []
    missing = []
    
    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            existing.append(file_path)
        else:
            print(f"❌ {file_path} - یافت نشد")
            missing.append(file_path)
    
    return {
        "existing": existing,
        "missing": missing,
        "total": len(important_files)
    }

def generate_recommendations(results):
    """تولید توصیه‌ها"""
    print("\n🎯 توصیه‌ها و اقدامات پیشنهادی")
    print("=" * 50)
    
    recommendations = []
    
    # بررسی ایجنت‌ها
    if "agents" in results and results["agents"].get("success_rate", 0) < 70:
        recommendations.append("🔧 برخی ایجنت‌ها نیاز به تعمیر دارند")
    
    # بررسی وابستگی‌ها
    if "dependencies" in results and results["dependencies"]["missing"]:
        recommendations.append(f"📦 نصب کتابخانه‌های مفقود: {', '.join(results['dependencies']['missing'])}")
    
    # بررسی دیتابیس
    if "database" in results and results["database"]["status"] != "connected":
        recommendations.append("🗄️ بررسی تنظیمات دیتابیس")
    
    # بررسی سرور
    if "servers" in results and results["servers"]["persian_ui"] != "running":
        recommendations.append("🌐 راه‌اندازی Persian UI Server")
    
    if not recommendations:
        recommendations.append("✅ سیستم در وضعیت مطلوب است")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    return recommendations

def main():
    """اجرای گزارش کامل"""
    print("🤖 گزارش جامع وضعیت Aria Robot")
    print("=" * 60)
    print(f"⏰ زمان تولید گزارش: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # بررسی ایجنت‌ها
    results["agents"] = check_aria_agents_status()
    
    # بررسی وابستگی‌ها
    results["dependencies"] = check_system_dependencies()
    
    # بررسی دیتابیس
    results["database"] = check_database_connection()
    
    # بررسی سرورها
    results["servers"] = check_server_status()
    
    # بررسی فایل‌ها
    results["files"] = check_file_integrity()
    
    # تولید توصیه‌ها
    recommendations = generate_recommendations(results)
    
    # خلاصه نهایی
    print("\n" + "=" * 60)
    print("📊 خلاصه وضعیت کلی")
    print("=" * 60)
    
    if "agents" in results and not isinstance(results["agents"], dict):
        agents_ok = False
    else:
        agents_ok = results["agents"].get("success_rate", 0) >= 70
    
    deps_ok = len(results["dependencies"]["missing"]) == 0
    db_ok = results["database"]["status"] == "connected"
    files_ok = len(results["files"]["missing"]) == 0
    
    overall_score = sum([agents_ok, deps_ok, db_ok, files_ok]) / 4 * 100
    
    if overall_score >= 80:
        status_emoji = "🟢"
        status_text = "عالی"
    elif overall_score >= 60:
        status_emoji = "🟡"
        status_text = "قابل قبول"
    else:
        status_emoji = "🔴"
        status_text = "نیاز به توجه"
    
    print(f"وضعیت کلی: {status_emoji} {status_text} ({overall_score:.0f}%)")
    
    # ذخیره گزارش در فایل JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"aria_status_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "results": results,
            "recommendations": recommendations
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 گزارش کامل در فایل {report_file} ذخیره شد")

if __name__ == "__main__":
    main()
