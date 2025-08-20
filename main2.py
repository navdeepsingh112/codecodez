import os
import json
import subprocess
from json import JSONDecodeError
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Set
import requests
from dotenv import load_dotenv
import re
import time
import datetime

load_dotenv()

# Configure OpenRouter access
OPENROUTER_API_KEY_L = os.getenv("OPENROUTER_API_KEY").split(',')
print(OPENROUTER_API_KEY_L)
I = 0
OPENROUTER_API_KEY = OPENROUTER_API_KEY_L[0]
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
    status: str = "pending"  # pending, completed, error
    error_message: str = None
    task_id: str = None  # Unique identifier for tracking

@dataclass
class ProjectState:
    user_prompt: str
    structured_prompt: str = None
    task_tree: Dict = None
    completed_tasks: Set[str] = field(default_factory=set)
    error_tasks: Dict[str, str] = field(default_factory=dict)  # task_id -> error_message
    last_executed: str = None
    

class ProjectGenerator:
    def __init__(self):
        self.task_tree = None
        self.project_structure = {}
        self.state_file = "project_state.json"
        self.task_file = "tasks.json"
        self.state = None
        
    def assign_task_ids(self, task: Task, prefix="task") -> Task:
        """Recursively assign unique IDs to tasks for tracking"""
        if not task.task_id:
            timestamp = int(time.time() * 1000)
            task.task_id = f"{prefix}_{timestamp}"
            
        for i, subtask in enumerate(task.subtasks):
            self.assign_task_ids(subtask, f"{task.task_id}_{i}")
            
        return task
        
    def call_model(self, prompt: str, model: str, temperature=0.7) -> str:
        """Generic OpenRouter API caller with retries and logging"""
        global I, OPENROUTER_API_KEY
        max_retries = 3
        
        for retry in range(max_retries):
            try:
                print(f"{model} called (attempt {retry+1}/{max_retries})")
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
                
                if response.status_code == 200:
                    print(f"{model} call successful")
                    return response.json()['choices'][0]['message']['content']
                else:
                    print(f"API error: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"API call error: {str(e)}")
                
            # Rotate API key on failure
            I = (I + 1) % len(OPENROUTER_API_KEY_L)
            OPENROUTER_API_KEY = OPENROUTER_API_KEY_L[I]
            HEADERS["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"
            print(f"Switching to API key {I}")
            time.sleep(1)  # Small delay between retries
        
        raise RuntimeError(f"Failed to get response from {model} after {max_retries} attempts")

    def parse_prompt(self, user_prompt: str) -> str:
        """Use Gemini for language understanding"""
        # Check if we already have a structured prompt in the state
        if self.state and self.state.structured_prompt:
            return self.state.structured_prompt
            
        prompt = f"""
        Clarify and structure this project requirement:
        {user_prompt}
        
        Output format:
        - Project purpose
        - Key components
        - Technical requirements
        - Edge cases to consider
        """
        structured_prompt = self.call_model(prompt, "language", temperature=0.3)
        
        # Save structured prompt to state
        if self.state:
            self.state.structured_prompt = structured_prompt
            self.save_state()
            
        return structured_prompt

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
                file_path=task_data.get('file_path'),
                status=task_data.get('status', 'pending'),
                error_message=task_data.get('error_message'),
                task_id=task_data.get('task_id')
            )
            
            return task
            
        except Exception as e:
            print(f"Task creation error: {str(e)}")
            print(f"Problematic data: {task_data}")
            return Task(name="Error", description=str(e), subtasks=[], status="error", error_message=str(e))

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
                5. If there are no subtasks that can be created do not force it
                6. Each subtask you add must be a function or a task that can't be joined together into other subtasks.
                7. Try to avoid adding 1 line codes and codes from other tasks
                
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
                
                # Clean response before parsing
                cleaned_response = re.sub(r'``````', '', response, flags=re.DOTALL)
                cleaned_response = cleaned_response.strip()
                
                task_data = json.loads(cleaned_response)
                print("Task data parsed successfully")
                
                # Build the task tree
                task = self._build_task_from_data(task_data)
                
                # Assign unique IDs to tasks
                task = self.assign_task_ids(task)
                
                return task
                
            except (JSONDecodeError, ValueError) as e:
                if attempt == max_retries - 1:
                    error_task = Task(
                        name="Error", 
                        description="Failed decomposition", 
                        subtasks=[],
                        status="error",
                        error_message=str(e)
                    )
                    return self.assign_task_ids(error_task)
                
                print(f"Retry {attempt + 1}/{max_retries} for task decomposition: {str(e)}")
                continue

        error_task = Task(name="Error", description="Failed decomposition after retries", subtasks=[], status="error")
        return self.assign_task_ids(error_task)

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
        status_marker = "✓" if task.status == "completed" else "✗" if task.status == "error" else "-"
        print(" " * indent + f"{status_marker} {task.name} [{task.task_id}]")
        print(" " * (indent + 2) + f"Description: {task.description[:50]}...")
        print(" " * (indent + 2) + f"Function: {task.function_name}")
        print(" " * (indent + 2) + f"File: {task.file_path}")
        print(" " * (indent + 2) + f"Status: {task.status}")
        if task.error_message:
            print(" " * (indent + 2) + f"Error: {task.error_message}")
        print(" " * (indent + 2) + f"Subtasks: {len(task.subtasks)}")
        
        for subtask in task.subtasks:
            self.print_task_tree(subtask, indent + 4)

    def save_task_tree(self, task: Task = None):
        """Save the current task tree to JSON"""
        if task is None:
            task = self.task_tree
        
        if task:
            with open(self.task_file, "w") as f:
                json.dump(asdict(task), f, indent=2)
                print(f"Task tree saved to {self.task_file}")

    def load_task_tree(self) -> Optional[Task]:
        """Load task tree from JSON file"""
        try:
            if os.path.exists(self.task_file):
                with open(self.task_file, "r") as f:
                    task_data = json.load(f)
                    task = self._build_task_from_data(task_data)
                    print(f"Task tree loaded from {self.task_file}")
                    return task
        except Exception as e:
            print(f"Error loading task tree: {str(e)}")
        return None

    def save_state(self):
        """Save current project state"""
        if self.state:
            # Convert task_tree to dict if it exists
            task_tree_dict = None
            if self.task_tree:
                task_tree_dict = asdict(self.task_tree)
            
            # Update the state with the latest task tree
            self.state.task_tree = task_tree_dict
            self.state.last_executed = datetime.datetime.now().isoformat()
            
            # Save to file
            with open(self.state_file, "w") as f:
                json.dump(asdict(self.state), f, indent=2)
                print(f"Project state saved to {self.state_file}")

    def load_state(self) -> bool:
        """Load project state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r") as f:
                    state_data = json.load(f)
                    
                    # Initialize ProjectState from dict
                    self.state = ProjectState(
                        user_prompt=state_data.get("user_prompt", ""),
                        structured_prompt=state_data.get("structured_prompt"),
                        task_tree=state_data.get("task_tree"),
                        completed_tasks=set(state_data.get("completed_tasks", [])),
                        error_tasks=state_data.get("error_tasks", {}),
                        last_executed=state_data.get("last_executed")
                    )
                    
                    print(f"Project state loaded from {self.state_file}")
                    print(f"Last execution: {self.state.last_executed}")
                    print(f"Completed tasks: {len(self.state.completed_tasks)}")
                    print(f"Error tasks: {len(self.state.error_tasks)}")
                    return True
        except Exception as e:
            print(f"Error loading project state: {str(e)}")
        return False

    def update_task_status(self, task: Task, task_id: str, status: str, error_message: str = None):
        """Update the status of a task by ID"""
        if task.task_id == task_id:
            task.status = status
            if error_message:
                task.error_message = error_message
            return True
            
        for subtask in task.subtasks:
            if self.update_task_status(subtask, task_id, status, error_message):
                return True
                
        return False

    def generate_code(self, task: Task) -> str:
        """Generate code using OlympicCoder with status tracking"""
        # Skip if task already completed
        if task.status == "completed" and task.task_id in self.state.completed_tasks:
            print(f"Skipping completed task: {task.name}")
            return ""
            
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
        
        try:
            code = self.call_model(prompt, "coding", temperature=0.1)
            # Mark task as completed
            self.update_task_status(self.task_tree, task.task_id, "completed")
            if self.state:
                self.state.completed_tasks.add(task.task_id)
            return code
        except Exception as e:
            error_msg = f"Code generation error: {str(e)}"
            print(error_msg)
            # Mark task as error
            self.update_task_status(self.task_tree, task.task_id, "error", error_msg)
            if self.state:
                self.state.error_tasks[task.task_id] = error_msg
            return ""

    def find_pending_tasks(self, task: Task) -> List[Task]:
        """Find all pending tasks with file paths"""
        result = []
        
        if task.status == "pending" and task.file_path:
            result.append(task)
        
        for subtask in task.subtasks:
            result.extend(self.find_pending_tasks(subtask))
            
        return result

    def build_project(self, root_task: Task):
        """Create project structure and files with progress tracking"""
        # Find pending tasks
        pending_tasks = self.find_pending_tasks(root_task)
        print(f"Found {len(pending_tasks)} pending tasks to process")
        
        for task in pending_tasks:
            print(f"Processing task: {task.name}")
            if task.file_path:
                path = Path(task.file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                
                if path.suffix == '.py':
                    code = self.generate_code(task)
                    if code:
                        path.write_text(code, encoding="utf-8")
                else:
                    path.touch()
                    
                self.project_structure[task.file_path] = asdict(task)
            
            # Save state after each task
            self.save_state()
            self.save_task_tree()
            
    def fix_code(self, error_message: str, file_path: str) -> str:
        """Generate fixed code based on error message"""
        try:
            # Read existing code
            with open(file_path, "r", encoding="utf-8") as f:
                existing_code = f.read()
                
            prompt = f"""
            Fix this Python code that has the following error:
            {error_message}
            
            Current code:
            {existing_code}
            
            Write the COMPLETE corrected code file, not just the fixed part.
            """
            
            fixed_code = self.call_model(prompt, "coding", temperature=0.1)
            return fixed_code
        except Exception as e:
            print(f"Fix code error: {str(e)}")
            return ""

    def execute_and_debug(self):
        """Run generated code and handle errors"""
        # Save state before execution
        self.save_state()
        
        try:
            result = subprocess.run(["python", "main.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("Project executed successfully!")
                return True
            else:
                print(f"Execution error: {result.stderr}")
                
                # Parse error for file path and line number
                error_lines = result.stderr.splitlines()
                error_file = None
                
                for line in error_lines:
                    if "File " in line:
                        match = re.search(r'File "([^"]+)", line \d+', line)
                        if match:
                            error_file = match.group(1)
                            break
                
                if error_file and os.path.exists(error_file):
                    print(f"Attempting to fix file: {error_file}")
                    fixed_code = self.fix_code(result.stderr, error_file)
                    
                    if fixed_code:
                        with open(error_file, "w", encoding="utf-8") as f:
                            f.write(fixed_code)
                        print(f"Fixed code written to {error_file}")
                        
                        # Update task status
                        for file_path, task_data in self.project_structure.items():
                            if file_path == error_file:
                                self.update_task_status(
                                    self.task_tree, 
                                    task_data.get("task_id"), 
                                    "completed"
                                )
                                if task_data.get("task_id") in self.state.error_tasks:
                                    del self.state.error_tasks[task_data.get("task_id")]
                                break
                        
                        # Save updated state
                        self.save_state()
                        self.save_task_tree()
                        
                        # Try execution again
                        return self.execute_and_debug()
                        
                return False
                
        except subprocess.TimeoutExpired:
            print("Execution timed out")
            return False
        except Exception as e:
            print(f"Execution error: {str(e)}")
            return False

    def run_pipeline(self, user_prompt: str):
        """End-to-end project generation workflow with state management"""
        # Initialize or load project state
        if self.load_state():
            print("Resuming project from saved state")
            # Load task tree if state exists but task tree not loaded
            if not self.task_tree and self.state.task_tree:
                self.task_tree = self._build_task_from_data(self.state.task_tree)
            elif not self.task_tree:
                self.task_tree = self.load_task_tree()
        else:
            print("Starting new project")
            self.state = ProjectState(user_prompt=user_prompt)
            self.save_state()
            
        # Parse prompt if needed
        if not self.state.structured_prompt:
            structured_prompt = self.parse_prompt(user_prompt)
            self.state.structured_prompt = structured_prompt
            self.save_state()
        else:
            structured_prompt = self.state.structured_prompt
            
        # Decompose task if needed
        if not self.task_tree:
            self.task_tree = self.decompose_task(structured_prompt)
            self.task_tree = self.rebuild_task_tree(self.task_tree)
            self.save_task_tree()
            self.save_state()
            
        # Print task tree for debugging
        print("\n=== Task Tree Structure ===")
        self.print_task_tree(self.task_tree)
        print("==========================\n")
        
        # Build project (processes pending tasks only)
        self.build_project(self.task_tree)
        
        # Save project metadata
        with open("README.md", "w") as f:
            f.write(f"# AI Generated Project\n\n")
            f.write(f"Original prompt: {user_prompt}\n\n")
            f.write(f"## Project Structure\n\n")
            for file_path in self.project_structure:
                f.write(f"- {file_path}\n")
            
        # Execute and debug
        success = self.execute_and_debug()
        print(f"Project execution {'successful' if success else 'failed'}")
        
        # Final state save
        self.save_state()
        self.save_task_tree()

# Example usage
if __name__ == "__main__":
    generator = ProjectGenerator()
    user_input = "Create a REST API for Fibonacci sequence with FastAPI"
    generator.run_pipeline(user_input)