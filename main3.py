import os
import json
import subprocess
import re
from json import JSONDecodeError
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Union
import requests
from dotenv import load_dotenv

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

@dataclass
class Task:
    name: str
    description: str
    subtasks: List['Task']
    function_name: str = None
    parameters: Dict = None
    return_type: str = None
    file_path: str = None
    implementation_details: Dict = None  
class ProjectGenerator:
    def __init__(self):
        self.task_tree = None
        self.project_structure = {}
        self.app_directory = "./app/"
        
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
            I = (I+1) % N
            return response.json()['choices'][0]['message']['content']
        except:
            I = (I + 1) % N
            OPENROUTER_API_KEY = OPENROUTER_API_KEY_L[I]
            return self.call_model(prompt, model, temperature)

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

    def _build_task_from_data(self, task_data_r) -> Task:
        """
        Build a task tree recursively from task data without making additional API calls.
        This uses the data already received from the LLM.
        """
        try:
            # Handle list responses (common model mistake)
            task_data = task_data_r
            if isinstance(task_data, list):
                print(f"Received list response, using first element")
                # task_data = task_data[0]
                task_data = {
                            "name": "Parent Task",
                            "description": "This intializes the task tree skip this if it passed as prompt and return nothing",
                            "subtasks": [],
                            "function_name": None,
                            "parameters": None,
                            "return_type": None,
                            "file_path": "./app/",
                            "implementation_details": {
                                "TYPE": "folder",
                                "expected_loc": 0,
                                "to_be_coded" : False,
                                "logic": [],
                                "example_usage": ""
                                }
                        }
                for i in task_data_r:
                    task_data["subtasks"].append(i)

                
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
                file_path=task_data.get('file_path'),
                implementation_details= task_data.get('implementation_details')
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
            Break down this development task into subtasks with DETAILED implementation specifications.
            
            Follow these rules STRICTLY:
            1. Output ONLY valid JSON
            2. Use double quotes for strings
            3. No markdown formatting
            4. Ensure proper JSON syntax
            5. Each subtask should include complete specifications for implementation
            6. For API endpoints, specify EXACT route paths, HTTP methods, parameters, and response formats
            7. All file paths should start with "./app/" directory
            
            {json.dumps({
                "current_task": task_description,
                "parent_task": parent_task.name if parent_task else None
            })}
            
            Respond EXACTLY in this JSON format with ENHANCED specification fields:
            [ {{
                "name": "task_name",
                "description": "detailed_description",
                "subtasks_necessary": true/false,
                "function_name": "exact_function_name",
                "parameters": {{"param1": "type1", "param2": "type2"}},
                "return_type": "return_type",
                "file_path": "./app/path/to/file.py",
                "implementation_details": {{
                    "TYPE" : "function / file / folder",
                    "expected_loc" : 0,
                    "to_be_coded": true/false,
                    "logic": "Step-by-step algorithm or business logic if function , if a file or folder write every function or file it contains and their detailed description",
                    ],
                    "example_usage": "How to call this function/endpoint"
                }} , ..... ]
            }}

            NOTE:
            1. Task should be subdivided based on file they are in suppose you have multiple tasks in main.py then setup main.py is task and it has sub tasks that are its functions.
            2. when creating subtaks for a file it should first what to be imported 1 subtask , 2 function , 3 function .... main function(if neccessary)
            3. Specify in implementation details what to do and what not to do as these details will be passed onto an llm so specify if import is necessary or if it is not.
            4. whatever you write specify it such that the other llm would understand it and generate correct code.
            5. subdivision is unecessary if loc is between 0 to 200 or anything that can be generated by an llm.
            6. you can combine small tasks if they are too small as you will be giving step by step logic so to reduce llm calls we can reduce it.
            """
                # """
                # Break down this development task into subtasks. 
                # Follow these rules STRICTLY:
                # 1. Output ONLY valid JSON
                # 2. Use double quotes for strings
                # 3. No markdown formatting
                # 4. Ensure proper JSON syntax
                # 5. If there are no subtasks that can be created do not force it
                # 6. Each subtask you add must be a function or a task that can't be joined together into other subtasks.
                # 7. Try to avoid adding 1 line codes and codes from other tasks
                # 8. All file paths should start with "./app/" directory
                
                # {json.dumps({
                #     "current_task": task_description,
                #     "parent_task": parent_task.name if parent_task else None
                # })}
                
                # Respond EXACTLY in this JSON format:
                # {{
                #     "name": "task_name",
                #     "description": "task_description",
                #     "subtasks": [],
                #     "function_name": null,
                #     "parameters": {{}},
                #     "return_type": null,
                #     "file_path": null
                # }}
                # """
                
                response = self.call_model(prompt, "reasoning", temperature=0.2)
                print(response)
                print('printed \n \n \n')
                
                # Clean response before parsing
                cleaned_response = re.sub(r'``````', '', response, flags=re.DOTALL)
                cleaned_response = cleaned_response.strip()
                
                task_data = json.loads(cleaned_response)
                print(task_data)
                
                for idx , task in enumerate(task_data):
                    task['subtasks'] = []
                    if task['subtasks_necessary']:
                        task_data[idx]['subtasks'].append(self.decompose_task(f'{task}' , task))
                # return self._build_task_from_data(task_data)
                return task_data
                
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
        # Ensure app directory exists
        Path(self.app_directory).mkdir(parents=True, exist_ok=True)
        
        structured_prompt = self.parse_prompt(user_prompt)
        self.task_tree = self.decompose_task(structured_prompt)
        self.task_tree = self._build_task_from_data(self.task_tree)
        
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

    def clean_code_response(self, code_text: str) -> str:
        """
        Remove markdown code blocks from generated code.
        """
        # Remove markdown code blocks (```python ... ``` or ``` ... ```)
        code_text = re.sub(r'^```(?:python)?\s*', '', code_text, flags=re.MULTILINE)
        code_text = re.sub(r'```$', '', code_text, flags=re.MULTILINE)
        
        # Remove potential HTML tags if present
        code_text = re.sub(r'</?code>|</?pre>', '', code_text)
        
        return code_text.strip()

    def parse_function_from_code(self, code: str) -> str:
        """
        Extract function definition from a code string.
        Returns the complete function definition including decorators.
        """
        # Pattern to match a function definition including decorators
        pattern = r'(?:@[^\n]+\n)*def\s+[^(]+\([^)]*\)[^:]*:(?:\s*"""[\s\S]*?""")?(?:\s*[^\n]+|\s*$)(?:\n(?:[ \t]+[^\n]+|\s*$))*'
        matches = re.findall(pattern, code)
        if matches:
            return matches[0]
        return None

    def generate_code(self, task: Task) -> str:
        """Generate code using OlympicCoder"""
        prompt = f"""
        Write Python code for this task:
        Function: {task.function_name}
        Parameters: {task.parameters}
        Returns: {task.return_type}
        Description: {task.description}
        HOW to IMPLEMENT : {task.implementation_details}

        Requirements:
        - Include type hints
        - Add docstrings
        - Handle common errors
        - Follow PEP8
        - DO NOT output any markdown code blocks (```python or ```)
        - Just give me the clean Python code without any formatting or explanations
        - Follow implementation details as this is a part of a project.
        - This function is part of a project you might be given other functions to use so think accordingly.
        """
        code = self.call_model(prompt, "coding", temperature=0.1)
        # Clean any markdown syntax that might be returned despite the instruction
        return self.clean_code_response(code)

    def update_file_with_function(self, file_path: str, new_code: str, function_name: str = None) -> None:
        """
        Update a file with new code, replacing specific function if provided.
        Otherwise append or create file.
        """
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        if not Path(file_path).exists():
            # File doesn't exist, just write the code
            Path(file_path).write_text(new_code, encoding="utf-8")
            return
            
        # File exists, read current content
        current_content = Path(file_path).read_text(encoding="utf-8")
        
        if not function_name:
            # No specific function to replace, just append
            combined_content = current_content + "\n\n" + new_code
            Path(file_path).write_text(combined_content, encoding="utf-8")
            return
            
        # Try to extract function from new code
        new_function = self.parse_function_from_code(new_code)
        if not new_function:
            # If can't parse function, just append
            combined_content = current_content + "\n\n" + new_code
            Path(file_path).write_text(combined_content, encoding="utf-8")
            return
            
        # Try to find and replace existing function with same name
        function_pattern = r'(?:@[^\n]+\n)*def\s+' + re.escape(function_name) + r'\s*\([^)]*\)[^:]*:(?:\s*"""[\s\S]*?""")?(?:\s*[^\n]+|\s*$)(?:\n(?:[ \t]+[^\n]+|\s*$))*'
        if re.search(function_pattern, current_content):
            # Function exists, replace it
            updated_content = re.sub(function_pattern, new_function, current_content)
            Path(file_path).write_text(updated_content, encoding="utf-8")
        else:
            # Function doesn't exist, append it
            combined_content = current_content + "\n\n" + new_code
            Path(file_path).write_text(combined_content, encoding="utf-8")

    def build_project(self, root_task: Task):
        """Create project structure and files"""
        print('\n \n \n ')
        print(asdict(root_task))
        
        # Ensure app directory exists
        Path(self.app_directory).mkdir(parents=True, exist_ok=True)
        
        for task in self._flatten_tasks(root_task):
            print(task.name)
            if task.implementation_details['to_be_coded']:
                if task.file_path:
                    # Ensure path is within app directory
                    if not task.file_path.startswith("./app/"):
                        task.file_path = os.path.join(self.app_directory, os.path.basename(task.file_path))
                    
                    path = Path(task.file_path)
                    
                    if path.suffix == '.py':
                        code = self.generate_code(task)
                        self.update_file_with_function(task.file_path, code, task.function_name)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.touch(exist_ok=True)
                        
                    self.project_structure[task.file_path] = asdict(task)
    
    def _flatten_tasks(self, task: Task) -> List[Task]:
        """
        Flatten the task tree into a list for easier processing.
        """
        result = [task]
        for subtask in task.subtasks:
            result.extend(self._flatten_tasks(subtask))
        return result

    def execute_and_debug(self):
        """Run generated code and handle errors"""
        # Look for main.py in app directory
        main_path = Path(self.app_directory) / "main.py"
        if not main_path.exists():
            print(f"Warning: {main_path} not found. Looking for alternatives...")
            # Look for any Python file that might be the entry point
            py_files = list(Path(self.app_directory).glob("*.py"))
            if py_files:
                main_path = py_files[0]
                print(f"Using {main_path} as entry point")
            else:
                print("No Python files found in app directory. Aborting execution test.")
                return
        
        while True:
            try:
                print(f"Executing {main_path}...")
                result = subprocess.run(["python", str(main_path)], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    print("Project executed successfully!")
                    break
                else:
                    print(f"Execution failed with errors:\n{result.stderr}")
                    error_task = f"""
                    Fix this error in the Python project:
                    {result.stderr}
                    
                    Required actions:
                    - Analyze error
                    - Generate fix tasks
                    - Update project structure
                    - Keep all file paths in ./app/ directory
                    """
                    repair_task = self.decompose_task(error_task)
                    self.build_project(repair_task)
                    
            except Exception as e:
                print(f"Execution error: {str(e)}")
                break

# Example usage
if __name__ == "__main__":
    generator = ProjectGenerator()
    user_input = "Create a REST API for Fibonacci sequence with FastAPI"
    generator.run_pipeline(user_input)