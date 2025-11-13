"""
Agent Autonomy API - RESTful endpoints for ML-powered agent capabilities
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from agent_autonomy_integration import get_autonomy_integration

logger = logging.getLogger(__name__)

# Create blueprint
autonomy_api_bp = Blueprint('autonomy_api', __name__, url_prefix='/api/v1/autonomy')


@autonomy_api_bp.route('/status', methods=['GET'])
def get_autonomy_status():
    """Get autonomy system status and performance"""
    try:
        integration = get_autonomy_integration()
        performance = integration.get_system_performance()
        
        return jsonify({
            "success": True,
            "status": "operational",
            "performance": performance
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting autonomy status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/manuscript/analyze', methods=['POST'])
def analyze_manuscript_autonomous():
    """
    Fully autonomous manuscript analysis using ML agents
    
    Request body:
    {
        "id": "manuscript_123",
        "title": "Research Title",
        "abstract": "Abstract text...",
        "full_text": "Complete manuscript...",
        "metadata": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'id' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: id"
            }), 400
        
        integration = get_autonomy_integration()
        result = integration.process_manuscript_autonomous(data)
        
        return jsonify({
            "success": True,
            "result": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing manuscript: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/research/plan', methods=['POST'])
def plan_research_strategy():
    """
    Generate autonomous research strategy
    
    Request body:
    {
        "goal": "Research objective description",
        "constraints": {
            "time_weeks": 12,
            "budget": 50000
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'goal' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: goal"
            }), 400
        
        integration = get_autonomy_integration()
        research_agent = integration.research_agent
        
        plan = research_agent.plan_research_strategy(
            research_goal=data['goal'],
            constraints=data.get('constraints', {})
        )
        
        return jsonify({
            "success": True,
            "plan": plan
        }), 200
        
    except Exception as e:
        logger.error(f"Error planning research strategy: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/learning/train', methods=['POST'])
def train_from_historical_data():
    """
    Train agents using historical data
    
    Request body:
    {
        "historical_data": [
            {
                "id": "manuscript_1",
                "title": "...",
                "actual_outcome": {"decision": "approve"}
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'historical_data' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: historical_data"
            }), 400
        
        integration = get_autonomy_integration()
        training_stats = integration.train_agent_from_historical_data(
            data['historical_data']
        )
        
        return jsonify({
            "success": True,
            "training_statistics": training_stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error training agents: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/memory/search', methods=['POST'])
def search_vector_memory():
    """
    Semantic search across agent memory
    
    Request body:
    {
        "query": "Search query text",
        "n_results": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: query"
            }), 400
        
        integration = get_autonomy_integration()
        results = integration.shared_memory.semantic_search_papers(
            query=data['query'],
            n_results=data.get('n_results', 10)
        )
        
        return jsonify({
            "success": True,
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/agent/<agent_id>/performance', methods=['GET'])
def get_agent_performance(agent_id: str):
    """Get performance metrics for specific agent"""
    try:
        integration = get_autonomy_integration()
        
        if agent_id not in integration.agents:
            return jsonify({
                "success": False,
                "error": f"Agent not found: {agent_id}"
            }), 404
        
        agent = integration.agents[agent_id]
        
        if hasattr(agent, 'get_agent_performance'):
            performance = agent.get_agent_performance()
        else:
            performance = {"error": "Agent does not support performance metrics"}
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "performance": performance
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/nlp/analyze', methods=['POST'])
def nlp_analyze_text():
    """
    NLP analysis of arbitrary text
    
    Request body:
    {
        "text": "Text to analyze"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: text"
            }), 400
        
        integration = get_autonomy_integration()
        analysis = integration.nlp_pipeline.extract_manuscript_metadata(data['text'])
        
        return jsonify({
            "success": True,
            "analysis": analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomy_api_bp.route('/decision/evaluate', methods=['POST'])
def evaluate_decision():
    """
    Evaluate potential action using decision engine
    
    Request body:
    {
        "agent_id": "research_discovery",
        "action": "approve_manuscript",
        "context": {
            "quality_score": 0.85,
            "impact_score": 0.75
        },
        "goals": ["maximize_quality"]
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['agent_id', 'action', 'context']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        integration = get_autonomy_integration()
        agent_id = data['agent_id']
        
        if agent_id not in integration.agents:
            return jsonify({
                "success": False,
                "error": f"Agent not found: {agent_id}"
            }), 404
        
        agent = integration.agents[agent_id]
        
        if hasattr(agent, 'decision_engine'):
            evaluation = agent.decision_engine.evaluate_action(
                action=data['action'],
                context=data['context'],
                goals=data.get('goals')
            )
        else:
            evaluation = {"error": "Agent does not have decision engine"}
        
        return jsonify({
            "success": True,
            "evaluation": evaluation
        }), 200
        
    except Exception as e:
        logger.error(f"Error evaluating decision: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Initialize autonomy integration on module load
try:
    _integration = get_autonomy_integration()
    logger.info("Agent Autonomy API initialized successfully")
except Exception as e:
    logger.error(f"Error initializing autonomy integration: {e}")
