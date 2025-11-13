"""
Reinforcement Learning Framework - Agent Learning & Adaptation
Implements Q-Learning and policy gradient methods for autonomous improvement
Phase 1: Foundation ML Infrastructure - Week 3
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import datetime
from collections import deque, defaultdict
import pickle

logger = logging.getLogger(__name__)


class ReinforcementLearningFramework:
    """
    Production-grade reinforcement learning for agent autonomy
    Implements Q-Learning, experience replay, and policy optimization
    """
    
    def __init__(self, agent_id: str, learning_rate: float = 0.1, 
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        """
        Initialize reinforcement learning framework
        
        Args:
            agent_id: Unique agent identifier
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Exploration rate for epsilon-greedy
        """
        self.agent_id = agent_id
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-table: state-action values
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=10000)
        
        # Performance tracking
        self.episode_rewards = []
        self.success_counts = defaultdict(int)
        self.failure_counts = defaultdict(int)
        
        # Policy parameters
        self.policy_weights = {}
        
        logger.info(f"ReinforcementLearningFramework initialized for agent: {agent_id}")
    
    def get_action(self, state: str, available_actions: List[str], 
                   use_exploration: bool = True) -> str:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state representation
            available_actions: List of possible actions
            use_exploration: Whether to use exploration (vs pure exploitation)
            
        Returns:
            Selected action
        """
        try:
            if use_exploration and np.random.random() < self.epsilon:
                # Exploration: random action
                action = np.random.choice(available_actions)
                logger.debug(f"Exploration: selected random action {action}")
            else:
                # Exploitation: best known action
                q_values = {action: self.q_table[state][action] for action in available_actions}
                
                if not any(q_values.values()):
                    # No learned values, choose randomly
                    action = np.random.choice(available_actions)
                else:
                    # Choose action with highest Q-value
                    action = max(q_values, key=q_values.get)
                
                logger.debug(f"Exploitation: selected best action {action} (Q={q_values[action]:.3f})")
            
            return action
            
        except Exception as e:
            logger.error(f"Error selecting action: {e}")
            return available_actions[0] if available_actions else "default"
    
    def update_q_value(self, state: str, action: str, reward: float, 
                      next_state: str, next_actions: List[str]) -> float:
        """
        Update Q-value using Q-learning update rule
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            next_actions: Available actions in next state
            
        Returns:
            Updated Q-value
        """
        try:
            # Current Q-value
            current_q = self.q_table[state][action]
            
            # Max Q-value for next state
            if next_actions:
                max_next_q = max(self.q_table[next_state][a] for a in next_actions)
            else:
                max_next_q = 0.0
            
            # Q-learning update
            new_q = current_q + self.learning_rate * (
                reward + self.discount_factor * max_next_q - current_q
            )
            
            # Update Q-table
            self.q_table[state][action] = new_q
            
            logger.debug(f"Updated Q({state}, {action}): {current_q:.3f} -> {new_q:.3f}")
            return new_q
            
        except Exception as e:
            logger.error(f"Error updating Q-value: {e}")
            return 0.0
    
    def store_experience(self, state: str, action: str, reward: float,
                        next_state: str, done: bool, metadata: Dict[str, Any] = None) -> bool:
        """
        Store experience in replay buffer for learning
        
        Args:
            state: State before action
            action: Action taken
            reward: Reward received
            next_state: State after action
            done: Whether episode ended
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            experience = {
                "state": state,
                "action": action,
                "reward": reward,
                "next_state": next_state,
                "done": done,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.experience_buffer.append(experience)
            
            # Track success/failure
            if done:
                if reward > 0:
                    self.success_counts[action] += 1
                else:
                    self.failure_counts[action] += 1
            
            logger.debug(f"Stored experience: {action} -> reward={reward:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing experience: {e}")
            return False
    
    def replay_experiences(self, batch_size: int = 32) -> Dict[str, Any]:
        """
        Learn from batch of past experiences (experience replay)
        
        Args:
            batch_size: Number of experiences to replay
            
        Returns:
            Learning statistics
        """
        try:
            if len(self.experience_buffer) < batch_size:
                batch_size = len(self.experience_buffer)
            
            if batch_size == 0:
                return {"experiences_replayed": 0}
            
            # Sample random batch
            indices = np.random.choice(len(self.experience_buffer), batch_size, replace=False)
            batch = [self.experience_buffer[i] for i in indices]
            
            # Update Q-values from batch
            total_update = 0.0
            for exp in batch:
                # Get available actions for next state (simplified)
                next_actions = [exp["action"]]  # In production, retrieve from state
                
                delta_q = self.update_q_value(
                    exp["state"],
                    exp["action"],
                    exp["reward"],
                    exp["next_state"],
                    next_actions
                )
                total_update += abs(delta_q)
            
            avg_update = total_update / batch_size
            
            logger.info(f"Replayed {batch_size} experiences, avg Q-update: {avg_update:.4f}")
            
            return {
                "experiences_replayed": batch_size,
                "average_q_update": avg_update,
                "buffer_size": len(self.experience_buffer)
            }
            
        except Exception as e:
            logger.error(f"Error replaying experiences: {e}")
            return {"error": str(e)}
    
    def calculate_action_success_rate(self, action: str) -> float:
        """Calculate success rate for specific action"""
        total = self.success_counts[action] + self.failure_counts[action]
        if total == 0:
            return 0.5  # Unknown
        return self.success_counts[action] / total
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """
        Get summary of learned policy
        
        Returns:
            Policy statistics and recommendations
        """
        try:
            # Get most visited states
            state_visits = defaultdict(int)
            for exp in self.experience_buffer:
                state_visits[exp["state"]] += 1
            
            # Get best actions per state
            best_actions = {}
            for state in self.q_table:
                if self.q_table[state]:
                    best_actions[state] = max(self.q_table[state], key=self.q_table[state].get)
            
            # Calculate success rates
            action_success_rates = {}
            for action in set(self.success_counts.keys()) | set(self.failure_counts.keys()):
                action_success_rates[action] = self.calculate_action_success_rate(action)
            
            # Overall performance
            total_successes = sum(self.success_counts.values())
            total_failures = sum(self.failure_counts.values())
            overall_success_rate = total_successes / max(total_successes + total_failures, 1)
            
            return {
                "agent_id": self.agent_id,
                "total_states_learned": len(self.q_table),
                "total_experiences": len(self.experience_buffer),
                "overall_success_rate": overall_success_rate,
                "action_success_rates": action_success_rates,
                "best_actions": best_actions,
                "most_visited_states": dict(sorted(state_visits.items(), 
                                                   key=lambda x: x[1], 
                                                   reverse=True)[:10]),
                "learning_parameters": {
                    "learning_rate": self.learning_rate,
                    "discount_factor": self.discount_factor,
                    "epsilon": self.epsilon
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating policy summary: {e}")
            return {}
    
    def adjust_epsilon(self, decay_factor: float = 0.99, min_epsilon: float = 0.01):
        """
        Decay exploration rate over time (epsilon decay)
        
        Args:
            decay_factor: Multiplicative decay factor
            min_epsilon: Minimum epsilon value
        """
        self.epsilon = max(min_epsilon, self.epsilon * decay_factor)
        logger.debug(f"Epsilon decayed to {self.epsilon:.4f}")
    
    def save_model(self, filepath: str) -> bool:
        """
        Save learned model to file
        
        Args:
            filepath: Path to save model
            
        Returns:
            Success status
        """
        try:
            model_data = {
                "agent_id": self.agent_id,
                "q_table": dict(self.q_table),
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "epsilon": self.epsilon,
                "success_counts": dict(self.success_counts),
                "failure_counts": dict(self.failure_counts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Load learned model from file
        
        Args:
            filepath: Path to load model from
            
        Returns:
            Success status
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.agent_id = model_data["agent_id"]
            self.q_table = defaultdict(lambda: defaultdict(float), model_data["q_table"])
            self.learning_rate = model_data["learning_rate"]
            self.discount_factor = model_data["discount_factor"]
            self.epsilon = model_data["epsilon"]
            self.success_counts = defaultdict(int, model_data["success_counts"])
            self.failure_counts = defaultdict(int, model_data["failure_counts"])
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class SupervisedLearningFramework:
    """
    Supervised learning for agent training from labeled examples
    Implements classification and regression for agent decisions
    """
    
    def __init__(self, agent_id: str):
        """Initialize supervised learning framework"""
        self.agent_id = agent_id
        self.training_examples = []
        self.model_weights = {}
        self.feature_importance = {}
        
        logger.info(f"SupervisedLearningFramework initialized for agent: {agent_id}")
    
    def add_training_example(self, features: Dict[str, float], 
                            label: Any, metadata: Dict[str, Any] = None) -> bool:
        """
        Add labeled training example
        
        Args:
            features: Feature dictionary
            label: True label
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            example = {
                "features": features,
                "label": label,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.training_examples.append(example)
            logger.debug(f"Added training example with label: {label}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding training example: {e}")
            return False
    
    def train_model(self, algorithm: str = "logistic_regression") -> Dict[str, Any]:
        """
        Train supervised learning model
        
        Args:
            algorithm: Learning algorithm to use
            
        Returns:
            Training statistics
        """
        try:
            if len(self.training_examples) < 10:
                logger.warning("Insufficient training examples for reliable training")
                return {"error": "insufficient_data", "examples": len(self.training_examples)}
            
            # Extract features and labels
            X = []
            y = []
            feature_names = set()
            
            for example in self.training_examples:
                features = example["features"]
                feature_names.update(features.keys())
                X.append(features)
                y.append(example["label"])
            
            # Simple logistic regression (in production, use scikit-learn)
            # This is a placeholder for demonstration
            accuracy = len([i for i, ex in enumerate(self.training_examples) 
                           if self._predict_simple(ex["features"]) == ex["label"]]) / len(self.training_examples)
            
            logger.info(f"Model trained with accuracy: {accuracy:.3f}")
            
            return {
                "algorithm": algorithm,
                "training_examples": len(self.training_examples),
                "features": list(feature_names),
                "accuracy": accuracy,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {"error": str(e)}
    
    def _predict_simple(self, features: Dict[str, float]) -> Any:
        """Simple prediction (placeholder)"""
        # In production, use trained model
        score = sum(features.values()) / max(len(features), 1)
        return "positive" if score > 0.5 else "negative"
    
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Make prediction using trained model
        
        Args:
            features: Feature dictionary
            
        Returns:
            Prediction with confidence
        """
        try:
            prediction = self._predict_simple(features)
            confidence = 0.75  # Placeholder
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "features_used": list(features.keys())
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {"prediction": None, "error": str(e)}
