import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class PromptTemplate:
    """A prompt template"""
    
    def __init__(self, name: str, template: str, description: str = ""):
        self.name = name
        self.template = template
        self.description = description
        self.variables = self._extract_variables(template)
    
    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from template"""
        import re
        return re.findall(r'\{\{(\w+)\}\}', template)
    
    def format(self, **kwargs) -> str:
        """Format the template with variables"""
        formatted = self.template
        for var in self.variables:
            value = kwargs.get(var, f"{{{{{var}}}}}")
            formatted = formatted.replace(f"{{{{{var}}}}}", str(value))
        return formatted

class PromptManager:
    """Manage prompt templates"""
    
    def __init__(self, prompts_dir: str = "./prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.templates = {}
        self.load_prompts()
    
    def load_prompts(self):
        """Load prompt templates from directory"""
        # Default prompts
        default_prompts = {
            'chat': PromptTemplate(
                name='chat',
                template="""You are a helpful AI assistant. Answer the user's questions helpfully and accurately.

Conversation history:
{history}

Current question: {question}

Assistant:""",
                description="Default chat prompt"
            ),
            'summarize': PromptTemplate(
                name='summarize',
                template="""Please summarize the following text concisely:

{text}

Summary:""",
                description="Text summarization"
            ),
            'translate': PromptTemplate(
                name='translate',
                template="""Translate the following text from {source_language} to {target_language}:

{text}

Translation:""",
                description="Text translation"
            ),
            'code_explain': PromptTemplate(
                name='code_explain',
                template="""Explain the following code:

{code}

Explanation:""",
                description="Code explanation"
            ),
            'rag_qa': PromptTemplate(
                name='rag_qa',
                template="""Based on the following context, answer the question. If you don't know, say so.

Context:
{context}

Question: {question}

Answer:""",
                description="RAG-based Q&A"
            )
        }
        
        self.templates.update(default_prompts)
        
        # Load custom prompts from files
        for prompt_file in self.prompts_dir.glob("*.yaml"):
            try:
                with open(prompt_file, 'r') as f:
                    prompt_data = yaml.safe_load(f)
                
                for name, data in prompt_data.items():
                    self.templates[name] = PromptTemplate(
                        name=name,
                        template=data.get('template', ''),
                        description=data.get('description', '')
                    )
            except Exception as e:
                logger.error(f"Failed to load prompt file {prompt_file}: {e}")
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                'name': name,
                'description': template.description,
                'variables': template.variables
            }
            for name, template in self.templates.items()
        ]
    
    def add_template(self, name: str, template: str, description: str = "") -> bool:
        """Add a new template"""
        if name in self.templates:
            logger.warning(f"Template {name} already exists")
            return False
        
        self.templates[name] = PromptTemplate(name, template, description)
        self.save_template(name)
        return True
    
    def save_template(self, name: str):
        """Save a template to file"""
        template = self.templates.get(name)
        if not template:
            return
        
        prompt_file = self.prompts_dir / f"{name}.yaml"
        data = {
            name: {
                'template': template.template,
                'description': template.description
            }
        }
        
        try:
            with open(prompt_file, 'w') as f:
                yaml.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save template {name}: {e}")

# Global prompt manager
prompt_manager = PromptManager()