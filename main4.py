import os
import json
import subprocess
import re
from json import JSONDecodeError
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
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
    "X-Title": "Universal AI Project Builder"
}

MODEL_CONFIG = {
    "reasoning": "deepseek/deepseek-r1-0528:free",
    "language": "deepseek/deepseek-r1-0528:free",
    "coding": "deepseek/deepseek-r1-0528:free"
}

# Language and framework configurations
LANGUAGE_CONFIG = {
    "python": {
        "file_extensions": [".py"],
        "main_files": ["main.py", "app.py", "run.py", "__init__.py"],
        "package_files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "run_commands": ["python {main_file}", "python -m {module}"],
        "install_commands": ["pip install -r requirements.txt", "pip install -e ."],
        "common_frameworks": ["fastapi", "flask", "django", "streamlit", "tkinter"]
    },
    "javascript": {
        "file_extensions": [".js", ".mjs"],
        "main_files": ["index.js", "main.js", "app.js", "server.js"],
        "package_files": ["package.json", "package-lock.json", "yarn.lock"],
        "run_commands": ["node {main_file}", "npm start", "npm run dev"],
        "install_commands": ["npm install", "yarn install"],
        "common_frameworks": ["express", "react", "vue", "angular", "next"]
    },
    "typescript": {
        "file_extensions": [".ts", ".tsx"],
        "main_files": ["index.ts", "main.ts", "app.ts", "server.ts"],
        "package_files": ["package.json", "tsconfig.json", "package-lock.json"],
        "run_commands": ["ts-node {main_file}", "npm start", "npm run dev"],
        "install_commands": ["npm install", "tsc"],
        "common_frameworks": ["express", "nest", "react", "vue", "angular"]
    },
    "java": {
        "file_extensions": [".java"],
        "main_files": ["Main.java", "App.java", "Application.java"],
        "package_files": ["pom.xml", "build.gradle", "gradle.properties"],
        "run_commands": ["java {main_class}", "mvn exec:java", "gradle run"],
        "install_commands": ["mvn install", "gradle build"],
        "common_frameworks": ["spring", "springboot", "jersey", "struts"]
    },
    "csharp": {
        "file_extensions": [".cs"],
        "main_files": ["Program.cs", "Main.cs", "App.cs"],
        "package_files": [".csproj", "packages.config", "project.json"],
        "run_commands": ["dotnet run", "dotnet {dll_file}"],
        "install_commands": ["dotnet restore", "nuget restore"],
        "common_frameworks": ["aspnet", "blazor", "wpf", "winforms"]
    },
    "go": {
        "file_extensions": [".go"],
        "main_files": ["main.go", "app.go"],
        "package_files": ["go.mod", "go.sum"],
        "run_commands": ["go run {main_file}", "go run ."],
        "install_commands": ["go mod download", "go get"],
        "common_frameworks": ["gin", "echo", "fiber", "gorilla"]
    },
    "rust": {
        "file_extensions": [".rs"],
        "main_files": ["main.rs", "lib.rs"],
        "package_files": ["Cargo.toml", "Cargo.lock"],
        "run_commands": ["cargo run", "rustc {main_file}"],
        "install_commands": ["cargo build"],
        "common_frameworks": ["actix", "warp", "rocket", "axum"]
    },
    "php": {
        "file_extensions": [".php"],
        "main_files": ["index.php", "main.php", "app.php"],
        "package_files": ["composer.json", "composer.lock"],
        "run_commands": ["php {main_file}", "php -S localhost:8000"],
        "install_commands": ["composer install"],
        "common_frameworks": ["laravel", "symfony", "codeigniter", "cakephp"]
    },
    "ruby": {
        "file_extensions": [".rb"],
        "main_files": ["main.rb", "app.rb"],
        "package_files": ["Gemfile", "Gemfile.lock", "gemspec"],
        "run_commands": ["ruby {main_file}", "bundle exec ruby {main_file}"],
        "install_commands": ["bundle install", "gem install"],
        "common_frameworks": ["rails", "sinatra", "hanami", "grape"]
    },
    "html": {
        "file_extensions": [".html", ".htm"],
        "main_files": ["index.html", "main.html", "app.html"],
        "package_files": ["package.json"],
        "run_commands": ["open {main_file}", "live-server"],
        "install_commands": [],
        "common_frameworks": ["bootstrap", "bulma", "tailwind"]
    },
    "css": {
        "file_extensions": [".css", ".scss", ".sass", ".less"],
        "main_files": ["style.css", "main.css", "app.css"],
        "package_files": ["package.json"],
        "run_commands": [],
        "install_commands": ["npm install"],
        "common_frameworks": ["bootstrap", "tailwind", "bulma"]
    }
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
    language: str = None
    framework: str = None

class UniversalProjectGenerator:
    def __init__(self):
        self.task_tree = None
        self.project_structure = {}
        self.app_directory = "./app/"
        self.detected_language = None
        self.detected_framework = None
        self.language_config = None
        
    def call_model(self, prompt: str, model: str, temperature=0.7) -> str:
        """Generic OpenRouter API caller"""
        global I, OPENROUTER_API_KEY
        try:
            print(model, 'called')
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

    def detect_language_and_framework(self, user_prompt: str) -> tuple:
        """Detect programming language and framework from user prompt"""
        prompt = f"""
        Analyze this project requirement and determine:
        1. Primary programming language
        2. Framework (if any)
        3. Project type (web app, API, desktop app, mobile app, etc.)
        
        User request: {user_prompt}
        
        Available languages: {', '.join(LANGUAGE_CONFIG.keys())}
        
        Respond in JSON format:
        {{
            "language": "detected_language",
            "framework": "detected_framework_or_null",
            "project_type": "project_type",
            "reasoning": "brief_explanation"
        }}
        """
        
        response = self.call_model(prompt, "language", temperature=0.3)
        try:
            result = json.loads(response.strip())
            language = result.get("language", "python").lower()
            framework = result.get("framework", "").lower()
            
            # Validate language
            if language not in LANGUAGE_CONFIG:
                language = "python"  # fallback
                
            return language, framework, result.get("project_type", ""), result.get("reasoning", "")
        except:
            return "python", "", "", "Failed to parse detection response"

    def parse_prompt(self, user_prompt: str) -> str:
        """Use Gemini for language understanding with language context"""
        # Detect language and framework first
        self.detected_language, self.detected_framework, project_type, reasoning = self.detect_language_and_framework(user_prompt)
        self.language_config = LANGUAGE_CONFIG[self.detected_language]
        
        print(f"Detected: {self.detected_language} | {self.detected_framework} | {project_type}")
        print(f"Reasoning: {reasoning}")
        
        prompt = f"""
        Clarify and structure this project requirement for {self.detected_language} development:
        {user_prompt}
        
        Context:
        - Language: {self.detected_language}
        - Framework: {self.detected_framework or 'None'}
        - Project Type: {project_type}
        
        Output format:
        - Project purpose
        - Key components
        - Technical requirements specific to {self.detected_language}
        - Framework-specific considerations for {self.detected_framework or 'standard library'}
        - File structure expectations
        - Dependencies and packages needed
        - Edge cases to consider
        """
        return self.call_model(prompt, "language", temperature=0.3)

    def _build_task_from_data(self, task_data_r) -> Task:
        """Build a task tree recursively from task data"""
        try:
            task_data = task_data_r
            if isinstance(task_data, list):
                print(f"Received list response, using first element")
                task_data = {
                    "name": "Parent Task",
                    "description": "Root task container",
                    "subtasks": [],
                    "function_name": None,
                    "parameters": None,
                    "return_type": None,
                    "file_path": "./app/",
                    "language": self.detected_language,
                    "framework": self.detected_framework,
                    "implementation_details": {
                        "TYPE": "folder",
                        "expected_loc": 0,
                        "to_be_coded": False,
                        "logic": [],
                        "example_usage": ""
                    }
                }
                for i in task_data_r:
                    task_data["subtasks"].append(i)
                
            if not isinstance(task_data, dict):
                raise ValueError(f"Expected dict, got {type(task_data)}")
            
            # Process subtasks first
            subtasks = []
            subtask_data_list = task_data.get('subtasks', [])
            
            if isinstance(subtask_data_list, list):
                for subtask_data in subtask_data_list:
                    subtask = self._build_task_from_data(subtask_data)
                    subtasks.append(subtask)
            
            # Create the task with processed subtasks
            task = Task(
                name=str(task_data.get('name', '')),
                description=str(task_data.get('description', '')),
                subtasks=subtasks,
                function_name=task_data.get('function_name'),
                parameters=task_data.get('parameters', {}),
                return_type=task_data.get('return_type'),
                file_path=task_data.get('file_path'),
                language=task_data.get('language', self.detected_language),
                framework=task_data.get('framework', self.detected_framework),
                implementation_details=task_data.get('implementation_details')
            )
            
            return task
            
        except Exception as e:
            print(f"Task creation error: {str(e)}")
            print(f"Problematic data: {task_data}")
            return Task(name="Error", description=str(e), subtasks=[], 
                       language=self.detected_language, framework=self.detected_framework)

    def decompose_task(self, task_description: str, parent_task=None) -> Task:
        """Recursive task decomposition with language-specific context"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get file extensions for the detected language
                extensions = self.language_config["file_extensions"]
                main_ext = extensions[0] if extensions else ".txt"
                
                prompt = f"""
                Break down this {self.detected_language} development task into subtasks with DETAILED implementation specifications.
                
                LANGUAGE CONTEXT:
                - Primary Language: {self.detected_language}
                - Framework: {self.detected_framework or 'Standard library'}
                - File Extension: {main_ext}
                - Common Frameworks: {', '.join(self.language_config['common_frameworks'])}
                
                Follow these rules STRICTLY:
                1. Output ONLY valid JSON
                2. Use double quotes for strings
                3. No markdown formatting
                4. Ensure proper JSON syntax
                5. Each subtask should include complete specifications for {self.detected_language} implementation
                6. For API endpoints, specify EXACT route paths, HTTP methods, parameters, and response formats
                7. All file paths should start with "./app/" directory and use appropriate file extensions
                8. Include language-specific requirements (imports, dependencies, etc.)
                9. Consider framework-specific patterns and conventions
                
                {json.dumps({
                    "current_task": task_description,
                    "parent_task": parent_task.name if parent_task else None,
                    "language": self.detected_language,
                    "framework": self.detected_framework
                })}
                
                Respond EXACTLY in this JSON format with ENHANCED specification fields:
                [ {{
                    "name": "task_name",
                    "description": "detailed_description",
                    "subtasks_necessary": true/false,
                    "function_name": "exact_function_name_or_class_name",
                    "parameters": {{"param1": "type1", "param2": "type2"}},
                    "return_type": "return_type",
                    "file_path": "./app/path/to/file{main_ext}",
                    "language": "{self.detected_language}",
                    "framework": "{self.detected_framework or ''}",
                    "implementation_details": {{
                        "TYPE": "function/file/folder/class/module",
                        "expected_loc": 0,
                        "to_be_coded": true/false,
                        "logic": "Step-by-step algorithm or business logic with {self.detected_language} specific details",
                        "dependencies": ["list", "of", "required", "imports", "or", "packages"],
                        "framework_specifics": "Framework-specific implementation notes",
                        "example_usage": "How to call this function/endpoint in {self.detected_language}"
                    }}
                }} ]
                
                NOTE:
                1. Tasks should be subdivided based on files/modules/classes they are in
                2. For {self.detected_language}, consider language-specific patterns and conventions
                3. Include proper import statements and dependency management
                4. Specify framework-specific setup if using {self.detected_framework}
                5. File paths should use correct extensions for {self.detected_language}
                6. Implementation details should be language and framework aware
                """
                
                response = self.call_model(prompt, "reasoning", temperature=0.2)
                print(response)
                print('printed \n \n \n')
                
                # Clean response before parsing
                cleaned_response = re.sub(r'``````', '', response, flags=re.DOTALL)
                cleaned_response = cleaned_response.strip()
                
                task_data = json.loads(cleaned_response)
                print(task_data)
                
                for idx, task in enumerate(task_data):
                    task['subtasks'] = []
                    if task['subtasks_necessary']:
                        task_data[idx]['subtasks'].append(self.decompose_task(f'{task}', task))
                
                return task_data
                
            except (JSONDecodeError, ValueError) as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to parse model response after {max_retries} attempts: {str(e)}")
                
                print(f"Retry {attempt + 1}/{max_retries} for task decomposition")
                continue

        return Task(name="Error", description="Failed decomposition", subtasks=[],
                   language=self.detected_language, framework=self.detected_framework)

    def rebuild_task_tree(self, root_task: Task) -> Task:
        """DFS function to rebuild the task tree"""
        if not hasattr(root_task, 'subtasks') or not root_task.subtasks:
            return root_task
        
        processed_subtasks = []
        for subtask in root_task.subtasks:
            processed_subtask = self.rebuild_task_tree(subtask)
            processed_subtasks.append(processed_subtask)
        
        root_task.subtasks = processed_subtasks
        return root_task

    def print_task_tree(self, task: Task, indent=0):
        """Helper method to print the task tree for debugging"""
        print(" " * indent + f"- {task.name} [{task.language}/{task.framework}]")
        print(" " * (indent + 2) + f"Description: {task.description[:50]}...")
        print(" " * (indent + 2) + f"Function: {task.function_name}")
        print(" " * (indent + 2) + f"File: {task.file_path}")
        print(" " * (indent + 2) + f"Subtasks: {len(task.subtasks)}")
        
        for subtask in task.subtasks:
            self.print_task_tree(subtask, indent + 4)

    def get_language_specific_syntax(self, language: str) -> Dict[str, str]:
        """Get language-specific syntax patterns"""
        syntax_patterns = {
            "python": {
                "function_def": "def {name}({params}):",
                "class_def": "class {name}:",
                "import": "import {module}",
                "comment": "# {comment}",
                "docstring": '"""\\n{content}\\n"""'
            },
            "javascript": {
                "function_def": "function {name}({params}) {{",
                "class_def": "class {name} {{",
                "import": "import {module} from '{path}';",
                "comment": "// {comment}",
                "docstring": "/**\\n * {content}\\n */"
            },
            "typescript": {
                "function_def": "function {name}({params}): {return_type} {{",
                "class_def": "class {name} {{",
                "import": "import {module} from '{path}';",
                "comment": "// {comment}",
                "docstring": "/**\\n * {content}\\n */"
            },
            "java": {
                "function_def": "public {return_type} {name}({params}) {{",
                "class_def": "public class {name} {{",
                "import": "import {package};",
                "comment": "// {comment}",
                "docstring": "/**\\n * {content}\\n */"
            },
            "csharp": {
                "function_def": "public {return_type} {name}({params}) {{",
                "class_def": "public class {name} {{",
                "import": "using {namespace};",
                "comment": "// {comment}",
                "docstring": "/// <summary>\\n/// {content}\\n/// </summary>"
            },
            "go": {
                "function_def": "func {name}({params}) {return_type} {{",
                "class_def": "type {name} struct {{",
                "import": "import \"{package}\"",
                "comment": "// {comment}",
                "docstring": "// {content}"
            },
            "rust": {
                "function_def": "fn {name}({params}) -> {return_type} {{",
                "class_def": "struct {name} {{",
                "import": "use {module};",
                "comment": "// {comment}",
                "docstring": "/// {content}"
            },
            "php": {
                "function_def": "function {name}({params}) {{",
                "class_def": "class {name} {{",
                "import": "require_once '{file}';",
                "comment": "// {comment}",
                "docstring": "/**\\n * {content}\\n */"
            },
            "ruby": {
                "function_def": "def {name}({params})",
                "class_def": "class {name}",
                "import": "require '{module}'",
                "comment": "# {comment}",
                "docstring": "# {content}"
            }
        }
        return syntax_patterns.get(language, syntax_patterns["python"])

    def clean_code_response(self, code_text: str) -> str:
        """Remove markdown code blocks from generated code"""
        # Remove markdown code blocks
        code_text = re.sub(r'^```\w*\s*', '', code_text, flags=re.MULTILINE)
        code_text = re.sub(r'```$', '', code_text, flags=re.MULTILINE)
        code_text = re.sub(r'</?code>|</?pre>', '', code_text)
        return code_text.strip()

    def generate_code(self, task: Task) -> str:
        """Generate code using language-specific patterns"""
        language = task.language or self.detected_language
        framework = task.framework or self.detected_framework
        syntax = self.get_language_specific_syntax(language)
        
        # Build language-specific context
        lang_context = f"""
        LANGUAGE: {language.upper()}
        FRAMEWORK: {framework or 'Standard library'}
        SYNTAX PATTERNS: {json.dumps(syntax, indent=2)}
        FILE EXTENSION: {self.language_config['file_extensions'][0]}
        """
        
        prompt = f"""
        Write {language} code for this task:
        
        {lang_context}
        
        Task Details:
        Function/Class: {task.function_name}
        Parameters: {task.parameters}
        Returns: {task.return_type}
        Description: {task.description}
        Implementation Details: {task.implementation_details}
        
        Requirements:
        - Write clean, production-ready {language} code
        - Follow {language} conventions and best practices
        - Include appropriate type annotations/hints for {language}
        - Add proper documentation/comments in {language} style
        - Handle common errors appropriately for {language}
        - DO NOT output any markdown code blocks
        - Just give me the clean {language} code without any formatting or explanations
        - If using {framework}, follow framework-specific patterns
        - Include necessary imports/dependencies for {language}
        - Consider this is part of a larger project structure
        
        IMPORTANT: Output only valid {language} code, no markdown, no explanations.
        """
        
        code = self.call_model(prompt, "coding", temperature=0.1)
        return self.clean_code_response(code)

    def update_file_with_code(self, file_path: str, new_code: str, function_name: str = None) -> None:
        """Update a file with new code, language-agnostic"""
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
            
        # Language-specific function replacement logic
        if self.detected_language == "python":
            pattern = r'(?:@[^\n]+\n)*def\s+' + re.escape(function_name) + r'\s*\([^)]*\)[^:]*:(?:\s*"""[\s\S]*?""")?(?:\s*[^\n]+|\s*$)(?:\n(?:[ \t]+[^\n]+|\s*$))*'
        elif self.detected_language in ["javascript", "typescript"]:
            pattern = r'function\s+' + re.escape(function_name) + r'\s*\([^)]*\)[^{]*{[^{}]*(?:{[^{}]*}[^{}]*)*}'
        elif self.detected_language == "java":
            pattern = r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+' + re.escape(function_name) + r'\s*\([^)]*\)[^{]*{[^{}]*(?:{[^{}]*}[^{}]*)*}'
        else:
            # Fallback: just append
            combined_content = current_content + "\n\n" + new_code
            Path(file_path).write_text(combined_content, encoding="utf-8")
            return
            
        if re.search(pattern, current_content, re.DOTALL):
            # Function exists, replace it
            updated_content = re.sub(pattern, new_code, current_content, flags=re.DOTALL)
            Path(file_path).write_text(updated_content, encoding="utf-8")
        else:
            # Function doesn't exist, append it
            combined_content = current_content + "\n\n" + new_code
            Path(file_path).write_text(combined_content, encoding="utf-8")

    def create_project_files(self, root_task: Task):
        """Create language-specific project files"""
        # Create main package/config files
        if self.detected_language == "python":
            self._create_python_files()
        elif self.detected_language in ["javascript", "typescript"]:
            self._create_node_files()
        elif self.detected_language == "java":
            self._create_java_files()
        elif self.detected_language == "csharp":
            self._create_csharp_files()
        elif self.detected_language == "go":
            self._create_go_files()
        elif self.detected_language == "rust":
            self._create_rust_files()
        elif self.detected_language == "php":
            self._create_php_files()
        elif self.detected_language == "ruby":
            self._create_ruby_files()

    def _create_python_files(self):
        """Create Python-specific files"""
        # requirements.txt
        requirements_content = """# Add your dependencies here
requests>=2.28.0
"""
        if self.detected_framework == "fastapi":
            requirements_content += "fastapi>=0.95.0\nuvicorn>=0.21.0\n"
        elif self.detected_framework == "flask":
            requirements_content += "flask>=2.2.0\n"
        elif self.detected_framework == "django":
            requirements_content += "django>=4.1.0\n"
            
        Path(self.app_directory + "requirements.txt").write_text(requirements_content)
        
        # __init__.py
        Path(self.app_directory + "__init__.py").touch()

    def _create_node_files(self):
        """Create Node.js/JavaScript/TypeScript files"""
        package_json = {
            "name": "generated-project",
            "version": "1.0.0",
            "description": "Generated project",
            "main": "index.js" if self.detected_language == "javascript" else "index.ts",
            "scripts": {
                "start": "node index.js" if self.detected_language == "javascript" else "ts-node index.ts",
                "dev": "nodemon"
            },
            "dependencies": {}
        }
        
        if self.detected_framework == "express":
            package_json["dependencies"]["express"] = "^4.18.0"
        elif self.detected_framework == "react":
            package_json["dependencies"]["react"] = "^18.0.0"
            package_json["dependencies"]["react-dom"] = "^18.0.0"
            
        if self.detected_language == "typescript":
            package_json["devDependencies"] = {
                "typescript": "^4.9.0",
                "@types/node": "^18.0.0",
                "ts-node": "^10.9.0"
            }
            
        Path(self.app_directory + "package.json").write_text(json.dumps(package_json, indent=2))

    def _create_java_files(self):
        """Create Java-specific files"""
        if self.detected_framework in ["spring", "springboot"]:
            pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>generated-project</artifactId>
    <version>1.0.0</version>
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.7.0</version>
        </dependency>
    </dependencies>
</project>"""
            Path(self.app_directory + "pom.xml").write_text(pom_content)

    def _create_csharp_files(self):
        """Create C# project files"""
        csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>"""
        if self.detected_framework == "aspnet":
            csproj_content = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.App" />
  </ItemGroup>
</Project>"""
        
        Path(self.app_directory + "Project.csproj").write_text(csproj_content)

    def _create_go_files(self):
        """Create Go project files"""
        go_mod_content = f"""module generated-project

go 1.19
"""
        if self.detected_framework == "gin":
            go_mod_content += """
require github.com/gin-gonic/gin v1.9.0
"""
        elif self.detected_framework == "echo":
            go_mod_content += """
require github.com/labstack/echo/v4 v4.10.0
"""
        
        Path(self.app_directory + "go.mod").write_text(go_mod_content)

    def _create_rust_files(self):
        """Create Rust project files"""
        cargo_toml = """[package]
name = "generated-project"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
        if self.detected_framework == "actix":
            cargo_toml += 'actix-web = "4.0"\ntokio = { version = "1.0", features = ["full"] }\n'
        elif self.detected_framework == "warp":
            cargo_toml += 'warp = "0.3"\ntokio = { version = "1.0", features = ["full"] }\n'
        elif self.detected_framework == "rocket":
            cargo_toml += 'rocket = "0.5"\n'
            
        Path(self.app_directory + "Cargo.toml").write_text(cargo_toml)

    def _create_php_files(self):
        """Create PHP project files"""
        if self.detected_framework == "laravel":
            composer_json = {
                "name": "generated/project",
                "description": "Generated Laravel project",
                "require": {
                    "php": "^8.0",
                    "laravel/framework": "^9.0"
                },
                "autoload": {
                    "psr-4": {
                        "App\\": "app/"
                    }
                }
            }
        else:
            composer_json = {
                "name": "generated/project",
                "description": "Generated PHP project",
                "require": {
                    "php": "^8.0"
                }
            }
            
        Path(self.app_directory + "composer.json").write_text(json.dumps(composer_json, indent=2))

    def _create_ruby_files(self):
        """Create Ruby project files"""
        gemfile_content = """source 'https://rubygems.org'

gem 'bundler'
"""
        if self.detected_framework == "rails":
            gemfile_content += "gem 'rails', '~> 7.0'\n"
        elif self.detected_framework == "sinatra":
            gemfile_content += "gem 'sinatra', '~> 3.0'\n"
            
        Path(self.app_directory + "Gemfile").write_text(gemfile_content)

    def build_project(self, root_task: Task):
        """Create project structure and files for any language"""
        print('\n \n \n ')
        print(asdict(root_task))
        
        # Ensure app directory exists
        Path(self.app_directory).mkdir(parents=True, exist_ok=True)
        
        # Create language-specific project files
        self.create_project_files(root_task)
        
        for task in self._flatten_tasks(root_task):
            print(f"Processing task: {task.name}")
            
            if task.implementation_details and task.implementation_details.get('to_be_coded', False):
                if task.file_path:
                    # Ensure path is within app directory
                    if not task.file_path.startswith("./app/"):
                        file_extension = self.language_config["file_extensions"][0]
                        base_name = os.path.splitext(os.path.basename(task.file_path))[0]
                        task.file_path = os.path.join(self.app_directory, base_name + file_extension)
                    
                    path = Path(task.file_path)
                    
                    # Check if it's a code file
                    if path.suffix in self.language_config["file_extensions"]:
                        code = self.generate_code(task)
                        self.update_file_with_code(task.file_path, code, task.function_name)
                    else:
                        # Create directory or empty file
                        if task.implementation_details.get('TYPE') == 'folder':
                            path.mkdir(parents=True, exist_ok=True)
                        else:
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.touch(exist_ok=True)
                            
                    self.project_structure[task.file_path] = asdict(task)
    
    def _flatten_tasks(self, task: Task) -> List[Task]:
        """Flatten the task tree into a list for easier processing"""
        result = [task]
        for subtask in task.subtasks:
            result.extend(self._flatten_tasks(subtask))
        return result

    def get_execution_commands(self) -> List[str]:
        """Get language-specific execution commands"""
        commands = []
        main_files = self.language_config["main_files"]
        run_commands = self.language_config["run_commands"]
        
        # Find main file
        main_file = None
        for potential_main in main_files:
            potential_path = Path(self.app_directory) / potential_main
            if potential_path.exists():
                main_file = potential_main
                break
        
        if not main_file:
            # Look for any file with appropriate extension
            for ext in self.language_config["file_extensions"]:
                files = list(Path(self.app_directory).glob(f"*{ext}"))
                if files:
                    main_file = files[0].name
                    break
        
        if main_file:
            for cmd_template in run_commands:
                if "{main_file}" in cmd_template:
                    commands.append(cmd_template.format(main_file=main_file))
                elif "{main_class}" in cmd_template:
                    # For Java
                    main_class = os.path.splitext(main_file)[0]
                    commands.append(cmd_template.format(main_class=main_class))
                elif "{dll_file}" in cmd_template:
                    # For C#
                    dll_file = "Project.dll"  # Assuming default
                    commands.append(cmd_template.format(dll_file=dll_file))
                else:
                    commands.append(cmd_template)
        
        return commands

    def install_dependencies(self):
        """Install project dependencies based on language"""
        install_commands = self.language_config.get("install_commands", [])
        
        for cmd in install_commands:
            try:
                print(f"Running: {cmd}")
                result = subprocess.run(cmd.split(), cwd=self.app_directory, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ Successfully ran: {cmd}")
                    break  # Success, no need to try other commands
                else:
                    print(f"✗ Failed: {cmd} - {result.stderr}")
            except Exception as e:
                print(f"✗ Error running {cmd}: {str(e)}")

    def execute_and_debug(self):
        """Run generated code and handle errors for any language"""
        # Install dependencies first
        print("Installing dependencies...")
        self.install_dependencies()
        
        # Get execution commands
        execution_commands = self.get_execution_commands()
        
        if not execution_commands:
            print(f"No execution commands available for {self.detected_language}")
            return
        
        # Try each execution command
        for cmd_template in execution_commands:
            try:
                print(f"Executing: {cmd_template}")
                
                # Handle different command formats
                if isinstance(cmd_template, str):
                    cmd_parts = cmd_template.split()
                else:
                    cmd_parts = cmd_template
                
                result = subprocess.run(cmd_parts, cwd=self.app_directory,
                                       capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("✓ Project executed successfully!")
                    print("Output:", result.stdout)
                    return
                else:
                    print(f"✗ Execution failed: {result.stderr}")
                    
                    # Try to fix errors automatically
                    if result.stderr:
                        self.attempt_error_fix(result.stderr)
                    
            except subprocess.TimeoutExpired:
                print("⚠ Execution timeout - might be a server/long-running process")
                return
            except Exception as e:
                print(f"✗ Execution error: {str(e)}")
                continue
        
        print("All execution attempts failed.")

    def attempt_error_fix(self, error_message: str):
        """Attempt to fix common errors automatically"""
        print(f"Attempting to fix error: {error_message[:200]}...")
        
        fix_prompt = f"""
        Fix this error in a {self.detected_language} project using {self.detected_framework or 'standard library'}:
        
        ERROR: {error_message}
        
        Language: {self.detected_language}
        Framework: {self.detected_framework}
        
        Provide:
        1. Root cause analysis
        2. Specific fix needed
        3. Updated code or configuration
        4. Any missing dependencies
        
        Focus on common issues like:
        - Missing imports/dependencies
        - Syntax errors
        - Configuration issues
        - Framework-specific problems
        """
        
        fix_suggestion = self.call_model(fix_prompt, "reasoning", temperature=0.3)
        print("Fix suggestion:", fix_suggestion)
        
        # This could be extended to automatically apply fixes
        # For now, just display the suggestion

    def run_pipeline(self, user_prompt: str):
        """End-to-end universal project generation workflow"""
        # Ensure app directory exists
        Path(self.app_directory).mkdir(parents=True, exist_ok=True)
        
        # Parse and analyze the prompt
        structured_prompt = self.parse_prompt(user_prompt)
        print(f"\nGenerated project structure for {self.detected_language} using {self.detected_framework or 'standard library'}")
        
        # Decompose tasks
        self.task_tree = self.decompose_task(structured_prompt)
        self.task_tree = self._build_task_from_data(self.task_tree)
        
        # Ensure task tree is properly built
        self.task_tree = self.rebuild_task_tree(self.task_tree)
        
        # Print task tree for debugging
        print("\n=== Task Tree Structure ===")
        self.print_task_tree(self.task_tree)
        print("==========================\n")
        
        # Build the project
        self.build_project(self.task_tree)
        
        # Create README with project info
        readme_content = f"""# Generated {self.detected_language.title()} Project

## Project Details
- **Language**: {self.detected_language}
- **Framework**: {self.detected_framework or 'Standard library'}
- **Generated from**: {user_prompt}

## Project Structure
```
{json.dumps(self.project_structure, indent=2)}
```

## How to Run
Language: {self.detected_language}
Commands to try:
{chr(10).join(['- ' + cmd for cmd in self.get_execution_commands()])}

## Installation
Dependencies installation commands:
{chr(10).join(['- ' + cmd for cmd in self.language_config.get('install_commands', [])])}

## Generated Files
{chr(10).join(['- ' + path for path in self.project_structure.keys()])}
"""
        
        with open("README.md", "w") as f:
            f.write(readme_content)
            
        # Try to execute the project
        self.execute_and_debug()

# Example usage
if __name__ == "__main__":
    generator = UniversalProjectGenerator()
    
    # Example prompts for different languages:
    examples = [
        "Create a REST API for Fibonacci sequence with FastAPI",  # Python
        "Build a Express.js web server with user authentication",  # JavaScript
        "Create a Spring Boot microservice for order management",  # Java
        "Build a Go web API with Gin for todo management",  # Go
        "Create a Rust web server using Actix for file upload",  # Rust
        "Build a Laravel API for blog management",  # PHP
        "Create a Rails application for e-commerce",  # Ruby
        "Build a React TypeScript app for task management",  # TypeScript
        "Create an ASP.NET Core API for inventory management"  # C#
    ]
    
    # You can test any of these:
    # user_input = "Create a REST API for Fibonacci sequence with FastAPI"
    user_input = examples[1]
    generator.run_pipeline(user_input)