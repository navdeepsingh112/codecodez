import os
import json
import subprocess
from json import JSONDecodeError
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict
import requests
from dotenv import load_dotenv
import re
load_dotenv()
# Configure OpenRouter access
OPENROUTER_API_KEY_L = os.getenv("OPENROUTER_API_KEY").split(',')
N = len(OPENROUTER_API_KEY_L)
print(OPENROUTER_API_KEY_L)
I = 0
OPENROUTER_API_KEY = OPENROUTER_API_KEY_L[1]
BASE_URL = "https://openrouter.ai/api/v1"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "X-Title": "AI Project Builder"
}

MODEL_CONFIG = {
    "reasoning": "deepseek/deepseek-r1:free",
    "language": "google/gemini-2.5-pro-exp-03-25:free",
    "coding": "open-r1/olympiccoder-32b:free"
}
# const response = await fetch('https://openrouter.ai/api/v1/auth/key', {
#   method: 'GET',
#   headers: {
#     Authorization: 'Bearer <OPENROUTER_API_KEY>',
#   },
# });

# response = requests.get(
#   url='https://openrouter.ai/api/v1/auth/key',
#   headers={
#     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#     "Content-Type": "application/json",
#   },
#   data=json.dumps({
#     "model": MODEL_CONFIG['reasoning'], # Optional
#     "messages": [
#       {
#         "role": "user",
#         "content": "What is the meaning of life?"
#       }
#     ]
#   })
# )

# print(response.json())
@dataclass
class Task:
    name: str
    description: str
    subtasks: List['Task']
    function_name: str = None
    parameters: Dict = None
    return_type: str = None
    file_path: str = None

