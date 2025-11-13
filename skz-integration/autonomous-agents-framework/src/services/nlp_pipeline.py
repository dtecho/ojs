"""
NLP Pipeline - Natural Language Processing for Academic Content
Implements text processing, entity recognition, and classification
Phase 1: Foundation ML Infrastructure - Week 2
"""

from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NLPPipeline:
    """
    Production-grade NLP pipeline for academic manuscript processing
    Uses BERT and transformer models for text understanding
    """
    
    def __init__(self, device: str = "cpu"):
        """Initialize NLP pipeline with production models"""
        self.device = device
        logger.info(f"Initializing NLP Pipeline on device: {device}")
        
        # Initialize models
        try:
            # Summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if device == "cuda" and torch.cuda.is_available() else -1
            )
            
            # Sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if device == "cuda" and torch.cuda.is_available() else -1
            )
            
            # Named Entity Recognition
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple",
                device=0 if device == "cuda" and torch.cuda.is_available() else -1
            )
            
            # Text classification
            self.classifier = pipeline(
                "text-classification",
                model="allenai/scibert_scivocab_uncased",
                device=0 if device == "cuda" and torch.cuda.is_available() else -1
            )
            
            # Zero-shot classification for custom categories
            self.zero_shot = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if device == "cuda" and torch.cuda.is_available() else -1
            )
            
            logger.info("NLP Pipeline models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            raise
    
    def extract_manuscript_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract key metadata from manuscript text
        
        Args:
            text: Manuscript text
            
        Returns:
            Extracted metadata including entities, sentiment, topics
        """
        try:
            # Extract entities
            entities = self.extract_entities(text)
            
            # Analyze sentiment/tone
            sentiment = self.analyze_sentiment(text[:512])  # Limit for model
            
            # Classify topic
            topics = self.classify_topic(text[:512])
            
            # Extract key phrases
            key_phrases = self.extract_key_phrases(text)
            
            # Generate summary
            summary = self.generate_summary(text)
            
            return {
                "entities": entities,
                "sentiment": sentiment,
                "topics": topics,
                "key_phrases": key_phrases,
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting manuscript metadata: {e}")
            return {}
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and their occurrences
        """
        try:
            # Run NER pipeline
            entities = self.ner_pipeline(text[:512])  # Limit for model
            
            # Group entities by type
            grouped = {}
            for entity in entities:
                entity_type = entity['entity_group']
                entity_text = entity['word']
                
                if entity_type not in grouped:
                    grouped[entity_type] = []
                
                if entity_text not in grouped[entity_type]:
                    grouped[entity_type].append(entity_text)
            
            # Extract domain-specific entities (ingredients, compounds)
            custom_entities = self._extract_custom_entities(text)
            grouped.update(custom_entities)
            
            logger.info(f"Extracted {len(entities)} entities from text")
            return grouped
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    def _extract_custom_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract domain-specific entities (ingredients, INCI names, compounds)"""
        entities = {
            "ingredients": [],
            "compounds": [],
            "methodologies": []
        }
        
        # Pattern for INCI names (capitalized chemical names)
        inci_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+[A-Z][a-z]+\b'
        entities["ingredients"] = list(set(re.findall(inci_pattern, text)))
        
        # Pattern for chemical compounds
        compound_pattern = r'\b[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*\b'
        entities["compounds"] = list(set(re.findall(compound_pattern, text)))[:10]
        
        # Extract methodology keywords
        methodology_keywords = ['double-blind', 'randomized', 'controlled', 'clinical trial',
                               'in vitro', 'in vivo', 'placebo', 'statistical analysis']
        entities["methodologies"] = [kw for kw in methodology_keywords if kw.lower() in text.lower()]
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment and confidence in text
        
        Args:
            text: Input text
            
        Returns:
            Sentiment analysis results
        """
        try:
            result = self.sentiment_analyzer(text[:512])[0]
            
            return {
                "label": result['label'],
                "score": float(result['score']),
                "confidence": "high" if result['score'] > 0.9 else "medium" if result['score'] > 0.7 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"label": "NEUTRAL", "score": 0.5, "confidence": "low"}
    
    def classify_topic(self, text: str, candidate_labels: Optional[List[str]] = None) -> List[Dict[str, float]]:
        """
        Classify text into topics using zero-shot classification
        
        Args:
            text: Input text
            candidate_labels: Optional list of topics to classify into
            
        Returns:
            List of topics with confidence scores
        """
        try:
            if candidate_labels is None:
                # Default cosmetic science topics
                candidate_labels = [
                    "skincare formulation",
                    "cosmetic safety",
                    "ingredient efficacy",
                    "regulatory compliance",
                    "clinical trials",
                    "product development",
                    "toxicology",
                    "dermatology"
                ]
            
            result = self.zero_shot(text[:512], candidate_labels)
            
            # Format results
            topics = []
            for label, score in zip(result['labels'], result['scores']):
                topics.append({
                    "topic": label,
                    "confidence": float(score)
                })
            
            logger.info(f"Classified text into {len(topics)} topics")
            return topics
            
        except Exception as e:
            logger.error(f"Error classifying topic: {e}")
            return []
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """
        Extract key phrases from text
        
        Args:
            text: Input text
            max_phrases: Maximum number of phrases to extract
            
        Returns:
            List of key phrases
        """
        # Simple keyword extraction using frequency and capitalization
        # In production, consider using KeyBERT or YAKE
        
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        word_freq = {}
        
        for word in words:
            if len(word.split()) >= 2:  # Multi-word phrases
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_phrases = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [phrase for phrase, _ in sorted_phrases[:max_phrases]]
    
    def generate_summary(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate summary of text
        
        Args:
            text: Input text
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            Generated summary
        """
        try:
            # Summarization works best with 512-1024 tokens
            text_chunk = text[:1024]
            
            if len(text_chunk.split()) < min_length:
                return text_chunk
            
            summary = self.summarizer(
                text_chunk,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]['summary_text']
            
            logger.info(f"Generated summary of {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return text[:500]  # Fallback to truncation
    
    def assess_quality_indicators(self, text: str) -> Dict[str, Any]:
        """
        Assess quality indicators in academic text
        
        Args:
            text: Manuscript text
            
        Returns:
            Quality indicators (methodology clarity, data support, etc.)
        """
        indicators = {
            "has_methodology": False,
            "has_data": False,
            "has_references": False,
            "clarity_score": 0.0,
            "technical_depth": 0.0
        }
        
        # Check for methodology section
        methodology_keywords = ['method', 'methodology', 'procedure', 'protocol', 'experimental']
        indicators["has_methodology"] = any(kw in text.lower() for kw in methodology_keywords)
        
        # Check for data presentation
        data_keywords = ['table', 'figure', 'results', 'data', 'n=', 'p<', 'p-value']
        indicators["has_data"] = any(kw in text.lower() for kw in data_keywords)
        
        # Check for references
        reference_patterns = [r'\[\d+\]', r'\(\d{4}\)', r'et al\.']
        indicators["has_references"] = any(re.search(pattern, text) for pattern in reference_patterns)
        
        # Assess clarity (based on sentence complexity)
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        indicators["clarity_score"] = min(1.0, 20.0 / max(avg_sentence_length, 1))
        
        # Assess technical depth (based on technical terms)
        technical_terms = len(re.findall(r'\b[A-Z][a-z]*[A-Z][a-z]*\b', text))
        indicators["technical_depth"] = min(1.0, technical_terms / 100.0)
        
        return indicators
    
    def classify_manuscript_quality(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive quality classification for manuscripts
        
        Args:
            text: Manuscript text
            metadata: Manuscript metadata
            
        Returns:
            Quality assessment with scores and recommendations
        """
        try:
            # Extract all NLP features
            nlp_metadata = self.extract_manuscript_metadata(text)
            
            # Assess quality indicators
            quality_indicators = self.assess_quality_indicators(text)
            
            # Calculate overall quality score
            scores = {
                "methodology_present": 0.2 if quality_indicators["has_methodology"] else 0.0,
                "data_supported": 0.2 if quality_indicators["has_data"] else 0.0,
                "well_referenced": 0.15 if quality_indicators["has_references"] else 0.0,
                "clarity": quality_indicators["clarity_score"] * 0.25,
                "technical_depth": quality_indicators["technical_depth"] * 0.2
            }
            
            overall_score = sum(scores.values())
            
            # Generate quality classification
            if overall_score >= 0.8:
                classification = "excellent"
            elif overall_score >= 0.6:
                classification = "good"
            elif overall_score >= 0.4:
                classification = "acceptable"
            else:
                classification = "needs_improvement"
            
            # Generate recommendations
            recommendations = []
            if not quality_indicators["has_methodology"]:
                recommendations.append("Add clear methodology section")
            if not quality_indicators["has_data"]:
                recommendations.append("Include data tables or figures")
            if not quality_indicators["has_references"]:
                recommendations.append("Add proper citations and references")
            if quality_indicators["clarity_score"] < 0.5:
                recommendations.append("Improve clarity and sentence structure")
            
            return {
                "overall_score": overall_score,
                "classification": classification,
                "component_scores": scores,
                "quality_indicators": quality_indicators,
                "nlp_metadata": nlp_metadata,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error classifying manuscript quality: {e}")
            return {
                "overall_score": 0.5,
                "classification": "unknown",
                "error": str(e)
            }
