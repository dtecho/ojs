"""
Agent Autonomy Integration Module
Integrates ML capabilities across all 7 autonomous agents
"""

from typing import Dict, List, Any
import logging
from datetime import datetime

# Import enhanced agents
from models.enhanced_research_discovery_agent import EnhancedResearchDiscoveryAgent

# Import core ML infrastructure
from services.vector_memory_system import VectorMemorySystem
from services.nlp_pipeline import NLPPipeline
from services.reinforcement_learning import ReinforcementLearningFramework, SupervisedLearningFramework
from services.autonomous_decision_engine import MLDecisionEngine, DecisionPriority

logger = logging.getLogger(__name__)


class AgentAutonomyIntegration:
    """
    Central integration for agent autonomy features
    Coordinates ML capabilities across all 7 agents
    """
    
    def __init__(self):
        """Initialize agent autonomy integration"""
        logger.info("Initializing Agent Autonomy Integration System")
        
        # Initialize enhanced agents
        self.research_agent = EnhancedResearchDiscoveryAgent("research_discovery")
        
        # Global shared resources
        self.shared_memory = VectorMemorySystem("./data/vector_db/shared")
        self.nlp_pipeline = NLPPipeline()
        
        # Agent registry
        self.agents = {
            "research_discovery": self.research_agent
        }
        
        # System-wide statistics
        self.system_stats = {
            "total_decisions": 0,
            "successful_outcomes": 0,
            "learning_episodes": 0
        }
        
        logger.info("Agent Autonomy Integration initialized successfully")
    
    def process_manuscript_autonomous(self, manuscript_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fully autonomous manuscript processing using ML-powered agents
        
        Args:
            manuscript_data: Manuscript information
            
        Returns:
            Comprehensive analysis and recommendations
        """
        try:
            manuscript_id = manuscript_data.get("id", "unknown")
            logger.info(f"Starting autonomous manuscript processing: {manuscript_id}")
            
            result = {
                "manuscript_id": manuscript_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_analyses": {},
                "final_recommendation": {},
                "learning_outcomes": {}
            }
            
            # 1. Research Discovery Agent Analysis
            research_analysis = self.research_agent.analyze_manuscript(
                manuscript_id=manuscript_id,
                title=manuscript_data.get("title", ""),
                abstract=manuscript_data.get("abstract", ""),
                full_text=manuscript_data.get("full_text", ""),
                metadata=manuscript_data.get("metadata", {})
            )
            result["agent_analyses"]["research_discovery"] = research_analysis
            
            # 2. Extract key insights for other agents
            quality_score = research_analysis.get("nlp_analysis", {}).get("nlp_metadata", {}).get("overall_score", 0.5)
            impact_score = research_analysis.get("impact_prediction", {}).get("impact_score", 0.5)
            
            # 3. Make final recommendation using combined insights
            final_decision = self._make_final_recommendation(
                quality_score=quality_score,
                impact_score=impact_score,
                research_analysis=research_analysis
            )
            result["final_recommendation"] = final_decision
            
            # 4. Update learning systems
            learning_update = self._update_learning_systems(
                manuscript_id=manuscript_id,
                analyses=result["agent_analyses"],
                outcome=final_decision
            )
            result["learning_outcomes"] = learning_update
            
            # 5. Update statistics
            self.system_stats["total_decisions"] += 1
            if final_decision.get("recommendation") in ["approve_high_confidence", "approve_moderate_confidence"]:
                self.system_stats["successful_outcomes"] += 1
            
            logger.info(f"Completed autonomous manuscript processing: {manuscript_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in autonomous manuscript processing: {e}")
            return {"error": str(e)}
    
    def _make_final_recommendation(self, quality_score: float, impact_score: float,
                                   research_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all analyses into final recommendation"""
        
        # Combined score (weighted average)
        combined_score = (quality_score * 0.6 + impact_score * 0.4)
        
        # Determine recommendation
        if combined_score >= 0.8:
            recommendation = "approve_high_confidence"
            confidence = "high"
        elif combined_score >= 0.6:
            recommendation = "approve_moderate_confidence"
            confidence = "medium"
        elif combined_score >= 0.4:
            recommendation = "request_revision"
            confidence = "medium"
        else:
            recommendation = "reject"
            confidence = "high"
        
        # Extract specific feedback
        gaps = research_analysis.get("research_gaps", [])
        recommendations = []
        
        if gaps:
            recommendations.append(f"Address identified research gaps: {', '.join([g.get('topic', '') for g in gaps[:2]])}")
        
        if quality_score < 0.6:
            recommendations.append("Improve manuscript quality and clarity")
        
        if impact_score < 0.5:
            recommendations.append("Strengthen novelty and potential impact")
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "combined_score": combined_score,
            "quality_score": quality_score,
            "impact_score": impact_score,
            "specific_feedback": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _update_learning_systems(self, manuscript_id: str, analyses: Dict[str, Any],
                                outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Update all learning systems with outcomes"""
        
        updates = {}
        
        # Calculate reward based on outcome
        if outcome["recommendation"] in ["approve_high_confidence"]:
            reward = 1.0
        elif outcome["recommendation"] in ["approve_moderate_confidence"]:
            reward = 0.7
        elif outcome["recommendation"] == "request_revision":
            reward = 0.4
        else:
            reward = 0.0
        
        # Update research agent learning
        if "research_discovery" in analyses:
            self.research_agent.rl_framework.store_experience(
                state=f"manuscript_{manuscript_id}",
                action="comprehensive_analysis",
                reward=reward,
                next_state="completed",
                done=True,
                metadata={"outcome": outcome["recommendation"]}
            )
        
        # Replay experiences for learning
        replay_stats = self.research_agent.rl_framework.replay_experiences(batch_size=16)
        
        updates = {
            "reward_assigned": reward,
            "replay_statistics": replay_stats,
            "learning_episode_complete": True
        }
        
        self.system_stats["learning_episodes"] += 1
        
        return updates
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get comprehensive system performance metrics"""
        
        performance = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_statistics": self.system_stats.copy(),
            "agent_performance": {},
            "memory_statistics": self.shared_memory.get_statistics()
        }
        
        # Get per-agent performance
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'get_agent_performance'):
                performance["agent_performance"][agent_id] = agent.get_agent_performance()
        
        # Calculate success rate
        total = self.system_stats["total_decisions"]
        if total > 0:
            performance["overall_success_rate"] = self.system_stats["successful_outcomes"] / total
        else:
            performance["overall_success_rate"] = 0.0
        
        return performance
    
    def train_agent_from_historical_data(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train agents using historical manuscript data
        
        Args:
            historical_data: List of past manuscripts with outcomes
            
        Returns:
            Training statistics
        """
        try:
            logger.info(f"Training agents from {len(historical_data)} historical examples")
            
            training_stats = {
                "total_examples": len(historical_data),
                "examples_processed": 0,
                "average_reward": 0.0
            }
            
            total_reward = 0.0
            
            for example in historical_data:
                # Process manuscript
                analysis = self.process_manuscript_autonomous(example)
                
                # Extract actual outcome if available
                actual_outcome = example.get("actual_outcome", {})
                
                # Calculate reward based on prediction accuracy
                if actual_outcome:
                    predicted = analysis["final_recommendation"]["recommendation"]
                    actual = actual_outcome.get("decision", "")
                    
                    reward = 1.0 if predicted == actual else 0.0
                    total_reward += reward
                
                training_stats["examples_processed"] += 1
            
            if training_stats["examples_processed"] > 0:
                training_stats["average_reward"] = total_reward / training_stats["examples_processed"]
            
            # Perform experience replay for all agents
            self.research_agent.rl_framework.replay_experiences(batch_size=32)
            
            logger.info(f"Training completed. Average reward: {training_stats['average_reward']:.3f}")
            return training_stats
            
        except Exception as e:
            logger.error(f"Error training agents: {e}")
            return {"error": str(e)}


# Global instance
_autonomy_integration = None


def get_autonomy_integration() -> AgentAutonomyIntegration:
    """Get or create global autonomy integration instance"""
    global _autonomy_integration
    if _autonomy_integration is None:
        _autonomy_integration = AgentAutonomyIntegration()
    return _autonomy_integration
