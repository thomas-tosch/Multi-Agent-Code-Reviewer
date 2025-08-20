from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import logging

logger = logging.getLogger(__name__)

class CodeReviewParser(BaseOutputParser):
    def parse(self, text: str) -> Dict[str, Any]:
        return {
            "raw_feedback": text.strip(),
            "confidence": self._extract_confidence(text),
            "issues_found": self._count_issues(text)
        }
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from review (future enhancement)"""
        # TODO: Implement confidence extraction from LLM response
        return 0.8  # Default confidence for now
    
    def _count_issues(self, text: str) -> int:
        indicators = ['issue', 'problem', 'vulnerability', 'inefficient', 'violation']
        return sum(1 for indicator in indicators if indicator.lower() in text.lower())


class BaseReviewAgent(ABC):
    """Base class for all review agents"""
    
    def __init__(self, llm: OllamaLLM, name: str):
        self.llm = llm
        self.name = name
        self.parser = CodeReviewParser()
        self.prompt = self._create_prompt()
        self.chain = self.prompt | self.llm | self.parser
    
    @abstractmethod
    def _create_prompt(self) -> PromptTemplate:
        pass
    
    @abstractmethod
    def get_focus_areas(self) -> list:
        pass
    
    def review(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            input_data = {"code": code}
            
            if context:
                input_data["context"] = self._format_context(context)
            
            result = self.chain.invoke(input_data)
            
            result["agent_name"] = self.name
            result["focus_areas"] = self.get_focus_areas()
            
            logger.info(f"{self.name} completed review successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name} review: {str(e)}")
            return {
                "agent_name": self.name,
                "error": str(e),
                "raw_feedback": f"Error during review: {str(e)}",
                "confidence": 0.0,
                "issues_found": 0
            }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        context_str = ""
        if "related_files" in context:
            context_str += f"\nRelated files: {', '.join(context['related_files'])}"
        if "project_type" in context:
            context_str += f"\nProject type: {context['project_type']}"
        return context_str
