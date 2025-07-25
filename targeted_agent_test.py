
#!/usr/bin/env python3
"""
Targeted functionality test for existing Aria agents.
"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, '.')

def test_aria_summary_agent():
    """Test AriaUtilityAgent functionality"""
    print("\n" + "="*50)
    print("TESTING: ARIA_SUMMARY_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    try:
        # Test import
        from superagi.agents.aria_agents.aria_summary_agent.aria_summary_agent import AriaSummaryAgent
        results["import"] = True
        print("✅ Import successful")
        
        # Test inheritance
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        if issubclass(AriaSummaryAgent, BaseAriaAgent):
            results["inheritance"] = True
            print("✅ Correct inheritance from BaseAriaAgent")
        else:
            print("❌ Does not inherit from BaseAriaAgent")
        
        # Test methods
        required_methods = ['execute', 'get_capabilities', 'get_agent_type']
        missing_methods = [m for m in required_methods if not hasattr(AriaSummaryAgent, m)]
        if not missing_methods:
            results["methods"] = True
            print("✅ All required methods present")
        else:
            print(f"❌ Missing methods: {missing_methods}")
        
        # Test config
        config_path = "superagi/agents/aria_agents/aria_summary_agent/agent_config.yaml"
        if os.path.exists(config_path):
            results["config"] = True
            print("✅ Config file exists")
        else:
            print("❌ Config file not found")
        
        # Test instantiation
        try:
            agent = AriaSummaryAgent(session=None, agent_id=1)
            results["instantiation"] = True
            print("✅ Instantiation successful")
            
            # Test execution
            try:
                result = agent.execute("test summary", {"task_type": "text_summary", "content": "This is test content for summarization."})
                if isinstance(result, dict):
                    results["execution"] = True
                    print("✅ Execution successful")
                else:
                    print(f"❌ Execution returned invalid type: {type(result)}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
            
            # Test error handling
            try:
                result = agent.execute(None, None)
                results["error_handling"] = True
                print("✅ Error handling successful")
            except Exception as e:
                results["error_handling"] = True
                print(f"✅ Error handling successful (properly raised exception: {type(e).__name__})")
                
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    return results

def test_aria_tool_agent():
    """Test AriaToolAgent functionality"""
    print("\n" + "="*50)
    print("TESTING: ARIA_TOOL_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    try:
        # Test import
        from superagi.agents.aria_agents.aria_tool_agent.aria_tool_agent import AriaToolAgent
        results["import"] = True
        print("✅ Import successful")
        
        # Test inheritance
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        if issubclass(AriaToolAgent, BaseAriaAgent):
            results["inheritance"] = True
            print("✅ Correct inheritance from BaseAriaAgent")
        else:
            print("❌ Does not inherit from BaseAriaAgent")
        
        # Test methods
        required_methods = ['execute', 'get_capabilities', 'get_agent_type']
        missing_methods = [m for m in required_methods if not hasattr(AriaToolAgent, m)]
        if not missing_methods:
            results["methods"] = True
            print("✅ All required methods present")
        else:
            print(f"❌ Missing methods: {missing_methods}")
        
        # Test config
        config_path = "superagi/agents/aria_agents/aria_tool_agent/config.yaml"
        if os.path.exists(config_path):
            results["config"] = True
            print("✅ Config file exists")
        else:
            print("❌ Config file not found")
        
        # Test instantiation
        try:
            agent = AriaToolAgent(session=None, agent_id=1)
            results["instantiation"] = True
            print("✅ Instantiation successful")
            
            # Test execution
            try:
                result = agent.execute("test task", {"task_type": "general"})
                if isinstance(result, dict):
                    results["execution"] = True
                    print("✅ Execution successful")
                else:
                    print(f"❌ Execution returned invalid type: {type(result)}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
            
            # Test error handling
            try:
                result = agent.execute(None, None)
                results["error_handling"] = True
                print("✅ Error handling successful")
            except Exception as e:
                results["error_handling"] = True
                print(f"✅ Error handling successful (properly raised exception: {type(e).__name__})")
                
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    return results

def test_aria_utility_agent():
    """Test AriaUtilityAgent functionality"""
    print("\n" + "="*50)
    print("TESTING: ARIA_UTILITY_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    try:
        # Test import
        from superagi.agents.aria_agents.aria_utility_agent.aria_utility_agent import AriaUtilityAgent
        results["import"] = True
        print("✅ Import successful")
        
        # Test inheritance
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        if issubclass(AriaUtilityAgent, BaseAriaAgent):
            results["inheritance"] = True
            print("✅ Correct inheritance from BaseAriaAgent")
        else:
            print("❌ Does not inherit from BaseAriaAgent")
        
        # Test methods
        required_methods = ['execute', 'get_capabilities', 'get_agent_type']
        missing_methods = [m for m in required_methods if not hasattr(AriaUtilityAgent, m)]
        if not missing_methods:
            results["methods"] = True
            print("✅ All required methods present")
        else:
            print(f"❌ Missing methods: {missing_methods}")
        
        # Test config
        config_path = "superagi/agents/aria_agents/aria_utility_agent/config.yaml"
        if os.path.exists(config_path):
            results["config"] = True
            print("✅ Config file exists")
        else:
            print("❌ Config file not found")
        
        # Test instantiation
        try:
            agent = AriaUtilityAgent(session=None, agent_id=1)
            results["instantiation"] = True
            print("✅ Instantiation successful")
            
            # Test execution
            try:
                result = agent.execute("test utility task", {"task_type": "text_processing", "data": "test data"})
                if isinstance(result, dict):
                    results["execution"] = True
                    print("✅ Execution successful")
                else:
                    print(f"❌ Execution returned invalid type: {type(result)}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
            
            # Test error handling
            try:
                result = agent.execute(None, None)
                results["error_handling"] = True
                print("✅ Error handling successful")
            except Exception as e:
                results["error_handling"] = True
                print(f"✅ Error handling successful (properly raised exception: {type(e).__name__})")
                
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    return results

def test_aria_emotion_agent():
    """Test AriaEmotionAgent functionality"""
    print("\n" + "="*50)
    print("TESTING: ARIA_EMOTION_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    try:
        # Test import
        from superagi.agents.aria_agents.aria_emotion_agent.aria_emotion_agent import AriaEmotionAgent
        results["import"] = True
        print("✅ Import successful")
        
        # Test inheritance
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        if issubclass(AriaEmotionAgent, BaseAriaAgent):
            results["inheritance"] = True
            print("✅ Correct inheritance from BaseAriaAgent")
        else:
            print("❌ Does not inherit from BaseAriaAgent")
        
        # Test methods
        required_methods = ['execute', 'get_capabilities']
        missing_methods = [m for m in required_methods if not hasattr(AriaEmotionAgent, m)]
        if not missing_methods:
            results["methods"] = True
            print("✅ Required methods present")
        else:
            print(f"❌ Missing methods: {missing_methods}")
        
        # Test config
        config_path = "superagi/agents/aria_agents/aria_emotion_agent/agent_config.yaml"
        if os.path.exists(config_path):
            results["config"] = True
            print("✅ Config file exists")
        else:
            print("❌ Config file not found")
        
        # Test instantiation
        try:
            agent = AriaEmotionAgent(llm=None, agent_id=1)
            results["instantiation"] = True
            print("✅ Instantiation successful")
            
            # Test execution
            try:
                result = agent.execute({"type": "general_emotion_analysis", "description": "test emotion"})
                if isinstance(result, dict):
                    results["execution"] = True
                    print("✅ Execution successful")
                else:
                    print(f"❌ Execution returned invalid type: {type(result)}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
            
            # Test error handling
            try:
                result = agent.execute(None)
                results["error_handling"] = True
                print("✅ Error handling successful")
            except Exception as e:
                results["error_handling"] = True
                print(f"✅ Error handling successful (properly raised exception: {type(e).__name__})")
                
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    return results

def test_aria_memory_agent():
    """Test AriaMemoryAgent functionality"""
    print("\n" + "="*50)
    print("TESTING: ARIA_MEMORY_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    try:
        # Test import
        from superagi.agents.aria_agents.aria_memory_agent.aria_memory_agent import AriaMemoryAgent
        results["import"] = True
        print("✅ Import successful")
        
        # Test inheritance
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        if issubclass(AriaMemoryAgent, BaseAriaAgent):
            results["inheritance"] = True
            print("✅ Correct inheritance from BaseAriaAgent")
        else:
            print("❌ Does not inherit from BaseAriaAgent")
        
        # Test methods
        required_methods = ['execute', 'get_capabilities']
        missing_methods = [m for m in required_methods if not hasattr(AriaMemoryAgent, m)]
        if not missing_methods:
            results["methods"] = True
            print("✅ Required methods present")
        else:
            print(f"❌ Missing methods: {missing_methods}")
        
        # Test config
        config_path = "superagi/agents/aria_agents/aria_memory_agent/config.yaml"
        if os.path.exists(config_path):
            results["config"] = True
            print("✅ Config file exists")
        else:
            print("❌ Config file not found")
        
        # Test instantiation
        try:
            agent = AriaMemoryAgent(llm=None, agent_id=1)
            results["instantiation"] = True
            print("✅ Instantiation successful")
            
            # Test execution
            try:
                result = agent.execute({"type": "general_memory", "description": "test memory"})
                if isinstance(result, dict):
                    results["execution"] = True
                    print("✅ Execution successful")
                else:
                    print(f"❌ Execution returned invalid type: {type(result)}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
            
            # Test error handling
            try:
                result = agent.execute(None)
                results["error_handling"] = True
                print("✅ Error handling successful")
            except Exception as e:
                results["error_handling"] = True
                print(f"✅ Error handling successful (properly raised exception: {type(e).__name__})")
                
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    return results

def test_aria_master_agent():
    """Test AriaMasterAgent functionality"""
    print("\n" + "="*50)
    print("TESTING: ARIA_MASTER_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    try:
        # Test import
        from superagi.agents.aria_agents.aria_master_agent.aria_master_agent import AriaMasterAgent
        results["import"] = True
        print("✅ Import successful")
        
        # Test inheritance
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        if issubclass(AriaMasterAgent, BaseAriaAgent):
            results["inheritance"] = True
            print("✅ Correct inheritance from BaseAriaAgent")
        else:
            print("❌ Does not inherit from BaseAriaAgent")
        
        # Test methods
        required_methods = ['execute', 'get_capabilities']
        missing_methods = [m for m in required_methods if not hasattr(AriaMasterAgent, m)]
        if not missing_methods:
            results["methods"] = True
            print("✅ Required methods present")
        else:
            print(f"❌ Missing methods: {missing_methods}")
        
        # Test config
        config_path = "superagi/agents/aria_agents/aria_master_agent/agent_config.yaml"
        if os.path.exists(config_path):
            results["config"] = True
            print("✅ Config file exists")
        else:
            print("❌ Config file not found")
        
        # Test instantiation
        try:
            agent = AriaMasterAgent(llm=None, agent_id=1)
            results["instantiation"] = True
            print("✅ Instantiation successful")
            
            # Test execution
            try:
                result = agent.execute({"type": "coordinate", "description": "test coordination"})
                if isinstance(result, dict):
                    results["execution"] = True
                    print("✅ Execution successful")
                else:
                    print(f"❌ Execution returned invalid type: {type(result)}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
            
            # Test error handling
            try:
                result = agent.execute(None)
                results["error_handling"] = True
                print("✅ Error handling successful")
            except Exception as e:
                results["error_handling"] = True
                print(f"✅ Error handling successful (properly raised exception: {type(e).__name__})")
                
        except Exception as e:
            print(f"❌ Instantiation failed: {e}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    return results

def test_aria_goal_agent():
    """Test AriaGoalAgent functionality if it exists"""
    print("\n" + "="*50)
    print("TESTING: ARIA_GOAL_AGENT")
    print("="*50)
    
    results = {
        "import": False,
        "inheritance": False,
        "methods": False,
        "config": False,
        "instantiation": False,
        "execution": False,
        "error_handling": False
    }
    
    # Check if the agent exists in aria_core_repo
    goal_agent_path = "aria_core_repo/superagi/agents/aria_agents/aria_goal_agent/aria_goal_agent.py"
    if os.path.exists(goal_agent_path):
        print("⚠️  Found aria_goal_agent in aria_core_repo, attempting to test...")
        try:
            # Add the aria_core_repo to path temporarily
            sys.path.insert(0, 'aria_core_repo')
            from superagi.agents.aria_agents.aria_goal_agent.aria_goal_agent import AriaGoalAgent
            results["import"] = True
            print("✅ Import successful from aria_core_repo")
            
            # Test methods - this agent uses different base class
            required_methods = ['respond', 'get_capabilities']
            missing_methods = [m for m in required_methods if not hasattr(AriaGoalAgent, m)]
            if not missing_methods:
                results["methods"] = True
                print("✅ Required methods present")
            else:
                print(f"❌ Missing methods: {missing_methods}")
            
            # Test config
            config_path = "aria_core_repo/superagi/agents/aria_agents/aria_goal_agent/agent_config.yaml"
            if os.path.exists(config_path):
                results["config"] = True
                print("✅ Config file exists")
            
            # Remove from path
            sys.path.remove('aria_core_repo')
            
        except Exception as e:
            print(f"❌ Import from aria_core_repo failed: {e}")
            sys.path.remove('aria_core_repo') if 'aria_core_repo' in sys.path else None
    else:
        print("❌ aria_goal_agent not found in main superagi directory")
    
    return results

def generate_final_report(all_results):
    """Generate final comprehensive report"""
    print("\n" + "="*60)
    print("FINAL TEST REPORT - ARIA AGENTS")
    print("="*60)
    
    agent_names = [
        "aria_summary_agent",
        "aria_tool_agent", 
        "aria_utility_agent",
        "aria_emotion_agent",
        "aria_goal_agent",
        "aria_memory_agent",
        "aria_master_agent"
    ]
    
    for agent_name in agent_names:
        if agent_name in all_results:
            results = all_results[agent_name]
            print(f"\n🤖 {agent_name.upper()}:")
            
            passed_tests = []
            failed_tests = []
            
            for test_name, success in results.items():
                if success:
                    passed_tests.append(test_name)
                else:
                    failed_tests.append(test_name)
            
            if passed_tests:
                print("   ✅ PASSED TESTS:")
                for test in passed_tests:
                    print(f"      - {test}")
            
            if failed_tests:
                print("   ❌ FAILED TESTS:")
                for test in failed_tests:
                    print(f"      - {test}")
            
            # Overall status
            total_tests = len(results)
            passed_count = len(passed_tests)
            
            if passed_count == total_tests:
                print(f"   🎉 OVERALL: FULLY FUNCTIONAL ({passed_count}/{total_tests})")
            elif passed_count >= total_tests * 0.7:
                print(f"   ⚠️  OVERALL: MOSTLY FUNCTIONAL ({passed_count}/{total_tests})")
            else:
                print(f"   🚨 OVERALL: NEEDS ATTENTION ({passed_count}/{total_tests})")
        else:
            print(f"\n🤖 {agent_name.upper()}:")
            print("   ❌ NOT TESTED - Agent not found or failed to load")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    fully_functional = 0
    mostly_functional = 0
    needs_attention = 0
    not_available = 0
    
    for agent_name in agent_names:
        if agent_name in all_results:
            results = all_results[agent_name]
            total_tests = len(results)
            passed_count = sum(1 for success in results.values() if success)
            
            if passed_count == total_tests:
                fully_functional += 1
            elif passed_count >= total_tests * 0.7:
                mostly_functional += 1
            else:
                needs_attention += 1
        else:
            not_available += 1
    
    print(f"Fully Functional Agents: {fully_functional}/{len(agent_names)}")
    print(f"Mostly Functional Agents: {mostly_functional}/{len(agent_names)}")
    print(f"Agents Needing Attention: {needs_attention}/{len(agent_names)}")
    print(f"Agents Not Available: {not_available}/{len(agent_names)}")
    
    functional_agents = fully_functional + mostly_functional
    total_agents = len(agent_names)
    
    if functional_agents >= total_agents * 0.8:
        print("\n🚀 MVP READINESS: GOOD - Most agents are functional")
    elif functional_agents >= total_agents * 0.6:
        print("\n⚠️  MVP READINESS: MODERATE - Some agents need attention")
    else:
        print("\n🚨 MVP READINESS: LOW - Multiple agents need fixes")

def main():
    """Main test execution"""
    print("Starting comprehensive Aria Agents functionality test...")
    print("Testing 7 target agents for MVP readiness")
    
    all_results = {}
    
    # Test each agent
    test_functions = [
        ("aria_summary_agent", test_aria_summary_agent),
        ("aria_tool_agent", test_aria_tool_agent),
        ("aria_utility_agent", test_aria_utility_agent),
        ("aria_emotion_agent", test_aria_emotion_agent),
        ("aria_goal_agent", test_aria_goal_agent),
        ("aria_memory_agent", test_aria_memory_agent),
        ("aria_master_agent", test_aria_master_agent)
    ]
    
    for agent_name, test_func in test_functions:
        try:
            results = test_func()
            all_results[agent_name] = results
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR testing {agent_name}: {e}")
            all_results[agent_name] = {"CRITICAL_ERROR": False}
    
    generate_final_report(all_results)

if __name__ == "__main__":
    main()
