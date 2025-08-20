from langchain.prompts import PromptTemplate
from .base import BaseReviewAgent

class SecurityAgent(BaseReviewAgent):
    """Agent specialized in security vulnerability detection"""
    
    def _create_prompt(self) -> PromptTemplate:
        template = """You are a security expert reviewing code for vulnerabilities.

Code to review:
{code}

{context}

Focus on:
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) vulnerabilities  
- Authentication/authorization issues
- Input validation problems
- Cryptographic weaknesses
- Hardcoded secrets or credentials
- Path traversal vulnerabilities
- Insecure deserialization

Provide specific, actionable security recommendations.
Format your response with:
1. List each vulnerability found
2. Explain the potential impact
3. Provide a specific fix or mitigation

Security Review:"""
        
        return PromptTemplate(
            input_variables=["code", "context"],
            template=template,
            partial_variables={"context": ""}  # Default empty context
        )
    
    def get_focus_areas(self) -> list:
        return [
            "SQL Injection",
            "XSS",
            "Authentication",
            "Input Validation",
            "Cryptography",
            "Secrets Management",
            "Path Traversal",
            "Deserialization"
        ]
