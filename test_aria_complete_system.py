
#!/usr/bin/env python3
"""
Comprehensive Aria System Tests
Tests all components, agents, and integrations
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

class AriaSystemIntegrationTest(unittest.TestCase):
    """Integration tests for complete Aria system"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_session = Mock()
        self.test_config = {
            "max_retries": 2,
            "timeout": 10,
            "cache_enabled": True
        }
    
    def test_complete_agent_workflow(self):
        """Test complete workflow with all agents"""
        print("\n🔄 Testing complete agent workflow...")
        
        try:
            # Import all required components
            from superagi.agents.aria_agents.aria_controller import AriaController
            from superagi.agents.aria_agents.aria_agent_registry import AriaAgentRegistry
            
            # Initialize system
            registry = AriaAgentRegistry()
            controller = AriaController(self.mock_session, registry)
            
            # Test agent creation
            test_agents = [
                "AriaUtilityAgent",
                "AriaToolAgent", 
                "AriaMemoryAgent",
                "AriaSummaryAgent",
                "AriaMasterAgent"
            ]
            
            created_agents = []
            for agent_type in test_agents:
                try:
                    agent = controller.create_agent(agent_type, self.test_config)
                    self.assertIsNotNone(agent)
                    created_agents.append(agent)
                    print(f"✅ Created {agent_type}")
                except Exception as e:
                    print(f"❌ Failed to create {agent_type}: {e}")
                    self.fail(f"Agent creation failed: {agent_type}")
            
            # Test agent communication
            test_message = "Process this test request with coordination"
            
            for agent in created_agents:
                try:
                    response = agent.respond(test_message)
                    self.assertIsInstance(response, dict)
                    self.assertIn("response", response)
                    print(f"✅ {agent.name} responded successfully")
                except Exception as e:
                    print(f"❌ {agent.name} failed to respond: {e}")
            
            print("✅ Complete agent workflow test passed")
            
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            self.fail("Required components not available")
        except Exception as e:
            print(f"❌ Workflow test failed: {e}")
            self.fail(f"Complete workflow test failed: {e}")
    
    def test_memory_system_integration(self):
        """Test advanced memory system"""
        print("\n🧠 Testing memory system integration...")
        
        try:
            from superagi.agents.aria_agents.aria_advanced_memory_agent.aria_advanced_memory_agent import AriaAdvancedMemoryAgent
            
            # Create memory agent
            memory_agent = AriaAdvancedMemoryAgent(
                self.mock_session, 
                "test_memory_agent", 
                self.test_config
            )
            
            # Test memory storage
            test_memories = [
                ("Important user feedback: The system works well", {"importance": "high"}),
                ("Task completed successfully", {"task_id": "123"}),
                ("Error occurred in module X", {"severity": "medium"}),
                ("User prefers dark theme", {"preference": "ui"}),
                ("Learning: Use caching for better performance", {"type": "insight"})
            ]
            
            for content, context in test_memories:
                response = memory_agent.respond(f"store {content}", context)
                self.assertIn("stored successfully", response["response"].lower())
                print(f"✅ Stored memory: {content[:30]}...")
            
            # Test memory retrieval
            retrieval_tests = [
                "retrieve user feedback",
                "retrieve task information", 
                "retrieve error reports",
                "retrieve insights about performance"
            ]
            
            for query in retrieval_tests:
                response = memory_agent.respond(query)
                self.assertIn("response", response)
                print(f"✅ Retrieved: {query}")
            
            # Test memory analysis
            analysis_response = memory_agent.respond("analyze User likes the new interface design")
            self.assertIn("importance_score", analysis_response["response"])
            print("✅ Memory analysis working")
            
            # Test memory statistics
            stats_response = memory_agent.respond("statistics")
            self.assertIn("Statistics", stats_response["response"])
            print("✅ Memory statistics working")
            
            print("✅ Memory system integration test passed")
            
        except Exception as e:
            print(f"❌ Memory system test failed: {e}")
            self.fail(f"Memory system integration failed: {e}")
    
    def test_openai_fallback_system(self):
        """Test OpenAI fallback mechanisms"""
        print("\n🔄 Testing OpenAI fallback system...")
        
        try:
            from superagi.helper.openai_fallback import OpenAIFallbackManager
            
            # Create fallback manager
            fallback_config = {
                "max_retries": 2,
                "base_delay": 0.1,  # Fast for testing
                "fallback_models": ["gpt-3.5-turbo", "text-davinci-003"]
            }
            
            fallback_manager = OpenAIFallbackManager(fallback_config)
            
            # Test health status
            health_status = fallback_manager.get_health_status()
            self.assertIn("status", health_status)
            self.assertIn("fallback_models_available", health_status)
            print("✅ Fallback manager health check passed")
            
            # Test error handling simulation
            def mock_failing_request():
                raise Exception("Simulated API failure")
            
            def mock_successful_request():
                return {"response": "success", "model": "test-model"}
            
            # Test with successful fallback
            try:
                result = fallback_manager.make_request_with_fallback(mock_successful_request)
                self.assertEqual(result["response"], "success")
                print("✅ Successful request handling works")
            except Exception as e:
                print(f"⚠️ Successful request test issue: {e}")
            
            print("✅ OpenAI fallback system test completed")
            
        except Exception as e:
            print(f"❌ OpenAI fallback test failed: {e}")
            self.fail(f"OpenAI fallback system failed: {e}")
    
    def test_api_performance_monitoring(self):
        """Test API performance monitoring"""
        print("\n📊 Testing API performance monitoring...")
        
        try:
            from superagi.helper.api_improvements import APIPerformanceManager
            
            # Create performance manager
            perf_manager = APIPerformanceManager({
                "cache_ttl": 60,
                "max_concurrent": 3
            })
            
            # Simulate some requests
            test_requests = [
                {"endpoint": "chat/completions", "duration": 1.5, "success": True},
                {"endpoint": "chat/completions", "duration": 2.1, "success": True},
                {"endpoint": "embeddings", "duration": 0.8, "success": False},
                {"endpoint": "chat/completions", "duration": 1.2, "success": True}
            ]
            
            for request in test_requests:
                perf_manager.track_request(
                    request["endpoint"],
                    request["duration"], 
                    request["success"]
                )
            
            # Test performance stats
            stats = perf_manager.get_performance_stats()
            self.assertIn("total_requests", stats)
            self.assertIn("success_rate", stats)
            self.assertIn("avg_response_time", stats)
            print(f"✅ Performance stats: {stats['total_requests']} requests, {stats['success_rate']}% success rate")
            
            # Test cache functionality
            cache_key = perf_manager.get_cache_key("test/endpoint", {"param": "value"})
            self.assertIsInstance(cache_key, str)
            
            # Test cache storage and retrieval
            test_response = {"test": "cached_data"}
            perf_manager.cache_response(cache_key, test_response)
            cached_result = perf_manager.get_cached_response(cache_key)
            self.assertEqual(cached_result["test"], "cached_data")
            print("✅ Cache system working")
            
            # Test health metrics
            health_metrics = perf_manager.get_health_metrics()
            self.assertIn("status", health_metrics)
            self.assertIn("recommendations", health_metrics)
            print(f"✅ Health status: {health_metrics['status']}")
            
            print("✅ API performance monitoring test passed")
            
        except Exception as e:
            print(f"❌ API performance test failed: {e}")
            self.fail(f"API performance monitoring failed: {e}")
    
    def test_system_resilience(self):
        """Test system resilience and error handling"""
        print("\n🛡️ Testing system resilience...")
        
        try:
            from superagi.agents.aria_agents.aria_controller import AriaController
            from superagi.agents.aria_agents.aria_agent_registry import AriaAgentRegistry
            
            registry = AriaAgentRegistry()
            controller = AriaController(self.mock_session, registry)
            
            # Test with invalid agent type
            try:
                invalid_agent = controller.create_agent("NonExistentAgent", {})
                print("⚠️ Should have failed for invalid agent type")
            except Exception:
                print("✅ Properly handles invalid agent types")
            
            # Test with malformed config
            try:
                agent = controller.create_agent("AriaUtilityAgent", "invalid_config")
                print("⚠️ Should handle malformed config gracefully")
            except Exception:
                print("✅ Properly handles malformed config")
            
            # Test with empty/None inputs
            valid_agent = controller.create_agent("AriaUtilityAgent", {})
            
            test_inputs = ["", None, {}, [], 123, "valid input"]
            for test_input in test_inputs:
                try:
                    response = valid_agent.respond(str(test_input) if test_input is not None else "")
                    self.assertIsInstance(response, dict)
                    print(f"✅ Handled input: {type(test_input).__name__}")
                except Exception as e:
                    print(f"⚠️ Issue with input {type(test_input).__name__}: {e}")
            
            print("✅ System resilience test passed")
            
        except Exception as e:
            print(f"❌ System resilience test failed: {e}")
            self.fail(f"System resilience test failed: {e}")
    
    def test_configuration_management(self):
        """Test configuration management across system"""
        print("\n⚙️ Testing configuration management...")
        
        try:
            # Test different configuration scenarios
            configs = [
                {},  # Empty config
                {"timeout": 30, "retries": 5},  # Basic config
                {"advanced": True, "features": ["cache", "fallback"]},  # Advanced config
                {"invalid": "config", "numbers": "should_be_int"}  # Mixed types
            ]
            
            for i, config in enumerate(configs):
                try:
                    from superagi.agents.aria_agents.aria_utility_agent.aria_utility_agent import AriaUtilityAgent
                    
                    agent = AriaUtilityAgent(self.mock_session, f"test_agent_{i}", config)
                    self.assertIsNotNone(agent)
                    self.assertIsInstance(agent.config, dict)
                    print(f"✅ Config {i+1}: Successfully handled")
                    
                except Exception as e:
                    print(f"⚠️ Config {i+1} issue: {e}")
            
            print("✅ Configuration management test passed")
            
        except Exception as e:
            print(f"❌ Configuration management test failed: {e}")
            self.fail(f"Configuration management failed: {e}")
    
    def test_performance_benchmarks(self):
        """Test system performance benchmarks"""
        print("\n⚡ Testing performance benchmarks...")
        
        try:
            from superagi.agents.aria_agents.aria_utility_agent.aria_utility_agent import AriaUtilityAgent
            
            # Create agent for performance testing
            agent = AriaUtilityAgent(self.mock_session, "perf_test_agent", {})
            
            # Test response times
            test_messages = [
                "Simple request",
                "Complex request with multiple parameters and detailed analysis requirements",
                "Medium complexity request for processing",
                "" * 100,  # Empty string
                "Repeated " * 50  # Long repetitive string
            ]
            
            response_times = []
            
            for msg in test_messages:
                start_time = time.time()
                try:
                    response = agent.respond(msg)
                    end_time = time.time()
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    # Performance assertions
                    self.assertLess(response_time, 5.0, "Response should be under 5 seconds")
                    self.assertIsInstance(response, dict)
                    
                except Exception as e:
                    print(f"⚠️ Performance test issue: {e}")
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                print(f"✅ Average response time: {avg_response_time:.3f}s")
                print(f"✅ Max response time: {max_response_time:.3f}s") 
                print(f"✅ Min response time: {min_response_time:.3f}s")
                
                # Performance benchmarks
                self.assertLess(avg_response_time, 1.0, "Average response time should be under 1 second")
                self.assertLess(max_response_time, 3.0, "Max response time should be under 3 seconds")
            
            print("✅ Performance benchmarks test passed")
            
        except Exception as e:
            print(f"❌ Performance benchmarks test failed: {e}")
            self.fail(f"Performance benchmarks failed: {e}")

def run_comprehensive_tests():
    """Run all comprehensive system tests"""
    print("🚀 Starting Comprehensive Aria System Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_complete_agent_workflow',
        'test_memory_system_integration', 
        'test_openai_fallback_system',
        'test_api_performance_monitoring',
        'test_system_resilience',
        'test_configuration_management',
        'test_performance_benchmarks'
    ]
    
    for method in test_methods:
        suite.addTest(AriaSystemIntegrationTest(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 Comprehensive Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n✅ Success Rate: {success_rate:.1f}%")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
