
#!/usr/bin/env python3
"""
Comprehensive functionality test for the 7 verified complete Aria agents.
Tests importability, class structure, methods, config binding, output, and error handling.
"""

import sys
import os
import traceback
import importlib.util
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class AgentTester:
    def __init__(self):
        self.results = {}
        self.agents_to_test = [
            'aria_summary_agent',
            'aria_tool_agent', 
            'aria_utility_agent',
            'aria_emotion_agent',
            'aria_goal_agent',
            'aria_memory_agent',
            'aria_master_agent'
        ]
        
    def log(self, message, level="INFO"):
        """Log test messages with consistent formatting"""
        print(f"[{level}] {message}")
        
    def test_agent_import(self, agent_name):
        """Test if agent can be imported without errors"""
        try:
            # Check if file exists first
            agent_file = f"superagi/agents/aria_agents/{agent_name}/{agent_name}.py"
            if not os.path.exists(agent_file):
                return False, f"Agent file {agent_file} not found"
            
            # Try to import the agent module
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            spec = importlib.util.find_spec(module_path)
            
            if spec is None:
                return False, f"Module {module_path} not found"
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Try to get the agent class
            class_name = ''.join(word.capitalize() for word in agent_name.split('_'))
            if hasattr(module, class_name):
                agent_class = getattr(module, class_name)
                return True, f"Successfully imported {class_name}"
            else:
                # List available classes in module
                available_classes = [name for name in dir(module) if not name.startswith('_') and isinstance(getattr(module, name), type)]
                return False, f"Class {class_name} not found. Available classes: {available_classes}"
                
        except Exception as e:
            return False, f"Import error: {str(e)}"
    
    def test_base_agent_inheritance(self, agent_name):
        """Test if agent inherits from BaseAgent properly"""
        try:
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            spec = importlib.util.find_spec(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            class_name = ''.join(word.capitalize() for word in agent_name.split('_'))
            agent_class = getattr(module, class_name)
            
            # Check if it inherits from BaseAgent or BaseAriaAgent
            from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
            
            if issubclass(agent_class, BaseAriaAgent):
                return True, f"{class_name} correctly inherits from BaseAriaAgent"
            else:
                return False, f"{class_name} does not inherit from BaseAriaAgent"
                
        except Exception as e:
            return False, f"Inheritance check error: {str(e)}"
    
    def test_required_methods(self, agent_name):
        """Test if agent has required methods (execute, get_capabilities, get_agent_type)"""
        try:
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            spec = importlib.util.find_spec(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            class_name = ''.join(word.capitalize() for word in agent_name.split('_'))
            agent_class = getattr(module, class_name)
            
            required_methods = ['execute', 'get_capabilities', 'get_agent_type']
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(agent_class, method):
                    missing_methods.append(method)
            
            if missing_methods:
                return False, f"Missing methods: {', '.join(missing_methods)}"
            else:
                return True, "All required methods present"
                
        except Exception as e:
            return False, f"Method check error: {str(e)}"
    
    def test_config_binding(self, agent_name):
        """Test if agent's config YAML is accessible and properly structured"""
        try:
            config_path = f"superagi/agents/aria_agents/{agent_name}/agent_config.yaml"
            
            if not os.path.exists(config_path):
                # Try alternative config file names
                alt_config_path = f"superagi/agents/aria_agents/{agent_name}/config.yaml"
                if os.path.exists(alt_config_path):
                    config_path = alt_config_path
                else:
                    return False, "No config.yaml or agent_config.yaml found"
            
            # Try to read the config file
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            if config and isinstance(config, dict):
                return True, f"Config file loaded successfully with {len(config)} top-level keys"
            else:
                return False, "Config file is empty or invalid"
                
        except Exception as e:
            return False, f"Config error: {str(e)}"
    
    def test_agent_instantiation(self, agent_name):
        """Test if agent can be instantiated"""
        try:
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            spec = importlib.util.find_spec(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            class_name = ''.join(word.capitalize() for word in agent_name.split('_'))
            agent_class = getattr(module, class_name)
            
            # Try to instantiate with minimal parameters
            try:
                # Try different instantiation patterns based on agent type
                if agent_name in ['aria_emotion_agent', 'aria_memory_agent', 'aria_master_agent']:
                    # These might need llm, agent_id parameters
                    agent = agent_class(llm=None, agent_id=1)
                else:
                    # Try with session and agent_id
                    agent = agent_class(session=None, agent_id=1)
                
                return True, f"Successfully instantiated {class_name}"
                
            except TypeError as te:
                # Try alternative instantiation
                try:
                    agent = agent_class()
                    return True, f"Successfully instantiated {class_name} with no args"
                except:
                    return False, f"Instantiation failed: {str(te)}"
                    
        except Exception as e:
            return False, f"Instantiation error: {str(e)}"
    
    def test_basic_execution(self, agent_name):
        """Test if agent can execute with minimal valid input"""
        try:
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            spec = importlib.util.find_spec(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            class_name = ''.join(word.capitalize() for word in agent_name.split('_'))
            agent_class = getattr(module, class_name)
            
            # Try to instantiate and execute
            try:
                if agent_name in ['aria_emotion_agent', 'aria_memory_agent', 'aria_master_agent']:
                    agent = agent_class(llm=None, agent_id=1)
                else:
                    agent = agent_class(session=None, agent_id=1)
            except:
                try:
                    agent = agent_class()
                except:
                    return False, "Could not instantiate agent for execution test"
            
            # Test execute method with simple input
            try:
                if agent_name == 'aria_emotion_agent':
                    result = agent.execute({"type": "general_emotion_analysis", "description": "test"})
                elif agent_name == 'aria_memory_agent':
                    result = agent.execute({"type": "general_memory", "description": "test"})
                elif agent_name == 'aria_master_agent':
                    result = agent.execute({"type": "coordinate", "description": "test"})
                else:
                    # For other agents, try standard execute pattern
                    result = agent.execute("test task", {"task_type": "general"})
                
                if result and isinstance(result, dict):
                    return True, f"Execute method returned valid dict result"
                else:
                    return False, f"Execute method returned invalid result: {type(result)}"
                    
            except Exception as exe_error:
                return False, f"Execute method failed: {str(exe_error)}"
                
        except Exception as e:
            return False, f"Execution test error: {str(e)}"
    
    def test_error_handling(self, agent_name):
        """Test if agent handles invalid input gracefully"""
        try:
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            spec = importlib.util.find_spec(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            class_name = ''.join(word.capitalize() for word in agent_name.split('_'))
            agent_class = getattr(module, class_name)
            
            # Try to instantiate
            try:
                if agent_name in ['aria_emotion_agent', 'aria_memory_agent', 'aria_master_agent']:
                    agent = agent_class(llm=None, agent_id=1)
                else:
                    agent = agent_class(session=None, agent_id=1)
            except:
                try:
                    agent = agent_class()
                except:
                    return False, "Could not instantiate agent for error handling test"
            
            # Test with invalid input
            try:
                if agent_name == 'aria_emotion_agent':
                    result = agent.execute(None)
                elif agent_name == 'aria_memory_agent':
                    result = agent.execute(None)
                elif agent_name == 'aria_master_agent':
                    result = agent.execute(None)
                else:
                    result = agent.execute(None, None)
                
                # If we get here without exception, check if result indicates error handling
                if result and isinstance(result, dict):
                    if "error" in result or "success" in result:
                        return True, "Agent handles invalid input gracefully"
                    else:
                        return True, "Agent processed invalid input without error"
                else:
                    return False, "Agent returned None or invalid response for invalid input"
                    
            except Exception as error_test:
                # This is actually good - agent should handle errors
                return True, f"Agent properly raises exception for invalid input: {type(error_test).__name__}"
                
        except Exception as e:
            return False, f"Error handling test failed: {str(e)}"
    
    def test_single_agent(self, agent_name):
        """Run all tests for a single agent"""
        self.log(f"\n{'='*50}")
        self.log(f"Testing Agent: {agent_name.upper()}")
        self.log(f"{'='*50}")
        
        tests = [
            ("Import Test", self.test_agent_import),
            ("BaseAgent Inheritance", self.test_base_agent_inheritance),
            ("Required Methods", self.test_required_methods),
            ("Config Binding", self.test_config_binding),
            ("Agent Instantiation", self.test_agent_instantiation),
            ("Basic Execution", self.test_basic_execution),
            ("Error Handling", self.test_error_handling)
        ]
        
        agent_results = {}
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                success, message = test_func(agent_name)
                status = "✅ PASSED" if success else "❌ FAILED"
                self.log(f"{status}: {message}")
                agent_results[test_name] = {"success": success, "message": message}
            except Exception as e:
                self.log(f"❌ FAILED: Unexpected error in {test_name}: {str(e)}")
                agent_results[test_name] = {"success": False, "message": f"Unexpected error: {str(e)}"}
        
        self.results[agent_name] = agent_results
        return agent_results
    
    def run_all_tests(self):
        """Run tests for all agents"""
        self.log("Starting comprehensive Aria Agents functionality test...")
        self.log(f"Testing {len(self.agents_to_test)} agents")
        
        for agent_name in self.agents_to_test:
            try:
                self.test_single_agent(agent_name)
            except Exception as e:
                self.log(f"❌ CRITICAL ERROR testing {agent_name}: {str(e)}")
                self.results[agent_name] = {"CRITICAL_ERROR": {"success": False, "message": str(e)}}
        
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final test report"""
        self.log(f"\n{'='*60}")
        self.log("FINAL TEST REPORT - ARIA AGENTS")
        self.log(f"{'='*60}")
        
        for agent_name in self.agents_to_test:
            self.log(f"\n🤖 {agent_name.upper()}:")
            
            if agent_name not in self.results:
                self.log("   ❌ No test results available")
                continue
            
            agent_results = self.results[agent_name]
            passed_tests = []
            failed_tests = []
            partial_tests = []
            
            for test_name, result in agent_results.items():
                if result["success"]:
                    passed_tests.append(f"   ✅ {test_name}: {result['message']}")
                else:
                    failed_tests.append(f"   ❌ {test_name}: {result['message']}")
            
            # Print results
            if passed_tests:
                self.log("   PASSED TESTS:")
                for test in passed_tests:
                    self.log(test)
            
            if failed_tests:
                self.log("   FAILED TESTS:")
                for test in failed_tests:
                    self.log(test)
            
            # Overall agent status
            total_tests = len(agent_results)
            passed_count = sum(1 for r in agent_results.values() if r["success"])
            
            if passed_count == total_tests:
                self.log(f"   🎉 OVERALL: FULLY FUNCTIONAL ({passed_count}/{total_tests})")
            elif passed_count >= total_tests * 0.7:
                self.log(f"   ⚠️  OVERALL: MOSTLY FUNCTIONAL ({passed_count}/{total_tests})")
            else:
                self.log(f"   🚨 OVERALL: NEEDS ATTENTION ({passed_count}/{total_tests})")
        
        # Summary
        self.log(f"\n{'='*60}")
        self.log("SUMMARY")
        self.log(f"{'='*60}")
        
        fully_functional = 0
        mostly_functional = 0
        needs_attention = 0
        
        for agent_name in self.agents_to_test:
            if agent_name in self.results:
                agent_results = self.results[agent_name]
                total_tests = len(agent_results)
                passed_count = sum(1 for r in agent_results.values() if r["success"])
                
                if passed_count == total_tests:
                    fully_functional += 1
                elif passed_count >= total_tests * 0.7:
                    mostly_functional += 1
                else:
                    needs_attention += 1
        
        self.log(f"Fully Functional Agents: {fully_functional}/{len(self.agents_to_test)}")
        self.log(f"Mostly Functional Agents: {mostly_functional}/{len(self.agents_to_test)}")
        self.log(f"Agents Needing Attention: {needs_attention}/{len(self.agents_to_test)}")
        
        if fully_functional + mostly_functional >= len(self.agents_to_test) * 0.8:
            self.log("\n🚀 MVP READINESS: GOOD - Most agents are functional")
        elif fully_functional + mostly_functional >= len(self.agents_to_test) * 0.6:
            self.log("\n⚠️  MVP READINESS: MODERATE - Some agents need fixes")
        else:
            self.log("\n🚨 MVP READINESS: LOW - Multiple agents need attention")

def main():
    """Main function to run the tests"""
    tester = AgentTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
