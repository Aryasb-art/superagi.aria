
import requests
import json
import time

def test_system():
    """تست کامل سیستم"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 شروع تست سیستم...")
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/ping")
        assert response.status_code == 200
        print("✅ Health Check: موفق")
    except Exception as e:
        print(f"❌ Health Check: خطا - {e}")
        return False
    
    # Test 2: Static Files (Persian UI)
    try:
        response = requests.get(f"{base_url}/static/index.html")
        assert response.status_code == 200
        assert "Persian UI" in response.text or "فارسی" in response.text
        print("✅ Persian UI: در دسترس")
    except Exception as e:
        print(f"❌ Persian UI: خطا - {e}")
        return False
    
    # Test 3: API Health
    try:
        response = requests.get(f"{base_url}/api/health")
        assert response.status_code == 200
        print("✅ API Health: موفق")
    except Exception as e:
        print(f"❌ API Health: خطا - {e}")
        return False
    
    # Test 4: Aria Agent API
    try:
        test_data = {
            "message": "سلام، تست اتصال",
            "agent_type": "AriaGoalAgent"
        }
        response = requests.post(f"{base_url}/api/execute_agent", 
                               json=test_data)
        assert response.status_code == 200
        result = response.json()
        assert "success" in result
        print("✅ Aria Agent API: موفق")
    except Exception as e:
        print(f"❌ Aria Agent API: خطا - {e}")
        return False
    
    print("🎉 همه تست‌ها موفق بودند!")
    return True

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    test_system()
