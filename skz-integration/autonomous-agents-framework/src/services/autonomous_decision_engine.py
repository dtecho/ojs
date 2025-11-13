"""
ML-Powered Decision Engine - Autonomous Goal-Oriented Decision Making
Implements constraint management, risk assessment, and adaptive planning
Phase 1: Foundation ML Infrastructure - Week 4
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DecisionPriority(Enum):
    """Decision priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class Goal:
    """Represents an agent goal with constraints and evaluation criteria"""
    
    def __init__(self, goal_id: str, description: str, priority: DecisionPriority,
                 constraints: Dict[str, Any], success_criteria: Dict[str, float]):
        self.goal_id = goal_id
        self.description = description
        self.priority = priority
        self.constraints = constraints
        self.success_criteria = success_criteria
        self.status = "active"
        self.progress = 0.0
        self.created_at = datetime.utcnow()


class MLDecisionEngine:
    """
    Production-grade ML-powered decision engine for autonomous agents
    Implements goal-oriented behavior, risk assessment, and adaptive planning
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize ML decision engine
        
        Args:
            agent_id: Unique agent identifier
        """
        self.agent_id = agent_id
        self.goals = {}
        self.decision_history = []
        self.constraints = {}
        self.risk_thresholds = {
            "safety": 0.95,
            "quality": 0.80,
            "efficiency": 0.70,
            "compliance": 0.99
        }
        
        logger.info(f"MLDecisionEngine initialized for agent: {agent_id}")
    
    def add_goal(self, goal_id: str, description: str, priority: DecisionPriority,
                 constraints: Dict[str, Any], success_criteria: Dict[str, float]) -> bool:
        """
        Add new goal to agent's goal hierarchy
        
        Args:
            goal_id: Unique goal identifier
            description: Goal description
            priority: Goal priority level
            constraints: Constraints that must be satisfied
            success_criteria: Criteria for goal success
            
        Returns:
            Success status
        """
        try:
            goal = Goal(goal_id, description, priority, constraints, success_criteria)
            self.goals[goal_id] = goal
            
            logger.info(f"Added goal: {goal_id} with priority {priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding goal: {e}")
            return False
    
    def evaluate_action(self, action: str, context: Dict[str, Any],
                       goals: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate potential action against goals and constraints
        
        Args:
            action: Action to evaluate
            context: Current context
            goals: Goals to consider (None = all active goals)
            
        Returns:
            Evaluation results with scores and recommendations
        """
        try:
            if goals is None:
                goals = [g_id for g_id, g in self.goals.items() if g.status == "active"]
            
            evaluation = {
                "action": action,
                "context": context,
                "goal_alignment": {},
                "constraint_satisfaction": {},
                "risk_assessment": {},
                "overall_score": 0.0,
                "recommendation": "",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Evaluate against each goal
            total_weight = 0.0
            weighted_score = 0.0
            
            for goal_id in goals:
                if goal_id not in self.goals:
                    continue
                
                goal = self.goals[goal_id]
                
                # Calculate goal alignment score
                alignment = self._calculate_goal_alignment(action, context, goal)
                evaluation["goal_alignment"][goal_id] = alignment
                
                # Weight by priority
                weight = 1.0 / goal.priority.value
                weighted_score += alignment * weight
                total_weight += weight
            
            # Calculate overall goal alignment
            if total_weight > 0:
                evaluation["overall_score"] = weighted_score / total_weight
            
            # Evaluate constraint satisfaction
            evaluation["constraint_satisfaction"] = self._evaluate_constraints(action, context)
            
            # Assess risks
            evaluation["risk_assessment"] = self._assess_risks(action, context)
            
            # Generate recommendation
            evaluation["recommendation"] = self._generate_recommendation(evaluation)
            
            # Store in decision history
            self.decision_history.append(evaluation)
            
            logger.info(f"Evaluated action '{action}': score={evaluation['overall_score']:.3f}, "
                       f"recommendation={evaluation['recommendation']}")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating action: {e}")
            return {"error": str(e)}
    
    def _calculate_goal_alignment(self, action: str, context: Dict[str, Any], 
                                  goal: Goal) -> float:
        """Calculate how well action aligns with goal"""
        # In production, use ML model trained on past outcomes
        # This is a simplified heuristic-based calculation
        
        score = 0.5  # Neutral baseline
        
        # Check if action keywords match goal description
        action_keywords = set(action.lower().split())
        goal_keywords = set(goal.description.lower().split())
        keyword_overlap = len(action_keywords & goal_keywords) / max(len(goal_keywords), 1)
        score += keyword_overlap * 0.3
        
        # Check success criteria
        for criterion, threshold in goal.success_criteria.items():
            if criterion in context:
                if context[criterion] >= threshold:
                    score += 0.2
        
        return min(1.0, score)
    
    def _evaluate_constraints(self, action: str, context: Dict[str, Any]) -> Dict[str, bool]:
        """Evaluate if action satisfies all constraints"""
        satisfaction = {}
        
        for constraint_name, constraint_spec in self.constraints.items():
            # Check if constraint is satisfied
            if constraint_spec["type"] == "threshold":
                field = constraint_spec["field"]
                threshold = constraint_spec["value"]
                operator = constraint_spec.get("operator", ">=")
                
                if field in context:
                    if operator == ">=":
                        satisfaction[constraint_name] = context[field] >= threshold
                    elif operator == "<=":
                        satisfaction[constraint_name] = context[field] <= threshold
                    elif operator == "==":
                        satisfaction[constraint_name] = context[field] == threshold
                else:
                    satisfaction[constraint_name] = False
            else:
                satisfaction[constraint_name] = True  # Unknown type, assume satisfied
        
        return satisfaction
    
    def _assess_risks(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with action"""
        risks = {
            "safety_risk": 0.0,
            "quality_risk": 0.0,
            "efficiency_risk": 0.0,
            "compliance_risk": 0.0,
            "overall_risk": 0.0
        }
        
        # Calculate risk scores based on context
        # In production, use trained risk prediction models
        
        # Safety risk
        if "safety_score" in context:
            risks["safety_risk"] = 1.0 - context["safety_score"]
        
        # Quality risk
        if "quality_score" in context:
            risks["quality_risk"] = 1.0 - context["quality_score"]
        
        # Efficiency risk (time-based)
        if "estimated_time" in context and "deadline" in context:
            time_ratio = context["estimated_time"] / max(context["deadline"], 1)
            risks["efficiency_risk"] = min(1.0, time_ratio)
        
        # Compliance risk
        if "compliance_score" in context:
            risks["compliance_risk"] = 1.0 - context["compliance_score"]
        
        # Overall risk (weighted average)
        risks["overall_risk"] = (
            risks["safety_risk"] * 0.4 +
            risks["quality_risk"] * 0.3 +
            risks["efficiency_risk"] * 0.2 +
            risks["compliance_risk"] * 0.1
        )
        
        return risks
    
    def _generate_recommendation(self, evaluation: Dict[str, Any]) -> str:
        """Generate recommendation based on evaluation"""
        score = evaluation["overall_score"]
        risks = evaluation["risk_assessment"]
        constraints = evaluation["constraint_satisfaction"]
        
        # Check if any critical constraints are violated
        if not all(constraints.values()):
            return "reject_constraint_violation"
        
        # Check if risks are too high
        if risks["overall_risk"] > 0.5:
            return "reject_high_risk"
        
        # Recommend based on score
        if score >= 0.8:
            return "approve_high_confidence"
        elif score >= 0.6:
            return "approve_moderate_confidence"
        elif score >= 0.4:
            return "review_required"
        else:
            return "reject_low_alignment"
    
    def select_best_action(self, available_actions: List[str], 
                          context: Dict[str, Any],
                          goals: List[str] = None) -> Dict[str, Any]:
        """
        Select best action from available options
        
        Args:
            available_actions: List of possible actions
            context: Current context
            goals: Goals to optimize for
            
        Returns:
            Selected action with justification
        """
        try:
            if not available_actions:
                return {"error": "no_actions_available"}
            
            # Evaluate all actions
            evaluations = []
            for action in available_actions:
                eval_result = self.evaluate_action(action, context, goals)
                evaluations.append((action, eval_result))
            
            # Sort by overall score (descending)
            evaluations.sort(key=lambda x: x[1]["overall_score"], reverse=True)
            
            # Select best action
            best_action, best_eval = evaluations[0]
            
            # Generate justification
            justification = self._generate_justification(best_action, best_eval, evaluations)
            
            return {
                "selected_action": best_action,
                "confidence": best_eval["overall_score"],
                "recommendation": best_eval["recommendation"],
                "justification": justification,
                "alternatives": [
                    {"action": action, "score": eval_result["overall_score"]}
                    for action, eval_result in evaluations[1:4]  # Top 3 alternatives
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error selecting best action: {e}")
            return {"error": str(e)}
    
    def _generate_justification(self, action: str, evaluation: Dict[str, Any],
                                all_evaluations: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Generate human-readable justification for decision"""
        parts = []
        
        # Main reason
        parts.append(f"Selected '{action}' with confidence {evaluation['overall_score']:.2f}")
        
        # Goal alignment
        if evaluation["goal_alignment"]:
            best_goal = max(evaluation["goal_alignment"].items(), key=lambda x: x[1])
            parts.append(f"Best aligned with goal '{best_goal[0]}' (score: {best_goal[1]:.2f})")
        
        # Risk assessment
        risk = evaluation["risk_assessment"]["overall_risk"]
        if risk < 0.2:
            parts.append("Low risk assessment")
        elif risk < 0.5:
            parts.append("Moderate risk (acceptable)")
        else:
            parts.append(f"High risk ({risk:.2f}) - requires caution")
        
        # Comparison with alternatives
        if len(all_evaluations) > 1:
            second_best_score = all_evaluations[1][1]["overall_score"]
            margin = evaluation["overall_score"] - second_best_score
            parts.append(f"Margin over next best option: {margin:.2f}")
        
        return ". ".join(parts)
    
    def adaptive_planning(self, goal_id: str, current_state: Dict[str, Any],
                         available_actions: List[str], horizon: int = 5) -> List[str]:
        """
        Generate adaptive plan to achieve goal
        
        Args:
            goal_id: Goal to plan for
            current_state: Current state
            available_actions: Available actions at each step
            horizon: Planning horizon (steps)
            
        Returns:
            Planned sequence of actions
        """
        try:
            if goal_id not in self.goals:
                return []
            
            goal = self.goals[goal_id]
            plan = []
            state = current_state.copy()
            
            # Iterative planning (greedy best-first)
            for step in range(horizon):
                # Select best action for current state
                decision = self.select_best_action(available_actions, state, [goal_id])
                
                if "error" in decision:
                    break
                
                action = decision["selected_action"]
                plan.append(action)
                
                # Simulate state update (simplified)
                state = self._simulate_action_outcome(action, state)
                
                # Check if goal achieved
                if self._check_goal_achievement(goal, state):
                    break
            
            logger.info(f"Generated adaptive plan with {len(plan)} steps for goal {goal_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error in adaptive planning: {e}")
            return []
    
    def _simulate_action_outcome(self, action: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate outcome of action (simplified)"""
        # In production, use learned state transition model
        new_state = state.copy()
        
        # Simple heuristic updates
        if "quality" in action.lower():
            new_state["quality_score"] = min(1.0, state.get("quality_score", 0.5) + 0.1)
        if "review" in action.lower():
            new_state["review_status"] = "reviewed"
        
        return new_state
    
    def _check_goal_achievement(self, goal: Goal, state: Dict[str, Any]) -> bool:
        """Check if goal is achieved in given state"""
        for criterion, threshold in goal.success_criteria.items():
            if criterion not in state:
                return False
            if state[criterion] < threshold:
                return False
        return True
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get statistics about decision-making performance"""
        try:
            if not self.decision_history:
                return {"total_decisions": 0}
            
            # Calculate statistics
            total_decisions = len(self.decision_history)
            
            recommendations = [d["recommendation"] for d in self.decision_history]
            recommendation_counts = {}
            for rec in set(recommendations):
                recommendation_counts[rec] = recommendations.count(rec)
            
            # Average scores
            avg_score = sum(d["overall_score"] for d in self.decision_history) / total_decisions
            
            # Risk statistics
            avg_risk = sum(d["risk_assessment"]["overall_risk"] 
                          for d in self.decision_history) / total_decisions
            
            return {
                "total_decisions": total_decisions,
                "average_confidence": avg_score,
                "average_risk": avg_risk,
                "recommendation_distribution": recommendation_counts,
                "active_goals": len([g for g in self.goals.values() if g.status == "active"]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating decision statistics: {e}")
            return {"error": str(e)}
