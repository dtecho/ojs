"""
Vector Memory System - Persistent Memory with Semantic Search
Implements vector database for agent knowledge storage and retrieval
Phase 1: Foundation ML Infrastructure - Week 1
"""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime
import json
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorMemorySystem:
    """
    Persistent vector-based memory system for agents
    Enables semantic search and knowledge graph construction
    """
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        """Initialize vector memory system with persistent storage"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Initialize embedding model for semantic search
        self.embedding_model = SentenceTransformer('sentence-transformers/allenai-specter')
        
        # Create collections for different memory types
        self.research_memory = self._get_or_create_collection("research_papers")
        self.episodic_memory = self._get_or_create_collection("agent_episodes")
        self.knowledge_graph = self._get_or_create_collection("knowledge_graph")
        self.experience_memory = self._get_or_create_collection("agent_experiences")
        
        logger.info(f"VectorMemorySystem initialized with persist_directory: {persist_directory}")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(name)
    
    def store_research_paper(self, paper_id: str, title: str, abstract: str, 
                            metadata: Dict[str, Any]) -> bool:
        """
        Store research paper in vector database for semantic search
        
        Args:
            paper_id: Unique identifier for the paper
            title: Paper title
            abstract: Paper abstract
            metadata: Additional metadata (authors, keywords, etc.)
        """
        try:
            # Combine title and abstract for embedding
            full_text = f"{title}\n\n{abstract}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(full_text).tolist()
            
            # Store in collection
            self.research_memory.add(
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[{
                    "paper_id": paper_id,
                    "title": title,
                    "timestamp": datetime.utcnow().isoformat(),
                    **metadata
                }],
                ids=[paper_id]
            )
            
            logger.info(f"Stored research paper: {paper_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing research paper {paper_id}: {e}")
            return False
    
    def semantic_search_papers(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search across research papers
        
        Args:
            query: Search query (natural language)
            n_results: Number of results to return
        
        Returns:
            List of matching papers with relevance scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in vector database
            results = self.research_memory.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            papers = []
            if results and results['ids']:
                for i in range(len(results['ids'][0])):
                    papers.append({
                        'paper_id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Semantic search returned {len(papers)} results for query: {query[:50]}...")
            return papers
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def store_agent_experience(self, agent_id: str, action: str, context: Dict[str, Any],
                               outcome: Dict[str, Any], success: bool) -> bool:
        """
        Store agent experience for learning and improvement
        
        Args:
            agent_id: Agent identifier
            action: Action taken
            context: Context in which action was taken
            outcome: Result of the action
            success: Whether action was successful
        """
        try:
            experience_id = f"{agent_id}_{datetime.utcnow().timestamp()}"
            
            # Create experience description
            description = f"Agent {agent_id} performed {action} with outcome: {outcome.get('summary', 'N/A')}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(description).tolist()
            
            # Store experience
            self.experience_memory.add(
                embeddings=[embedding],
                documents=[description],
                metadatas=[{
                    "experience_id": experience_id,
                    "agent_id": agent_id,
                    "action": action,
                    "context": json.dumps(context),
                    "outcome": json.dumps(outcome),
                    "success": success,
                    "timestamp": datetime.utcnow().isoformat()
                }],
                ids=[experience_id]
            )
            
            logger.info(f"Stored experience for agent {agent_id}: {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing agent experience: {e}")
            return False
    
    def retrieve_similar_experiences(self, agent_id: str, current_context: str,
                                     n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar past experiences for learning
        
        Args:
            agent_id: Agent requesting experiences
            current_context: Current situation description
            n_results: Number of similar experiences to retrieve
        """
        try:
            # Generate context embedding
            context_embedding = self.embedding_model.encode(current_context).tolist()
            
            # Search for similar experiences
            results = self.experience_memory.query(
                query_embeddings=[context_embedding],
                n_results=n_results,
                where={"agent_id": agent_id}
            )
            
            # Format results
            experiences = []
            if results and results['ids']:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    experiences.append({
                        'experience_id': metadata['experience_id'],
                        'action': metadata['action'],
                        'context': json.loads(metadata['context']),
                        'outcome': json.loads(metadata['outcome']),
                        'success': metadata['success'],
                        'timestamp': metadata['timestamp'],
                        'similarity': 1 - results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Retrieved {len(experiences)} similar experiences for {agent_id}")
            return experiences
            
        except Exception as e:
            logger.error(f"Error retrieving similar experiences: {e}")
            return []
    
    def store_episodic_memory(self, episode_id: str, agent_id: str, 
                             events: List[Dict[str, Any]], outcome: Dict[str, Any]) -> bool:
        """
        Store complete episode (sequence of events) for learning
        
        Args:
            episode_id: Unique episode identifier
            agent_id: Agent involved
            events: Sequence of events in episode
            outcome: Final outcome of episode
        """
        try:
            # Create episode summary
            summary = f"Agent {agent_id} episode with {len(events)} events, outcome: {outcome.get('status', 'unknown')}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(summary).tolist()
            
            # Store episode
            self.episodic_memory.add(
                embeddings=[embedding],
                documents=[summary],
                metadatas=[{
                    "episode_id": episode_id,
                    "agent_id": agent_id,
                    "events": json.dumps(events),
                    "outcome": json.dumps(outcome),
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_count": len(events)
                }],
                ids=[episode_id]
            )
            
            logger.info(f"Stored episodic memory: {episode_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing episodic memory: {e}")
            return False
    
    def build_knowledge_graph_node(self, node_id: str, node_type: str,
                                   properties: Dict[str, Any], 
                                   connections: List[str]) -> bool:
        """
        Add node to knowledge graph
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node (ingredient, paper, author, etc.)
            properties: Node properties
            connections: IDs of connected nodes
        """
        try:
            # Create node description
            description = f"{node_type}: {properties.get('name', node_id)}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(description).tolist()
            
            # Store node
            self.knowledge_graph.add(
                embeddings=[embedding],
                documents=[description],
                metadatas=[{
                    "node_id": node_id,
                    "node_type": node_type,
                    "properties": json.dumps(properties),
                    "connections": json.dumps(connections),
                    "timestamp": datetime.utcnow().isoformat()
                }],
                ids=[node_id]
            )
            
            logger.info(f"Added knowledge graph node: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding knowledge graph node: {e}")
            return False
    
    def query_knowledge_graph(self, query: str, node_type: Optional[str] = None,
                             n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Query knowledge graph semantically
        
        Args:
            query: Natural language query
            node_type: Filter by node type (optional)
            n_results: Number of results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build filter
            where_filter = {"node_type": node_type} if node_type else None
            
            # Search knowledge graph
            results = self.knowledge_graph.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            nodes = []
            if results and results['ids']:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    nodes.append({
                        'node_id': metadata['node_id'],
                        'node_type': metadata['node_type'],
                        'properties': json.loads(metadata['properties']),
                        'connections': json.loads(metadata['connections']),
                        'relevance': 1 - results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Knowledge graph query returned {len(nodes)} nodes")
            return nodes
            
        except Exception as e:
            logger.error(f"Error querying knowledge graph: {e}")
            return []
    
    def persist(self):
        """Persist all collections to disk"""
        try:
            self.client.persist()
            logger.info("Vector memory system persisted to disk")
            return True
        except Exception as e:
            logger.error(f"Error persisting vector memory: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            "research_papers": self.research_memory.count(),
            "agent_experiences": self.experience_memory.count(),
            "episodic_memories": self.episodic_memory.count(),
            "knowledge_graph_nodes": self.knowledge_graph.count(),
            "persist_directory": self.persist_directory,
            "embedding_model": "sentence-transformers/allenai-specter"
        }
