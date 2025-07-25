#!/usr/bin/env python3
"""
Fix OpenAI API fallback mechanisms across all agents
"""
import os
import re

def add_openai_fallback_to_agent(agent_path, agent_name):
    """Add comprehensive OpenAI fallback to agent"""
    try:
        with open(agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has proper fallback
        if 'insufficient_quota' in content and 'fallback' in content:
            print(f"✅ {agent_name} already has OpenAI fallback")
            return True
        
        # Add fallback wrapper function
        fallback_code = '''
    def _safe_openai_call(self, prompt, model="gpt-4o", max_tokens=150, temperature=0.3):
        """
        Safe OpenAI API call with comprehensive error handling and fallback
        """
        try:
            if not hasattr(self, 'openai_client') or not self.openai_client:
                return self._fallback_response(prompt)
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['quota', 'rate_limit', '429', 'insufficient_quota']):
                self.logger.warning(f"[{self.name}] OpenAI quota exceeded, using fallback")
                return self._fallback_response(prompt)
            elif 'timeout' in error_msg:
                self.logger.warning(f"[{self.name}] OpenAI timeout, using fallback")
                return self._fallback_response(prompt)
            else:
                self.logger.error(f"[{self.name}] OpenAI error: {e}, using fallback")
                return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt):
        """
        Fallback response when OpenAI is unavailable
        """
        prompt_lower = prompt.lower()
        
        # Simple keyword-based responses
        if any(word in prompt_lower for word in ['sad', 'unhappy', 'depressed', 'down']):
            return "متوجه می‌شوم که احساس غمگینی دارید. این احساس طبیعی است و گذرا خواهد بود."
        elif any(word in prompt_lower for word in ['happy', 'good', 'great', 'excellent']):
            return "خوشحالم که احساس خوبی دارید! این انرژی مثبت را حفظ کنید."
        elif any(word in prompt_lower for word in ['angry', 'mad', 'furious', 'upset']):
            return "متوجه خشم شما هستم. تنفس عمیق کنید و کمی وقت بگذارید."
        elif any(word in prompt_lower for word in ['confused', 'lost', 'unclear']):
            return "گاهی گیج شدن طبیعی است. آرام باشید و مرحله به مرحله فکر کنید."
        else:
            return "پیام شما دریافت شد. به دلیل محدودیت‌های فنی، پاسخ ساده ارائه می‌دهم."
'''
        
        # Find the class definition and add the fallback methods
        class_match = re.search(r'class\s+(\w+)\s*\([^)]+\):', content)
        if class_match:
            class_start = class_match.end()
            # Find the end of __init__ method
            init_match = re.search(r'def __init__\(self[^)]*\):[^}]+?(?=\n    def|\nclass|\n\n|\Z)', content[class_start:])
            if init_match:
                insert_pos = class_start + init_match.end()
                new_content = content[:insert_pos] + fallback_code + content[insert_pos:]
                
                # Write back the modified content
                with open(agent_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Added OpenAI fallback to {agent_name}")
                return True
        
        print(f"❌ Could not add fallback to {agent_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error processing {agent_name}: {e}")
        return False

def main():
    """Main function to add fallbacks to all agents"""
    print("🔧 Adding OpenAI Fallback Mechanisms to All Agents...")
    print("=" * 60)
    
    agents_dir = "agents"
    if not os.path.exists(agents_dir):
        print("❌ Agents directory not found!")
        return
    
    # List of agent files to process
    agent_files = [
        "emotion_regulation_agent.py",
        "utility_agent.py",
        "tool_agent.py",
        "summary_agent.py",
        "conceptual_memory_agent.py",
        "goal_inference_agent.py",
        "bias_detection_agent.py",
        "cognitive_distortion_agent.py",
        "ethical_reasoning_agent.py",
        "advanced_memory_manager_agent.py"
    ]
    
    success_count = 0
    for agent_file in agent_files:
        agent_path = os.path.join(agents_dir, agent_file)
        if os.path.exists(agent_path):
            agent_name = agent_file.replace('.py', '')
            if add_openai_fallback_to_agent(agent_path, agent_name):
                success_count += 1
        else:
            print(f"⚠️ Agent file not found: {agent_file}")
    
    print(f"\n📊 Summary: {success_count}/{len(agent_files)} agents updated")
    print("✅ OpenAI fallback mechanisms added successfully!")

if __name__ == "__main__":
    main()