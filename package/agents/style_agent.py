from langchain.prompts import PromptTemplate
from .base import BaseReviewAgent

class StyleAgent(BaseReviewAgent):
    """Agent specialized in code style and best practices"""
    
    def _create_prompt(self) -> PromptTemplate:
        template = """You are a code quality expert reviewing code style and best practices.

Code to review:
{code}

{context}

Focus on:
- Code readability and clarity
- Naming conventions (variables, functions, classes)
- Function/class design (single responsibility, DRY)
- Code organization and structure
- Documentation quality (docstrings, comments)
- Language-specific conventions (PEP 8 for Python, etc.)
- Error handling patterns
- Code duplication

Provide specific code quality recommendations.
For each issue:
1. Identify the style or practice violation
2. Explain why it matters for maintainability
3. Show the improved approach

Style Review:"""
        
        return PromptTemplate(
            input_variables=["code", "context"],
            template=template,
            partial_variables={"context": ""}
        )
    
    def get_focus_areas(self) -> list:
        return [
            "Readability",
            "Naming Conventions",
            "Design Patterns",
            "Code Organization",
            "Documentation",
            "Language Conventions",
            "Error Handling",
            "DRY Principle"
        ]
