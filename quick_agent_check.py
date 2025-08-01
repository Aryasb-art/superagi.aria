
import os
import sys

# Add project root to path
sys.path.insert(0, '.')

def check_agent_files():
    """Check which agent files actually exist"""
    agents_dir = "superagi/agents/aria_agents"
    
    if not os.path.exists(agents_dir):
        print(f"❌ Agents directory not found: {agents_dir}")
        return
    
    target_agents = [
        'aria_summary_agent',
        'aria_tool_agent', 
        'aria_utility_agent',
        'aria_emotion_agent',
        'aria_goal_agent',
        'aria_memory_agent',
        'aria_master_agent'
    ]
    
    print("📁 Checking agent directory structure...")
    
    for agent_name in target_agents:
        agent_dir = os.path.join(agents_dir, agent_name)
        agent_py = os.path.join(agent_dir, f"{agent_name}.py")
        config_yaml = os.path.join(agent_dir, "agent_config.yaml")
        alt_config = os.path.join(agent_dir, "config.yaml")
        
        print(f"\n🤖 {agent_name}:")
        print(f"   Directory: {'✅' if os.path.exists(agent_dir) else '❌'}")
        print(f"   Python file: {'✅' if os.path.exists(agent_py) else '❌'}")
        print(f"   Config YAML: {'✅' if os.path.exists(config_yaml) else '✅' if os.path.exists(alt_config) else '❌'}")
        
        if os.path.exists(agent_dir):
            files = os.listdir(agent_dir)
            print(f"   Files: {files}")

def test_imports():
    """Test basic imports"""
    print("\n🔍 Testing basic imports...")
    
    # Test base agent import
    try:
        from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
        print("✅ BaseAriaAgent import successful")
    except Exception as e:
        print(f"❌ BaseAriaAgent import failed: {e}")
    
    # Test individual agents
    target_agents = [
        'aria_summary_agent',
        'aria_tool_agent', 
        'aria_utility_agent',
        'aria_emotion_agent',
        'aria_memory_agent',
        'aria_master_agent'
    ]
    
    for agent_name in target_agents:
        try:
            module_path = f"superagi.agents.aria_agents.{agent_name}.{agent_name}"
            exec(f"from {module_path} import *")
            print(f"✅ {agent_name} import successful")
        except Exception as e:
            print(f"❌ {agent_name} import failed: {e}")

if __name__ == "__main__":
    check_agent_files()
    test_imports()
