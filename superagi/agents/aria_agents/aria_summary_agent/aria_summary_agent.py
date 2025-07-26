
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger


class AriaSummaryAgent(BaseAriaAgent):
    """
    Aria Summary Agent - Specializes in content summarization and analysis
    """

    def get_capabilities(self) -> List[str]:
        return [
            "text_summarization",
            "content_analysis",
            "key_point_extraction",
            "document_analysis",
            "data_aggregation",
            "insight_generation",
            "report_creation",
            "information_distillation"
        ]

    def get_agent_type(self) -> str:
        return "AriaSummaryAgent"

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute summarization and analysis tasks
        
        Args:
            task (str): The summarization task to perform
            context (Dict): Optional context containing content and parameters
            
        Returns:
            Dict: Task execution result with summary and analysis
        """
        try:
            logger.info(f"Executing summary task: {task}")
            
            if not context:
                context = {}
            
            task_type = context.get('task_type', 'text_summary')
            content = context.get('content', '')
            parameters = context.get('parameters', {})
            
            result = None
            
            if task_type == 'text_summary':
                result = self._summarize_text(content, parameters)
            elif task_type == 'data_summary':
                result = self._summarize_data(content, parameters)
            elif task_type == 'key_points':
                result = self._extract_key_points(content, parameters)
            elif task_type == 'analysis':
                result = self._analyze_content(content, parameters)
            elif task_type == 'report':
                result = self._generate_report(content, parameters)
            else:
                result = self._general_summary(task, content, parameters)
            
            execution_result = {
                "success": True,
                "result": result,
                "task": task,
                "task_type": task_type,
                "content_length": len(str(content)),
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.get_agent_type()
            }
            
            logger.info(f"Completed summary task: {task}")
            return execution_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task": task,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.get_agent_type()
            }
            logger.error(f"Error executing summary task: {str(e)}")
            return error_result

    def _summarize_text(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize text content"""
        if not content:
            return {"error": "No content provided for summarization"}
        
        summary_type = parameters.get('type', 'brief')
        max_length = parameters.get('max_length', 200)
        
        # Simple extractive summarization
        sentences = self._split_into_sentences(content)
        
        if summary_type == 'brief':
            # Take first few sentences and key sentences
            summary_sentences = sentences[:3]
            if len(sentences) > 5:
                # Add middle and end sentences
                summary_sentences.extend(sentences[len(sentences)//2:len(sentences)//2+1])
                summary_sentences.extend(sentences[-1:])
        elif summary_type == 'detailed':
            # More comprehensive summary
            summary_sentences = sentences[:min(len(sentences), 8)]
        else:
            # Key points only
            summary_sentences = self._extract_key_sentences(sentences)
        
        summary = ' '.join(summary_sentences)
        
        # Truncate if needed
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
        
        return {
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(content), 2),
            "sentence_count": len(summary_sentences),
            "summary_type": summary_type
        }

    def _summarize_data(self, content: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize structured data"""
        summary_level = parameters.get('level', 'overview')
        
        if isinstance(content, dict):
            return self._summarize_dictionary(content, summary_level)
        elif isinstance(content, list):
            return self._summarize_list(content, summary_level)
        else:
            return self._summarize_other_data(content, summary_level)

    def _summarize_dictionary(self, data: dict, level: str) -> Dict[str, Any]:
        """Summarize dictionary data"""
        summary = {
            "type": "dictionary",
            "key_count": len(data),
            "keys": list(data.keys())[:10],  # First 10 keys
            "total_keys": len(data)
        }
        
        if level == 'detailed':
            # Analyze value types
            value_types = {}
            for key, value in data.items():
                vtype = type(value).__name__
                value_types[vtype] = value_types.get(vtype, 0) + 1
            
            summary.update({
                "value_types": value_types,
                "sample_entries": dict(list(data.items())[:5]),
                "nested_objects": sum(1 for v in data.values() if isinstance(v, (dict, list)))
            })
        
        return {"data_summary": summary}

    def _summarize_list(self, data: list, level: str) -> Dict[str, Any]:
        """Summarize list data"""
        summary = {
            "type": "list",
            "item_count": len(data),
            "first_item": data[0] if data else None,
            "last_item": data[-1] if data else None
        }
        
        if level == 'detailed' and data:
            # Analyze item types
            item_types = {}
            for item in data:
                itype = type(item).__name__
                item_types[itype] = item_types.get(itype, 0) + 1
            
            summary.update({
                "item_types": item_types,
                "sample_items": data[:5],
                "unique_items": len(set(str(item) for item in data)),
                "has_duplicates": len(data) != len(set(str(item) for item in data))
            })
        
        return {"data_summary": summary}

    def _summarize_other_data(self, data: Any, level: str) -> Dict[str, Any]:
        """Summarize other types of data"""
        summary = {
            "type": type(data).__name__,
            "value": str(data)[:100] if len(str(data)) > 100 else str(data),
            "length": len(str(data))
        }
        
        if isinstance(data, str):
            summary.update({
                "word_count": len(data.split()),
                "line_count": len(data.split('\n')),
                "character_count": len(data)
            })
        
        return {"data_summary": summary}

    def _extract_key_points(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key points from content"""
        if not content:
            return {"error": "No content provided for key point extraction"}
        
        max_points = parameters.get('max_points', 5)
        
        sentences = self._split_into_sentences(content)
        
        # Simple key point extraction based on sentence characteristics
        key_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Score sentences based on various factors
            score = 0
            
            # Longer sentences might be more informative
            if len(sentence) > 50:
                score += 1
            
            # Sentences with numbers might be important
            if any(char.isdigit() for char in sentence):
                score += 1
            
            # Sentences with certain keywords
            key_words = ['important', 'significant', 'key', 'main', 'primary', 'essential', 'critical', 'major']
            if any(word in sentence.lower() for word in key_words):
                score += 2
            
            # First and last sentences often contain key information
            if sentence in sentences[:2] or sentence in sentences[-2:]:
                score += 1
            
            key_sentences.append((sentence, score))
        
        # Sort by score and take top sentences
        key_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sent[0] for sent in key_sentences[:max_points]]
        
        return {
            "key_points": top_sentences,
            "total_sentences": len(sentences),
            "extracted_points": len(top_sentences),
            "extraction_method": "score_based"
        }

    def _analyze_content(self, content: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content structure and characteristics"""
        analysis_type = parameters.get('type', 'general')
        
        if isinstance(content, str):
            return self._analyze_text_content(content, analysis_type)
        elif isinstance(content, (dict, list)):
            return self._analyze_structured_content(content, analysis_type)
        else:
            return self._analyze_other_content(content, analysis_type)

    def _analyze_text_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze text content"""
        words = content.split()
        sentences = self._split_into_sentences(content)
        
        analysis = {
            "content_type": "text",
            "statistics": {
                "character_count": len(content),
                "word_count": len(words),
                "sentence_count": len(sentences),
                "paragraph_count": len(content.split('\n\n')),
                "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
                "average_sentence_length": round(len(words) / len(sentences), 2) if sentences else 0
            }
        }
        
        if analysis_type == 'detailed':
            # Word frequency analysis
            word_freq = {}
            for word in words:
                clean_word = word.lower().strip('.,!?";')
                if len(clean_word) > 3:  # Only count words longer than 3 characters
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Top words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            analysis["word_analysis"] = {
                "unique_words": len(word_freq),
                "most_frequent_words": top_words,
                "vocabulary_richness": round(len(word_freq) / len(words), 2) if words else 0
            }
        
        return {"content_analysis": analysis}

    def _analyze_structured_content(self, content: Any, analysis_type: str) -> Dict[str, Any]:
        """Analyze structured content (dict/list)"""
        if isinstance(content, dict):
            analysis = {
                "content_type": "dictionary",
                "structure": {
                    "key_count": len(content),
                    "depth": self._calculate_dict_depth(content),
                    "value_types": self._analyze_value_types(content)
                }
            }
        elif isinstance(content, list):
            analysis = {
                "content_type": "list",
                "structure": {
                    "item_count": len(content),
                    "item_types": self._analyze_list_types(content),
                    "has_nested_structures": any(isinstance(item, (dict, list)) for item in content)
                }
            }
        else:
            analysis = {"content_type": "unknown_structured"}
        
        return {"content_analysis": analysis}

    def _analyze_other_content(self, content: Any, analysis_type: str) -> Dict[str, Any]:
        """Analyze other types of content"""
        return {
            "content_analysis": {
                "content_type": type(content).__name__,
                "size": len(str(content)),
                "representation": str(content)[:200]
            }
        }

    def _generate_report(self, content: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report"""
        report_type = parameters.get('type', 'standard')
        sections = parameters.get('sections', ['summary', 'analysis', 'key_points'])
        
        report = {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": {}
        }
        
        if 'summary' in sections:
            summary_result = self._summarize_text(str(content), {'type': 'brief'}) if isinstance(content, str) else self._summarize_data(content, {'level': 'overview'})
            report["sections"]["summary"] = summary_result
        
        if 'analysis' in sections:
            analysis_result = self._analyze_content(content, {'type': 'detailed'})
            report["sections"]["analysis"] = analysis_result
        
        if 'key_points' in sections and isinstance(content, str):
            key_points_result = self._extract_key_points(content, {'max_points': 5})
            report["sections"]["key_points"] = key_points_result
        
        if 'statistics' in sections:
            stats = self._generate_statistics(content)
            report["sections"]["statistics"] = stats
        
        return {"report": report}

    def _generate_statistics(self, content: Any) -> Dict[str, Any]:
        """Generate basic statistics about content"""
        stats = {
            "content_type": type(content).__name__,
            "size": len(str(content)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if isinstance(content, str):
            stats.update({
                "words": len(content.split()),
                "characters": len(content),
                "lines": len(content.split('\n'))
            })
        elif isinstance(content, (list, dict)):
            stats.update({
                "items": len(content),
                "memory_usage": f"{len(str(content))} characters"
            })
        
        return stats

    def _general_summary(self, task: str, content: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general summarization tasks"""
        return {
            "general_summary": {
                "task": task,
                "content_type": type(content).__name__,
                "content_size": len(str(content)),
                "parameters": parameters,
                "result": "General summarization completed",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    # Helper methods
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_key_sentences(self, sentences: List[str]) -> List[str]:
        """Extract the most important sentences"""
        # Simple heuristic: first sentence, longest sentences, last sentence
        if not sentences:
            return []
        
        key_sentences = [sentences[0]]  # First sentence
        
        if len(sentences) > 2:
            # Add longest sentence from middle
            middle_sentences = sentences[1:-1]
            if middle_sentences:
                longest = max(middle_sentences, key=len)
                key_sentences.append(longest)
            
            # Add last sentence
            key_sentences.append(sentences[-1])
        
        return key_sentences

    def _calculate_dict_depth(self, d: dict, current_depth: int = 1) -> int:
        """Calculate the maximum depth of a nested dictionary"""
        if not isinstance(d, dict):
            return current_depth
        
        max_depth = current_depth
        for value in d.values():
            if isinstance(value, dict):
                depth = self._calculate_dict_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth

    def _analyze_value_types(self, d: dict) -> Dict[str, int]:
        """Analyze the types of values in a dictionary"""
        type_counts = {}
        for value in d.values():
            vtype = type(value).__name__
            type_counts[vtype] = type_counts.get(vtype, 0) + 1
        return type_counts

    def _analyze_list_types(self, lst: list) -> Dict[str, int]:
        """Analyze the types of items in a list"""
        type_counts = {}
        for item in lst:
            itype = type(item).__name__
            type_counts[itype] = type_counts.get(itype, 0) + 1
        return type_counts

    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response by executing summary task"""
        try:
            # Parse message to determine summary task
            task_context = context or {}
            task_context.setdefault('task_type', 'text_summary')
            task_context.setdefault('content', message)
            
            # Execute summary task
            result = self.execute(message, task_context)
            
            summary_result = result.get('result', {})
            if isinstance(summary_result, dict) and 'summary' in summary_result:
                response_text = summary_result['summary']
            else:
                response_text = "Summary completed successfully"
            
            return {
                "response": response_text,
                "success": True,
                "agent": self.get_agent_type(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "response": f"Error processing summary task: {str(e)}",
                "success": False,
                "agent": self.get_agent_type(),
                "timestamp": datetime.utcnow().isoformat()
            }
