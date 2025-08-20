from langchain.prompts import PromptTemplate
from .base import BaseReviewAgent

class PerformanceAgent(BaseReviewAgent):
    """Agent specialized in performance optimization"""
    
    def _create_prompt(self) -> PromptTemplate:
        template = """You are a performance optimization expert reviewing code.

Code to review:
{code}

{context}

Focus on:
- Time complexity issues (O(n²), O(n³) operations)
- Memory usage problems and leaks
- Inefficient loops or algorithms
- Database query optimization (N+1 queries, missing indexes)
- Resource management (file handles, connections)
- Caching opportunities
- Unnecessary computations or redundant operations

Provide specific performance improvement suggestions.
For each issue:
1. Identify the performance bottleneck
2. Explain the impact (time/space complexity)
3. Suggest an optimized approach

Performance Review:"""
        
        return PromptTemplate(
            input_variables=["code", "context"],
            template=template,
            partial_variables={"context": ""}
        )
    
    def get_focus_areas(self) -> list:
        return [
            "Time Complexity",
            "Memory Usage",
            "Algorithm Efficiency",
            "Database Queries",
            "Resource Management",
            "Caching",
            "Redundant Operations"
        ]
