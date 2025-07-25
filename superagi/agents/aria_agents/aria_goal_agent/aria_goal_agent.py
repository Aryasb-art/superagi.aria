"""
AriaGoalAgent - Advanced goal and intent detection system
"""

import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger

class AriaGoalAgent(BaseAriaAgent):
    """
    Aria Goal Agent - Handles goal setting, tracking, and achievement
    """

    def __init__(self, session, agent_id, agent_config=None):
        super().__init__(session, agent_id, agent_config)
        self.config = self._load_config()

    def get_agent_type(self) -> str:
        """Return agent type"""
        return "AriaGoalAgent"

    """
    AriaGoalAgent handles comprehensive goal processing including:
    - Goal detection and recognition
    - Intent analysis and categorization
    - Goal planning and tracking
    - Motivation assessment
    - Behavioral pattern analysis
    """

    def __init__(self, llm, agent_id: int, agent_execution_id: int = None):
        super().__init__(llm, agent_id, agent_execution_id)
        self.agent_name = "AriaGoalAgent"
        self.goal_history = []
        self.current_goals = []
        self.goal_patterns = {}
        self.intent_categories = [
            "action/initiation", "decision/choice", "concern/worry",
            "motivation/energy", "confusion/help", "planning/organization",
            "learning/knowledge", "health/wellness", "relationship/social",
            "career/work", "general/other"
        ]

    def get_capabilities(self) -> List[str]:
        """Return the capabilities of this agent"""
        return [
            "goal_detection",
            "intent_analysis", 
            "goal_planning",
            "motivation_assessment",
            "behavioral_analysis",
            "pattern_recognition",
            "goal_tracking"
        ]

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute goal-related tasks

        Args:
            task: Dictionary containing task information

        Returns:
            Dictionary containing execution results
        """
        try:
            task_type = task.get('type', 'analyze_goal')

            if task_type == 'detect_goal':
                return self._detect_goal(task)
            elif task_type == 'analyze_intent':
                return self._analyze_intent(task)
            elif task_type == 'plan_goal':
                return self._plan_goal(task)
            elif task_type == 'track_progress':
                return self._track_progress(task)
            elif task_type == 'assess_motivation':
                return self._assess_motivation(task)
            else:
                return self._general_goal_analysis(task)

        except Exception as e:
            logger.error(f"AriaGoalAgent execution error: {str(e)}")
            return {
                "status": "error",
                "message": f"Goal processing failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _detect_goal(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Detect goals from input data"""
        try:
            input_text = task.get('input', '')
            context = task.get('context', {})

            # Simple goal detection logic
            goal_keywords = {
                'want': 'desire/intention',
                'need': 'necessity/requirement', 
                'plan': 'planning/organization',
                'should': 'decision/choice',
                'help': 'confusion/help',
                'learn': 'learning/knowledge'
            }

            detected_goals = []
            input_lower = input_text.lower()

            for keyword, category in goal_keywords.items():
                if keyword in input_lower:
                    detected_goals.append({
                        'keyword': keyword,
                        'category': category,
                        'confidence': 0.7
                    })

            if not detected_goals:
                detected_goals.append({
                    'keyword': 'general',
                    'category': 'general/other',
                    'confidence': 0.5
                })

            # Store in history
            goal_entry = {
                'id': f"goal_{int(time.time() * 1000)}",
                'input_text': input_text,
                'detected_goals': detected_goals,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }

            self.goal_history.append(goal_entry)

            return {
                "status": "success",
                "message": "Goal detection completed",
                "goal_id": goal_entry['id'],
                "detected_goals": detected_goals,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Goal detection error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to detect goal: {str(e)}"
            }

    def _analyze_intent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user intent"""
        try:
            input_text = task.get('input', '')

            # Simple intent analysis
            intent_patterns = {
                'action/initiation': ['want to', 'going to', 'will'],
                'decision/choice': ['should I', 'which', 'better'],
                'confusion/help': ['confused', 'help', 'don\'t know'],
                'learning/knowledge': ['learn', 'understand', 'know']
            }

            intent_scores = {}
            input_lower = input_text.lower()

            for intent, patterns in intent_patterns.items():
                score = sum(1 for pattern in patterns if pattern in input_lower)
                if score > 0:
                    intent_scores[intent] = score / len(patterns)

            if intent_scores:
                primary_intent = max(intent_scores, key=intent_scores.get)
                confidence = intent_scores[primary_intent]
            else:
                primary_intent = 'general/other'
                confidence = 0.3

            return {
                "status": "success",
                "message": "Intent analysis completed",
                "primary_intent": primary_intent,
                "confidence": confidence,
                "all_intents": intent_scores,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to analyze intent: {str(e)}"
            }

    def _plan_goal(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a goal planning structure"""
        try:
            goal_description = task.get('goal', '')
            priority = task.get('priority', 'medium')
            timeline = task.get('timeline', 'medium_term')

            # Simple goal planning
            plan_steps = self._generate_plan_steps(goal_description)

            goal_plan = {
                'id': f"plan_{int(time.time() * 1000)}",
                'goal': goal_description,
                'priority': priority,
                'timeline': timeline,
                'steps': plan_steps,
                'created_at': datetime.now().isoformat(),
                'status': 'planned'
            }

            self.current_goals.append(goal_plan)

            return {
                "status": "success",
                "message": "Goal planning completed",
                "plan": goal_plan,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Goal planning error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to plan goal: {str(e)}"
            }

    def _track_progress(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Track progress on existing goals"""
        try:
            goal_id = task.get('goal_id')
            progress_update = task.get('progress', {})

            if goal_id:
                # Find and update specific goal
                for goal in self.current_goals:
                    if goal['id'] == goal_id:
                        goal['progress'] = progress_update
                        goal['last_updated'] = datetime.now().isoformat()
                        break

                return {
                    "status": "success",
                    "message": "Goal progress updated",
                    "goal_id": goal_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Return general progress overview
                progress_summary = {
                    'total_goals': len(self.current_goals),
                    'active_goals': len([g for g in self.current_goals if g.get('status') == 'active']),
                    'completed_goals': len([g for g in self.current_goals if g.get('status') == 'completed'])
                }

                return {
                    "status": "success",
                    "message": "Progress tracking completed",
                    "summary": progress_summary,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Progress tracking error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to track progress: {str(e)}"
            }

    def _assess_motivation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assess motivation levels and factors"""
        try:
            context = task.get('context', {})
            recent_activity = task.get('recent_activity', [])

            # Simple motivation assessment
            motivation_factors = {
                'goal_clarity': 0.7,
                'progress_satisfaction': 0.6,
                'external_support': 0.5,
                'intrinsic_drive': 0.8
            }

            overall_motivation = sum(motivation_factors.values()) / len(motivation_factors)

            assessment = {
                'overall_score': overall_motivation,
                'factors': motivation_factors,
                'assessment_date': datetime.now().isoformat(),
                'recommendations': self._generate_motivation_recommendations(overall_motivation)
            }

            return {
                "status": "success",
                "message": "Motivation assessment completed",
                "assessment": assessment,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Motivation assessment error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to assess motivation: {str(e)}"
            }

    def _general_goal_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general goal analysis tasks"""
        try:
            # Perform general goal state analysis
            current_analysis = {
                "total_goals_tracked": len(self.goal_history),
                "current_active_goals": len(self.current_goals),
                "recent_goal_count": len(self.goal_history[-10:]),
                "most_common_category": self._get_most_common_category()
            }

            return {
                "status": "success",
                "message": "General goal analysis completed",
                "analysis": current_analysis,
                "task_processed": task.get('description', 'General goal task'),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"General goal analysis error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to analyze goals: {str(e)}"
            }

    # Helper methods

    def _generate_plan_steps(self, goal_description: str) -> List[Dict[str, Any]]:
        """Generate basic plan steps for a goal"""
        # Simple step generation based on goal keywords
        if 'learn' in goal_description.lower():
            return [
                {'step': 1, 'action': 'Identify learning resources', 'status': 'pending'},
                {'step': 2, 'action': 'Create study schedule', 'status': 'pending'},
                {'step': 3, 'action': 'Begin learning process', 'status': 'pending'},
                {'step': 4, 'action': 'Practice and apply knowledge', 'status': 'pending'},
                {'step': 5, 'action': 'Evaluate progress', 'status': 'pending'}
            ]
        elif 'plan' in goal_description.lower():
            return [
                {'step': 1, 'action': 'Define objectives', 'status': 'pending'},
                {'step': 2, 'action': 'Gather requirements', 'status': 'pending'},
                {'step': 3, 'action': 'Create timeline', 'status': 'pending'},
                {'step': 4, 'action': 'Execute plan', 'status': 'pending'},
                {'step': 5, 'action': 'Monitor and adjust', 'status': 'pending'}
            ]
        else:
            return [
                {'step': 1, 'action': 'Analyze goal requirements', 'status': 'pending'},
                {'step': 2, 'action': 'Develop action plan', 'status': 'pending'},
                {'step': 3, 'action': 'Take initial steps', 'status': 'pending'},
                {'step': 4, 'action': 'Review progress', 'status': 'pending'}
            ]

    def _generate_motivation_recommendations(self, motivation_score: float) -> List[str]:
        """Generate recommendations based on motivation score"""
        if motivation_score >= 0.8:
            return [
                "Maintain current momentum",
                "Consider taking on additional challenges",
                "Share your success with others"
            ]
        elif motivation_score >= 0.6:
            return [
                "Focus on maintaining consistency",
                "Celebrate small wins",
                "Identify and address minor obstacles"
            ]
        else:
            return [
                "Break goals into smaller, manageable steps",
                "Seek support from others",
                "Revisit your why - reconnect with your motivation",
                "Consider adjusting goals to be more realistic"
            ]

    def _get_most_common_category(self) -> str:
        """Get the most common goal category from history"""
        if not self.goal_history:
            return "general/other"

        categories = []
        for entry in self.goal_history:
            for goal in entry.get('detected_goals', []):
                categories.append(goal.get('category', 'general/other'))

        if categories:
            return max(set(categories), key=categories.count)
        return "general/other"

    def get_goal_stats(self) -> Dict[str, Any]:
        """Get current goal statistics"""
        return {
            "total_goals_tracked": len(self.goal_history),
            "current_active_goals": len(self.current_goals),
            "recent_goals": [entry['detected_goals'] for entry in self.goal_history[-5:]],
            "most_common_category": self._get_most_common_category()
        }