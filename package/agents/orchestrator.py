import concurrent.futures
from typing import Dict, List, Any, Optional
from langchain_ollama import OllamaLLM
import logging
import time

from .security_agent import SecurityAgent
from .performance_agent import PerformanceAgent
from .style_agent import StyleAgent
from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_WORKERS, AGENT_TIMEOUT

logger = logging.getLogger(__name__)

class ReviewOrchestrator:
    """Orchestrates multiple review agents"""
    
    def __init__(self):
        self.llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
            num_predict=1000
        )
        
        self.agents = {
            "security": SecurityAgent(self.llm, "Security Agent"),
            "performance": PerformanceAgent(self.llm, "Performance Agent"),
            "style": StyleAgent(self.llm, "Style Agent")
        }
        
        logger.info(f"Initialized {len(self.agents)} review agents")
    
    def review_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        results = {
            "reviews": {},
            "summary": {},
            "metadata": {}
        }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_agent = {
                executor.submit(
                    agent.review, 
                    code, 
                    context
                ): agent_name
                for agent_name, agent in self.agents.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_agent, timeout=AGENT_TIMEOUT):
                agent_name = future_to_agent[future]
                try:
                    review_result = future.result()
                    results["reviews"][agent_name] = review_result
                    logger.info(f"Completed review from {agent_name}")
                except Exception as e:
                    logger.error(f"Agent {agent_name} failed: {str(e)}")
                    results["reviews"][agent_name] = {
                        "error": str(e),
                        "agent_name": agent_name,
                        "raw_feedback": f"Review failed: {str(e)}"
                    }
        
        results["summary"] = self._calculate_summary(results["reviews"])
        
        results["metadata"] = {
            "execution_time": time.time() - start_time,
            "agents_count": len(self.agents),
            "successful_reviews": sum(1 for r in results["reviews"].values() if "error" not in r),
            "code_length": len(code),
            "has_context": context is not None
        }
        
        logger.info(f"Completed all reviews in {results['metadata']['execution_time']:.2f} seconds")
        return results
    
    def review_repository(self, files: Dict[str, str]) -> Dict[str, Any]:
        # TODO: Implement sophisticated repository analysis
        # For now, review each file with awareness of others
        
        all_results = {}
        file_list = list(files.keys())
        
        for filepath, code in files.items():
            context = {
                "current_file": filepath,
                "related_files": [f for f in file_list if f != filepath],
                "total_files": len(files),
                "project_type": self._detect_project_type(files)
            }
            
            all_results[filepath] = self.review_code(code, context)
        
        all_results["repository_summary"] = self._analyze_repository_patterns(all_results)
        
        return all_results
    
    def _calculate_summary(self, reviews: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from all reviews"""
        total_issues = 0
        avg_confidence = 0.0
        critical_findings = []
        
        for agent_name, review in reviews.items():
            if "error" not in review:
                total_issues += review.get("issues_found", 0)
                avg_confidence += review.get("confidence", 0.0)

                if review.get("issues_found", 0) > 2:
                    critical_findings.append(agent_name)
        
        num_successful = len([r for r in reviews.values() if "error" not in r])
        
        return {
            "total_issues": total_issues,
            "average_confidence": avg_confidence / num_successful if num_successful > 0 else 0,
            "critical_agents": critical_findings,
            "review_consensus": self._determine_consensus(reviews)
        }
    
    def _determine_consensus(self, reviews: Dict[str, Any]) -> str:
        issues_count = sum(r.get("issues_found", 0) for r in reviews.values() if "error" not in r)
        
        if issues_count == 0:
            return "Excellent - No issues found"
        elif issues_count <= 3:
            return "Good - Minor issues to address"
        elif issues_count <= 7:
            return "Fair - Several improvements needed"
        else:
            return "Poor - Significant refactoring recommended"
    
    def _detect_project_type(self, files: Dict[str, str]) -> str:
        extensions = {filepath.split('.')[-1] for filepath in files.keys() if '.' in filepath}
        
        if 'py' in extensions:
            return "Python"
        elif 'js' in extensions or 'ts' in extensions:
            return "JavaScript/TypeScript"
        elif 'java' in extensions:
            return "Java"
        else:
            return "Mixed/Unknown"
    
    def _analyze_repository_patterns(self, results: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement cross-file pattern analysis
        return {
            "common_issues": [],
            "architectural_concerns": [],
            "consistency_score": 0.0
        }
