
#!/usr/bin/env python3
"""
Comprehensive test suite for Aria Robot MVP
Tests all 7 agents and core functionality
"""

import sys
import os
import unittest
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from superagi.agents.aria_agents.aria_controller import AriaController
from superagi.agents.aria_agents.aria_agent_registry import AriaAgentRegistry
from superagi.models.db import connect_db


class TestAriaMVP(unittest.TestCase):
    """Test suite for Aria MVP"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        try:
            cls.session = connect_db()
            cls.controller = AriaController(cls.session)
            print("✅ Test environment initialized")
        except Exception as e:
            print(f"❌ Failed to initialize test environment: {e}")
            raise
    
    def test_registry_initialization(self):
        """Test that registry is properly initialized"""
        agents = AriaAgentRegistry.get_all_agents()
        self.assertGreaterEqual(len(agents), 7, "Should have at least 7 agents")
        
        expected_agents = [
            "AriaUtilityAgent", "AriaToolAgent", "AriaMemoryAgent",
            "AriaSummaryAgent", "AriaMasterAgent", "AriaEmotionAgent", "AriaGoalAgent"
        ]
        
        for agent_type in expected_agents:
            self.assertIn(agent_type, agents, f"{agent_type} should be in registry")
    
    def test_agent_creation(self):
        """Test creation of all agent types"""
        available_agents = self.controller.get_available_agents()
        
        for agent_type in available_agents:
            with self.subTest(agent_type=agent_type):
                agent = self.controller.create_agent(agent_type)
                self.assertIsNotNone(agent, f"Should be able to create {agent_type}")
                self.assertEqual(agent.get_agent_type(), agent_type)
    
    def test_task_execution(self):
        """Test task execution with different agents"""
        test_cases = [
            ("AriaUtilityAgent", "راهنمایی عمومی بده"),
            ("AriaToolAgent", "ابزارهای موجود را نشان بده"),
            ("AriaMemoryAgent", "این اطلاعات را به خاطر بسپار: تست"),
            ("AriaSummaryAgent", "این متن را خلاصه کن: امروز روز خوبی بود"),
            ("AriaEmotionAgent", "احساس شادی را تحلیل کن"),
            ("AriaGoalAgent", "هدف یادگیری را بررسی کن"),
            ("AriaMasterAgent", "وضعیت سیستم را چک کن")
        ]
        
        for agent_type, task in test_cases:
            with self.subTest(agent_type=agent_type, task=task):
                result = self.controller.execute_task(task, agent_type)
                self.assertTrue(result.get("success"), f"Task should succeed for {agent_type}")
                self.assertIn("result", result, "Result should contain result field")
    
    def test_system_status(self):
        """Test system status functionality"""
        status = self.controller.get_system_status()
        
        required_fields = [
            "controller_id", "active_agents_count", "available_agent_types",
            "available_capabilities", "timestamp"
        ]
        
        for field in required_fields:
            self.assertIn(field, status, f"Status should contain {field}")
    
    def test_broadcast_functionality(self):
        """Test message broadcasting"""
        # Create some agents first
        self.controller.create_agent("AriaUtilityAgent")
        self.controller.create_agent("AriaToolAgent")
        
        result = self.controller.broadcast_message("تست پیام")
        
        self.assertIn("broadcast_id", result)
        self.assertIn("results", result)
        self.assertGreater(result.get("recipients", 0), 0)


def comprehensive_test():
    """Run comprehensive test and generate report"""
    print("🧪 شروع تست جامع Aria Robot MVP")
    print("=" * 50)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAriaMVP)
    runner = unittest.TextTestRunner(verbosity=2)
    result = unittest.TestResult()
    
    print("\n📊 نتایج تست:")
    suite.run(result)
    
    # Generate report
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_count = total_tests - failures - errors
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📈 گزارش نهایی:")
    print(f"   کل تست‌ها: {total_tests}")
    print(f"   موفق: {success_count}")
    print(f"   شکست: {failures}")
    print(f"   خطا: {errors}")
    print(f"   نرخ موفقیت: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 MVP آماده برای استفاده است!")
        mvp_status = "READY"
    elif success_rate >= 60:
        print("\n⚠️  MVP نیاز به بهبود دارد")
        mvp_status = "NEEDS_IMPROVEMENT"
    else:
        print("\n🚨 MVP آماده نیست - نیاز به رفع مشکلات")
        mvp_status = "NOT_READY"
    
    # Print failures and errors
    if result.failures:
        print("\n❌ شکست‌ها:")
        for test, error in result.failures:
            print(f"   {test}: {error}")
    
    if result.errors:
        print("\n💥 خطاها:")
        for test, error in result.errors:
            print(f"   {test}: {error}")
    
    return mvp_status, success_rate


if __name__ == "__main__":
    try:
        status, rate = comprehensive_test()
        if status == "READY":
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 تست متوقف شد")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطای سیستم: {e}")
        sys.exit(1)
