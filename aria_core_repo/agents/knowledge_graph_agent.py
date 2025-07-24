"""
Knowledge Graph Agent for extracting concepts, relationships, and building knowledge graphs.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine, desc, JSON
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class KnowledgeGraph(Base):
    """Database model for storing knowledge graph concepts and relationships."""
    __tablename__ = "knowledge_graph"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    source_text = Column(Text, nullable=False)  # Original text
    concepts = Column(JSON, nullable=False)  # List of extracted concepts
    relationships = Column(JSON, nullable=False)  # List of relationships between concepts
    graph_data = Column(JSON, nullable=False)  # Complete graph structure for visualization
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class KnowledgeGraphAgent(BaseAgent):
    """
    Knowledge Graph Agent that extracts concepts, identifies relationships, 
    and builds comprehensive knowledge graphs from text input.
    """
    
    def __init__(self):
        super().__init__("KnowledgeGraphAgent", "سازنده گراف دانش و تحلیلگر روابط مفهومی")
        self.log("Initialized with PostgreSQL database integration for knowledge graph storage")
        
        # Create table if it doesn't exist
        self._create_knowledge_graph_table()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self._initialize_openai()
        
        # Relationship types in Persian
        self.relationship_types = {
            "علت_معلول": ["باعث", "منجر به", "دلیل", "نتیجه", "چون", "زیرا"],
            "شامل": ["شامل", "دربرگیرنده", "حاوی", "متشکل از"],
            "مرتبط": ["مرتبط", "وابسته", "متصل", "مربوط"],
            "مشابه": ["مثل", "شبیه", "همانند", "مانند"],
            "متضاد": ["مخالف", "برعکس", "متضاد", "در مقابل"],
            "زمانی": ["قبل از", "بعد از", "همزمان", "در طول"],
            "مکانی": ["در", "روی", "زیر", "کنار", "نزدیک"]
        }
        
        # Important concept indicators
        self.concept_indicators = [
            "مفهوم", "ایده", "نظریه", "روش", "سیستم", "فرآیند", "هدف", "مشکل",
            "راه‌حل", "نتیجه", "عامل", "جنبه", "ویژگی", "خصوصیت", "عنصر"
        ]
        
        self.log("Knowledge graph relationship types and concept indicators initialized")
    
    def _create_knowledge_graph_table(self):
        """Create knowledge_graph table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Knowledge graph table ready")
        except Exception as e:
            self.log(f"Error creating knowledge graph table: {e}", level="error")
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.log("OpenAI GPT integration ready for concept extraction")
            else:
                self.log("OpenAI API key not found, using fallback methods")
        except ImportError:
            self.log("OpenAI library not available, using fallback methods")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}, using fallback methods")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process knowledge graph requests and generate response.
        
        Args:
            message (str): The message containing knowledge graph analysis request
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the knowledge graph analysis result
        """
        try:
            self.log(f"Processing knowledge graph request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Detect operation type
            operation = self._detect_operation(message)
            
            if operation == "build":
                result = self._build_knowledge_graph(message, context)
                return {"response": result.get("response", "")}
            elif operation == "search":
                result = self._search_knowledge_graph(message, context)
                return {"response": result.get("response", "")}
            elif operation == "list":
                result = self._list_knowledge_graphs(message, context)
                return {"response": result.get("response", "")}
            else:
                # Default: build knowledge graph from the message
                result = self._build_knowledge_graph(message, context)
                return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing knowledge graph request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل گراف دانش:** {str(e)}"
            }
    
    def _detect_operation(self, message: str) -> str:
        """Detect the type of knowledge graph operation requested."""
        message_lower = message.lower()
        
        build_keywords = ["تحلیل", "analyze", "گراف", "graph", "ساخت", "build", "استخراج", "extract"]
        search_keywords = ["جستجو", "search", "یافتن", "find", "بازیابی", "retrieve"]
        list_keywords = ["لیست", "list", "نمایش", "show", "همه", "all"]
        
        if any(keyword in message_lower for keyword in search_keywords):
            return "search"
        elif any(keyword in message_lower for keyword in list_keywords):
            return "list"
        elif any(keyword in message_lower for keyword in build_keywords):
            return "build"
        else:
            return "build"
    
    def _build_knowledge_graph(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build knowledge graph from input text."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Extract concepts from the text
            concepts = self._extract_concepts(message)
            
            if not concepts:
                return {
                    "response": "📊 **تحلیل گراف دانش:** هیچ مفهوم قابل استخراجی یافت نشد.",
                    "success": True,
                    "timestamp": self._get_current_timestamp()
                }
            
            # Identify relationships between concepts
            relationships = self._identify_relationships(message, concepts)
            
            # Build graph structure
            graph_data = self._build_graph_structure(concepts, relationships)
            
            # Save to database
            graph_id = self._save_knowledge_graph(
                user_id, message, concepts, relationships, graph_data
            )
            
            response = self._format_knowledge_graph_response(
                concepts, relationships, graph_data, graph_id
            )
            
            return {
                "response": response,
                "success": True,
                "concepts_count": len(concepts),
                "relationships_count": len(relationships),
                "graph_id": graph_id,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error building knowledge graph: {e}", level="error")
            return {
                "response": f"❌ **خطا در ساخت گراف دانش:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extract important concepts from text using OpenAI or fallback methods."""
        if self.openai_client:
            return self._extract_concepts_with_openai(text)
        else:
            return self._extract_concepts_fallback(text)
    
    def _extract_concepts_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """Extract concepts using OpenAI GPT."""
        try:
            prompt = f"""
            از متن زیر مفاهیم مهم را استخراج کن و هر مفهوم را با اطلاعات زیر در قالب JSON برگردان:
            - concept: نام مفهوم
            - type: نوع مفهوم (شخص، مکان، شیء، ایده، فرآیند، هدف، مشکل، راه‌حل)
            - importance: اهمیت از 1 تا 5
            - description: توضیح کوتاه
            
            متن: {text}
            
            فقط JSON برگردان:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            concepts = result.get("concepts", [])
            
            self.log(f"OpenAI extracted {len(concepts)} concepts")
            return concepts
            
        except Exception as e:
            self.log(f"OpenAI concept extraction failed: {e}, using fallback")
            return self._extract_concepts_fallback(text)
    
    def _extract_concepts_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Extract concepts using rule-based approach."""
        concepts = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?؟]', text)
        
        # Extract noun phrases and important words
        concept_candidates = set()
        
        for sentence in sentences:
            # Find words that might be concepts
            words = re.findall(r'\b\w+\b', sentence)
            
            # Look for concept indicators
            for i, word in enumerate(words):
                if word in self.concept_indicators and i + 1 < len(words):
                    concept_candidates.add(words[i + 1])
                
                # Add significant nouns (longer than 3 characters)
                if len(word) > 3 and word not in ['است', 'باید', 'می‌کند', 'دارد']:
                    concept_candidates.add(word)
        
        # Convert candidates to concept objects
        for candidate in list(concept_candidates)[:10]:  # Limit to top 10
            concepts.append({
                "concept": candidate,
                "type": self._categorize_concept(candidate),
                "importance": self._calculate_importance(candidate, text),
                "description": f"مفهوم استخراج شده: {candidate}"
            })
        
        self.log(f"Fallback method extracted {len(concepts)} concepts")
        return concepts
    
    def _categorize_concept(self, concept: str) -> str:
        """Categorize a concept based on its characteristics."""
        concept_lower = concept.lower()
        
        if any(word in concept_lower for word in ['هدف', 'آرزو', 'برنامه']):
            return "هدف"
        elif any(word in concept_lower for word in ['مشکل', 'مسئله', 'چالش']):
            return "مشکل"
        elif any(word in concept_lower for word in ['راه‌حل', 'حل', 'پاسخ']):
            return "راه‌حل"
        elif any(word in concept_lower for word in ['فرآیند', 'روش', 'تکنیک']):
            return "فرآیند"
        elif any(word in concept_lower for word in ['شخص', 'فرد', 'کس']):
            return "شخص"
        elif any(word in concept_lower for word in ['مکان', 'جا', 'محل']):
            return "مکان"
        else:
            return "ایده"
    
    def _calculate_importance(self, concept: str, text: str) -> int:
        """Calculate importance score for a concept."""
        # Count frequency
        frequency = text.lower().count(concept.lower())
        
        # Length factor
        length_factor = min(len(concept) / 5, 2)
        
        # Calculate score
        score = min(int(frequency + length_factor), 5)
        return max(score, 1)
    
    def _identify_relationships(self, text: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify relationships between concepts."""
        relationships = []
        
        if len(concepts) < 2:
            return relationships
        
        # Check for relationships using pattern matching
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts[i+1:], i+1):
                relationship = self._find_relationship(text, concept1, concept2)
                if relationship:
                    relationships.append(relationship)
        
        self.log(f"Identified {len(relationships)} relationships")
        return relationships
    
    def _find_relationship(self, text: str, concept1: Dict[str, Any], concept2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find relationship between two concepts in text."""
        text_lower = text.lower()
        name1 = concept1["concept"].lower()
        name2 = concept2["concept"].lower()
        
        # Look for both concepts in same sentence
        sentences = re.split(r'[.!?؟]', text_lower)
        
        for sentence in sentences:
            if name1 in sentence and name2 in sentence:
                # Check for relationship indicators
                for rel_type, keywords in self.relationship_types.items():
                    for keyword in keywords:
                        if keyword in sentence:
                            return {
                                "source": concept1["concept"],
                                "target": concept2["concept"],
                                "relationship": rel_type,
                                "description": f"{concept1['concept']} {keyword} {concept2['concept']}",
                                "confidence": 0.8,
                                "context": sentence.strip()
                            }
                
                # Default relationship if concepts appear together
                return {
                    "source": concept1["concept"],
                    "target": concept2["concept"],
                    "relationship": "مرتبط",
                    "description": f"{concept1['concept']} مرتبط با {concept2['concept']}",
                    "confidence": 0.5,
                    "context": sentence.strip()
                }
        
        return None
    
    def _build_graph_structure(self, concepts: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build graph structure for visualization."""
        nodes = []
        edges = []
        
        # Add nodes
        for concept in concepts:
            nodes.append({
                "id": concept["concept"],
                "label": concept["concept"],
                "type": concept["type"],
                "importance": concept["importance"],
                "description": concept["description"]
            })
        
        # Add edges
        for rel in relationships:
            edges.append({
                "source": rel["source"],
                "target": rel["target"],
                "relationship": rel["relationship"],
                "label": rel["relationship"],
                "confidence": rel["confidence"],
                "description": rel["description"]
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_concepts": len(concepts),
                "total_relationships": len(relationships),
                "created_at": self._get_current_timestamp()
            }
        }
    
    def _save_knowledge_graph(self, user_id: Optional[int], source_text: str, 
                            concepts: List[Dict], relationships: List[Dict], 
                            graph_data: Dict[str, Any]) -> int:
        """Save knowledge graph to database."""
        try:
            db = SessionLocal()
            
            knowledge_graph = KnowledgeGraph(
                user_id=user_id,
                source_text=source_text,
                concepts=concepts,
                relationships=relationships,
                graph_data=graph_data
            )
            
            db.add(knowledge_graph)
            db.commit()
            db.refresh(knowledge_graph)
            
            graph_id = knowledge_graph.id
            self.log(f"Knowledge graph saved with ID: {graph_id}")
            
            db.close()
            return graph_id
            
        except Exception as e:
            self.log(f"Error saving knowledge graph: {e}", level="error")
            return 0
    
    def _search_knowledge_graph(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for concepts in existing knowledge graphs."""
        try:
            user_id = context.get("user_id") if context else None
            search_term = self._extract_search_term(query)
            
            db = SessionLocal()
            
            # Search in concepts and relationships
            query_db = db.query(KnowledgeGraph)
            if user_id:
                query_db = query_db.filter(KnowledgeGraph.user_id == user_id)
            
            graphs = query_db.order_by(desc(KnowledgeGraph.created_at)).limit(20).all()
            
            matching_graphs = []
            for graph in graphs:
                if self._graph_matches_search(graph, search_term):
                    matching_graphs.append({
                        "id": graph.id,
                        "source_text": graph.source_text[:100] + "..." if len(graph.source_text) > 100 else graph.source_text,
                        "concepts_count": len(graph.concepts),
                        "relationships_count": len(graph.relationships),
                        "created_at": graph.created_at.isoformat() if graph.created_at else None
                    })
            
            db.close()
            
            response = self._format_search_response(matching_graphs, search_term)
            
            return {
                "response": response,
                "success": True,
                "results_count": len(matching_graphs),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error searching knowledge graphs: {e}", level="error")
            return {
                "response": f"❌ **خطا در جستجوی گراف دانش:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_search_term(self, query: str) -> str:
        """Extract search term from query."""
        # Remove common words and extract meaningful terms
        stop_words = {'جستجو', 'یافتن', 'بازیابی', 'search', 'find', 'در', 'برای', 'از'}
        words = re.findall(r'\b\w+\b', query.lower())
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        return ' '.join(meaningful_words[:3])  # Top 3 meaningful words
    
    def _graph_matches_search(self, graph: KnowledgeGraph, search_term: str) -> bool:
        """Check if a graph matches the search term."""
        search_lower = search_term.lower()
        
        # Check source text
        if search_lower in graph.source_text.lower():
            return True
        
        # Check concepts
        for concept in graph.concepts:
            if search_lower in concept.get("concept", "").lower():
                return True
        
        # Check relationships
        for rel in graph.relationships:
            if (search_lower in rel.get("source", "").lower() or 
                search_lower in rel.get("target", "").lower()):
                return True
        
        return False
    
    def _list_knowledge_graphs(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List recent knowledge graphs."""
        try:
            user_id = context.get("user_id") if context else None
            limit = self._extract_limit(message)
            
            db = SessionLocal()
            
            query = db.query(KnowledgeGraph)
            if user_id:
                query = query.filter(KnowledgeGraph.user_id == user_id)
            
            graphs = query.order_by(desc(KnowledgeGraph.created_at)).limit(limit).all()
            
            graph_list = []
            for graph in graphs:
                graph_list.append({
                    "id": graph.id,
                    "source_text": graph.source_text[:80] + "..." if len(graph.source_text) > 80 else graph.source_text,
                    "concepts_count": len(graph.concepts),
                    "relationships_count": len(graph.relationships),
                    "created_at": graph.created_at.isoformat() if graph.created_at else None
                })
            
            db.close()
            
            response = self._format_list_response(graph_list)
            
            return {
                "response": response,
                "success": True,
                "graphs": graph_list,
                "count": len(graph_list),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error listing knowledge graphs: {e}", level="error")
            return {
                "response": f"❌ **خطا در نمایش گراف‌های دانش:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_limit(self, message: str) -> int:
        """Extract limit number from message."""
        import re
        numbers = re.findall(r'\d+', message)
        return int(numbers[0]) if numbers else 10
    
    def _format_knowledge_graph_response(self, concepts: List[Dict], relationships: List[Dict], 
                                       graph_data: Dict[str, Any], graph_id: int) -> str:
        """Format the knowledge graph analysis response."""
        response = f"🧠 **گراف دانش ساخته شد!** (🆔 #{graph_id})\n\n"
        
        # Concepts section
        response += f"**📊 مفاهیم استخراج شده** ({len(concepts)} مورد):\n"
        for i, concept in enumerate(concepts[:5], 1):
            importance_stars = "⭐" * concept.get("importance", 1)
            response += f"**{i}.** {self._get_concept_emoji(concept.get('type', ''))} `{concept.get('type', 'نامشخص')}` - {concept.get('concept', '')}\n"
            response += f"   {importance_stars} اهمیت: {concept.get('importance', 1)}/5\n\n"
        
        if len(concepts) > 5:
            response += f"... و {len(concepts) - 5} مفهوم دیگر\n\n"
        
        # Relationships section
        if relationships:
            response += f"**🔗 روابط شناسایی شده** ({len(relationships)} مورد):\n"
            for i, rel in enumerate(relationships[:5], 1):
                confidence_percent = int(rel.get("confidence", 0.5) * 100)
                response += f"**{i}.** {rel.get('source', '')} ➜ `{rel.get('relationship', '')}` ➜ {rel.get('target', '')}\n"
                response += f"   📊 اطمینان: {confidence_percent}% | 📝 {rel.get('description', '')}\n\n"
            
            if len(relationships) > 5:
                response += f"... و {len(relationships) - 5} رابطه دیگر\n\n"
        else:
            response += "**🔗 روابط:** هیچ رابطه‌ای شناسایی نشد.\n\n"
        
        # Graph statistics
        response += f"**📈 آمار گراف:**\n"
        response += f"• تعداد گره‌ها: {len(concepts)}\n"
        response += f"• تعداد یال‌ها: {len(relationships)}\n"
        response += f"• پیچیدگی گراف: {'ساده' if len(relationships) < 3 else 'متوسط' if len(relationships) < 8 else 'پیچیده'}\n\n"
        
        response += "💡 **نکته:** برای جستجو در گراف‌های قبلی از دستور 'جستجوی گراف' استفاده کنید."
        
        return response
    
    def _format_search_response(self, matching_graphs: List[Dict], search_term: str) -> str:
        """Format the search results response."""
        response = f"🔍 **نتایج جستجو برای: \"{search_term}\"** ({len(matching_graphs)} مورد)\n\n"
        
        if matching_graphs:
            for i, graph in enumerate(matching_graphs[:5], 1):
                response += f"**{i}.** 📊 گراف #{graph['id']}\n"
                response += f"   **متن:** {graph['source_text']}\n"
                response += f"   🧠 مفاهیم: {graph['concepts_count']} | 🔗 روابط: {graph['relationships_count']}\n"
                response += f"   🕒 {graph['created_at'][:19].replace('T', ' ')}\n\n"
            
            if len(matching_graphs) > 5:
                response += f"... و {len(matching_graphs) - 5} نتیجه دیگر\n\n"
        else:
            response += "❌ **هیچ گراف دانشی یافت نشد.**\n\n"
        
        response += "💡 **راهنما:** برای ساخت گراف جدید، متن خود را برای تحلیل ارسال کنید."
        
        return response
    
    def _format_list_response(self, graphs: List[Dict]) -> str:
        """Format the graphs list response."""
        response = f"📚 **گراف‌های دانش ذخیره شده** ({len(graphs)} مورد):\n\n"
        
        if graphs:
            for i, graph in enumerate(graphs, 1):
                response += f"**{i}.** 🧠 گراف #{graph['id']}\n"
                response += f"   **متن:** {graph['source_text']}\n"
                response += f"   📊 مفاهیم: {graph['concepts_count']} | 🔗 روابط: {graph['relationships_count']}\n"
                response += f"   🕒 {graph['created_at'][:19].replace('T', ' ')}\n\n"
        else:
            response += "📭 **هنوز هیچ گراف دانشی ساخته نشده است.**\n\n"
        
        response += "💡 **راهنما:** برای ساخت گراف جدید، متن خود را برای تحلیل ارسال کنید."
        
        return response
    
    def _get_concept_emoji(self, concept_type: str) -> str:
        """Get emoji for concept type."""
        concept_emojis = {
            "هدف": "🎯",
            "مشکل": "❗",
            "راه‌حل": "💡",
            "فرآیند": "⚙️",
            "شخص": "👤",
            "مکان": "📍",
            "ایده": "💭",
            "شیء": "📦"
        }
        return concept_emojis.get(concept_type, "🔸")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "استخراج مفاهیم از متن",
            "تشخیص روابط بین مفاهیم",
            "ساخت گراف دانش ساختاری",
            "ذخیره گراف در دیتابیس",
            "جستجو در گراف‌های موجود",
            "نمایش آماری گراف‌ها"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for knowledge graphs."""
        try:
            db = SessionLocal()
            
            total_graphs = db.query(KnowledgeGraph).count()
            recent_graphs = db.query(KnowledgeGraph).filter(
                KnowledgeGraph.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count()
            
            # Get average concepts and relationships
            graphs = db.query(KnowledgeGraph).all()
            avg_concepts = sum(len(g.concepts) for g in graphs) / len(graphs) if graphs else 0
            avg_relationships = sum(len(g.relationships) for g in graphs) / len(graphs) if graphs else 0
            
            db.close()
            
            return {
                "total_graphs": total_graphs,
                "recent_graphs": recent_graphs,
                "avg_concepts": round(avg_concepts, 1),
                "avg_relationships": round(avg_relationships, 1),
                "table_name": "knowledge_graph"
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_graphs": 0,
                "recent_graphs": 0,
                "avg_concepts": 0,
                "avg_relationships": 0,
                "error": str(e)
            }