class ProjectGenerator:
    def __init__(self):
        self.task_tree = None
        self.project_structure = {}
        
    def call_model(self, prompt: str, model: str, temperature=0.7) -> str:
        """Generic OpenRouter API caller"""
        global I, OPENROUTER_API_KEY
        try:
            print(model , 'called')
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=HEADERS,
                json={
                    "model": MODEL_CONFIG[model],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature
                },
            timeout=120
            )
            print(model)
            print(response.json())
            I=(I+1) % N
            return response.json()['choices'][0]['message']['content']
        except:
            I = (I + 1) % N
            OPENROUTER_API_KEY = OPENROUTER_API_KEY_L[I]
            return self.call_model( prompt , model , temperature)

    def parse_prompt(self, user_prompt: str) -> str:
        """Use Gemini for language understanding"""
        prompt = f"""
        Clarify and structure this project requirement:
        {user_prompt}
        
        Output format:
        - Project purpose
        - Key components
        - Technical requirements
        - Edge cases to consider
        """
        return self.call_model(prompt, "language", temperature=0.3)

    # def decompose_task(self, task_description: str, parent_task=None) -> Task:
    #     """Recursive task decomposition using DeepSeek R1"""
    #     prompt = f"""
    #     Break down this development task into subtasks. 
    #     Follow these rules:
    #     1. Split until atomic functions are reached
    #     2. Define function signatures
    #     3. Specify file structure
    #     4. Consider error handling
        
    #     Current task: {task_description}
    #     {f"Parent task: {parent_task.name}" if parent_task else ""}
        
    #     Respond in JSON format with: name, description, subtasks[], function_name, parameters, return_type, file_path
    #     """
        
    #     response = self.call_model(prompt, "reasoning", temperature=0.2)
    #     task_data = json.loads(response)
    #     task = Task(**task_data)
        
    #     if not task.subtasks:
    #         return task
            
    #     task.subtasks = [self.decompose_task(sub, task) for sub in task.subtasks]
    #     return task
    # def decompose_task(self, task_description: str, parent_task=None) -> Task:
    #     """Recursive task decomposition with error handling"""
    #     max_retries = 3
    #     for attempt in range(max_retries):
    #         try:
    #             prompt = f"""
    #             Break down this development task into subtasks. 
    #             Follow these rules STRICTLY:
    #             1. Output ONLY valid JSON
    #             2. Use double quotes for strings
    #             3. No markdown formatting
    #             4. Ensure proper JSON syntax
                
    #             {json.dumps({
    #                 "current_task": task_description,
    #                 "parent_task": parent_task.name if parent_task else None
    #             })}
                
    #             Respond EXACTLY in this JSON format:
    #             {{
    #                 "name": "task_name",
    #                 "description": "task_description",
    #                 "subtasks": [],
    #                 "function_name": null,
    #                 "parameters": {{}},
    #                 "return_type": null,
    #                 "file_path": null
    #             }}
    #             """
                
    #             response = self.call_model(prompt, "reasoning", temperature=0.2)
    #             print(response)
    #             print('printed \n \n \n')
    #             # Clean response before parsing
    #             # cleaned_response = re.sub(r'[\s\n]*``````[\s\n]*', r'\1', response)
    #             # Fixed regex substitution
    #             cleaned_response = re.sub(r'``````', '', response, flags=re.DOTALL)

    #             cleaned_response = cleaned_response.strip()
                
    #             task_data = json.loads(cleaned_response)
    #             print(task_data)
    #             # task = Task(**task_data)
                
    #             # # Validate task structure
    #             # if not isinstance(task.subtasks, list):
    #             #     raise ValueError("Invalid subtasks format")
                    
    #             # if not task.name or not task.description:
    #             #     raise ValueError("Missing required fields")
                
    #             # # Process subtasks recursively if needed
    #             # if task.subtasks:
    #             #     task.subtasks = [self.decompose_task(sub, task) for sub in task.subtasks]
                
    #             # return task
    #             try:
    #                 # Handle list responses (common model mistake)
    #                 if isinstance(task_data, list):
    #                     print(f"Received list response, using first element")
    #                     task_data = task_data[0]
                        
    #                 # Validate root is dict
    #                 if not isinstance(task_data, dict):
    #                     raise ValueError(f"Expected dict, got {type(task_data)}")
                        
    #                 # Ensure subtasks are properly formatted
    #                 if 'subtasks' in task_data:
    #                     if not isinstance(task_data['subtasks'], list):
    #                         raise ValueError("Subtasks must be a list")
                            
    #                     # Convert string subtasks to proper format
    #                     task_data['subtasks'] = [
    #                         self._convert_to_task_dict(sub) 
    #                         for sub in task_data['subtasks']
    #                     ]
                        
    #                 # Create Task instance
    #                 return Task(
    #                     name=str(task_data.get('name', '')),
    #                     description=str(task_data.get('description', '')),
    #                     subtasks=[],
    #                     function_name=task_data.get('function_name'),
    #                     parameters=task_data.get('parameters', {}),
    #                     return_type=task_data.get('return_type'),
    #                     file_path=task_data.get('file_path')
    #                 )
                    
    #             except Exception as e:
    #                 print(f"Task creation error: {str(e)}")
    #                 print(f"Problematic data: {task_data}")
    #                 return Task(name="Error", description=str(e), subtasks=[])
                
    #         except (JSONDecodeError, ValueError) as e:
    #             if attempt == max_retries - 1:
    #                 raise RuntimeError(f"Failed to parse model response after {max_retries} attempts: {str(e)}")
                
    #             print(f"Retry {attempt + 1}/{max_retries} for task decomposition")
    #             continue

    #     return Task(name="Error", description="Failed decomposition", subtasks=[])
    def _build_task_from_data(self, task_data) -> Task:
        """
        Build a task tree recursively from task data without making additional API calls.
        This uses the data already received from the LLM.
        """
        try:
            # Handle list responses (common model mistake)
            if isinstance(task_data, list):
                print(f"Received list response, using first element")
                task_data = task_data[0]
                
            # Validate root is dict
            if not isinstance(task_data, dict):
                raise ValueError(f"Expected dict, got {type(task_data)}")
            
            # Process subtasks first
            subtasks = []
            subtask_data_list = task_data.get('subtasks', [])
            
            if isinstance(subtask_data_list, list):
                for subtask_data in subtask_data_list:
                    # Recursively build each subtask
                    subtask = self._build_task_from_data(subtask_data)
                    subtasks.append(subtask)
            
            # Create the task with processed subtasks
            task = Task(
                name=str(task_data.get('name', '')),
                description=str(task_data.get('description', '')),
                subtasks=subtasks,  # Already processed subtasks
                function_name=task_data.get('function_name'),
                parameters=task_data.get('parameters', {}),
                return_type=task_data.get('return_type'),
                file_path=task_data.get('file_path')
            )
            
            return task
            
        except Exception as e:
            print(f"Task creation error: {str(e)}")
            print(f"Problematic data: {task_data}")
            return Task(name="Error", description=str(e), subtasks=[])
    def decompose_task(self, task_description: str, parent_task=None) -> Task:
        """Recursive task decomposition with error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                prompt = f"""
                Break down this development task into subtasks. 
                Follow these rules STRICTLY:
                1. Output ONLY valid JSON
                2. Use double quotes for strings
                3. No markdown formatting
                4. Ensure proper JSON syntax
                5. If there are no subtasks that can ve created do not force it
                6. Each subtask you add must be a function or a task that can't be joined together into other subtasks.
                7. try to avoid adding 1 line codes and codes from other tasks
                
                {json.dumps({
                    "current_task": task_description,
                    "parent_task": parent_task.name if parent_task else None
                })}
                
                Respond EXACTLY in this JSON format:
                {{
                    "name": "task_name",
                    "description": "task_description",
                    "subtasks": [],
                    "function_name": null,
                    "parameters": {{}},
                    "return_type": null,
                    "file_path": null
                }}
                """
                
                response = self.call_model(prompt, "reasoning", temperature=0.2)
                print(response)
                print('printed \n \n \n')
                
                # Clean response before parsing
                cleaned_response = re.sub(r'``````', '', response, flags=re.DOTALL)
                cleaned_response = cleaned_response.strip()
                
                task_data = json.loads(cleaned_response)
                print(task_data)
                return self._build_task_from_data(task_data)
                # Process the response
                # try:
                #     # Handle list responses (common model mistake)
                #     if isinstance(task_data, list):
                #         print(f"Received list response, using first element")
                #         task_data = task_data[0]
                        
                #     # Validate root is dict
                #     if not isinstance(task_data, dict):
                #         raise ValueError(f"Expected dict, got {type(task_data)}")
                    
                #     # Create the main task
                #     task = Task(
                #         name=str(task_data.get('name', '')),
                #         description=str(task_data.get('description', '')),
                #         subtasks=[],  # Initialize empty, will fill with DFS
                #         function_name=task_data.get('function_name'),
                #         parameters=task_data.get('parameters', {}),
                #         return_type=task_data.get('return_type'),
                #         file_path=task_data.get('file_path')
                #     )
                    
                #     # Store subtask data for processing
                #     subtasks_data = task_data.get('subtasks', [])
                #     if subtasks_data and isinstance(subtasks_data, list):
                #         # Process each subtask recursively
                #         for subtask_item in subtasks_data:
                #             if isinstance(subtask_item, dict) and 'description' in subtask_item:
                #                 # If subtask already has structured data
                #                 subtask_desc = subtask_item.get('description')
                #             elif isinstance(subtask_item, str):
                #                 # If subtask is just a string
                #                 subtask_desc = subtask_item
                #             else:
                #                 # Use name or convert to string
                #                 subtask_desc = subtask_item.get('name', str(subtask_item))
                            
                #             # Recursively decompose each subtask
                #             subtask = self.decompose_task(subtask_desc, task)
                #             task.subtasks.append(subtask)
                    
                #     return task
                    
                # except Exception as e:
                #     print(f"Task creation error: {str(e)}")
                #     print(f"Problematic data: {task_data}")
                #     return Task(name="Error", description=str(e), subtasks=[])
                
            except (JSONDecodeError, ValueError) as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to parse model response after {max_retries} attempts: {str(e)}")
                
                print(f"Retry {attempt + 1}/{max_retries} for task decomposition")
                continue

        return Task(name="Error", description="Failed decomposition", subtasks=[])

    def rebuild_task_tree(self, root_task: Task) -> Task:
        """
        DFS function to rebuild the task tree by ensuring all subtasks are properly connected.
        This is useful for debugging or rebuilding a broken task tree.
        """
        # Base case: no subtasks or empty list
        if not hasattr(root_task, 'subtasks') or not root_task.subtasks:
            return root_task
        
        # Process each subtask recursively
        processed_subtasks = []
        for subtask in root_task.subtasks:
            processed_subtask = self.rebuild_task_tree(subtask)
            processed_subtasks.append(processed_subtask)
        
        # Update the root task with processed subtasks
        root_task.subtasks = processed_subtasks
        return root_task

    def print_task_tree(self, task: Task, indent=0):
        """
        Helper method to print the task tree for debugging.
        """
        print(" " * indent + f"- {task.name}")
        print(" " * (indent + 2) + f"Description: {task.description[:50]}...")
        print(" " * (indent + 2) + f"Function: {task.function_name}")
        print(" " * (indent + 2) + f"File: {task.file_path}")
        print(" " * (indent + 2) + f"Subtasks: {len(task.subtasks)}")
        
        for subtask in task.subtasks:
            self.print_task_tree(subtask, indent + 4)

    def run_pipeline(self, user_prompt: str):
        """End-to-end project generation workflow with task tree validation"""
        structured_prompt = self.parse_prompt(user_prompt)
        self.task_tree = self.decompose_task(structured_prompt)
        
        # Ensure task tree is properly built
        self.task_tree = self.rebuild_task_tree(self.task_tree)
        
        # Print task tree for debugging
        print("\n=== Task Tree Structure ===")
        self.print_task_tree(self.task_tree)
        print("==========================\n")
        
        self.build_project(self.task_tree)
        
        # Save project metadata
        with open("README.md", "w") as f:
            json.dump(self.project_structure, f, indent=2)
            
        self.execute_and_debug()
    
    def _convert_to_task_dict(self, sub) -> dict:
        """Convert various subtask formats to proper dict"""
        if isinstance(sub, dict):
            return sub
        if isinstance(sub, str):
            return {'name': sub, 'description': sub, 'subtasks': []}
        return {'name': str(sub), 'description': str(sub), 'subtasks': []}

    def generate_code(self, task: Task) -> str:
        """Generate code using OlympicCoder"""
        prompt = f"""
        Write Python code for this task:
        Function: {task.function_name}
        Parameters: {task.parameters}
        Returns: {task.return_type}
        Description: {task.description}
        
        Requirements:
        - Include type hints
        - Add docstrings
        - Handle common errors
        - Follow PEP8
        """
        return self.call_model(prompt, "coding", temperature=0.1)

    def build_project(self, root_task: Task):
        """Create project structure and files"""
        print('\n \n \n ')
        print(asdict(root_task))
        for task in root_task.subtasks:
            print(task.name)
            if task.file_path:
                path = Path(task.file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                
                if path.suffix == '.py':
                    code = self.generate_code(task)
                    path.write_text(code, encoding="utf-8")
                else:
                    path.touch()
                    
                self.project_structure[task.file_path] = asdict(task)

    def execute_and_debug(self):
        """Run generated code and handle errors"""
        while True:
            try:
                result = subprocess.run(["python", "main.py"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("Project executed successfully!")
                    break
                else:
                    error_task = f"""
                    Fix this error:
                    {result.stderr}
                    
                    Required actions:
                    - Analyze error
                    - Generate fix tasks
                    - Update project structure
                    """
                    repair_task = self.decompose_task(error_task)
                    self.build_project(repair_task)
                    
            except Exception as e:
                print(f"Execution error: {str(e)}")
                break

    # def run_pipeline(self, user_prompt: str):
    #     """End-to-end project generation workflow"""
    #     structured_prompt = self.parse_prompt(user_prompt)
    #     self.task_tree = self.decompose_task(structured_prompt)
    #     self.build_project(self.task_tree)
        
    #     # Save project metadata
    #     with open("README.md", "w") as f:
    #         json.dump(self.project_structure, f, indent=2)
            
    #     self.execute_and_debug()

# Example usage
if __name__ == "__main__":
    generator = ProjectGenerator()
    user_input = "Create a REST API for Fibonacci sequence with FastAPI"
    generator.run_pipeline(user_input)
