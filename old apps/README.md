# Generated Python Project

## Project Details
- **Language**: python
- **Framework**: fastapi
- **Generated from**: Create a REST API for Fibonacci sequence with FastAPI

## Project Structure
```
{
  "./app\\main.py": {
    "name": "setup_main_app",
    "description": "Create main FastAPI application instance with configuration",
    "subtasks": [],
    "function_name": "app",
    "parameters": {},
    "return_type": "FastAPI",
    "file_path": "./app\\main.py",
    "implementation_details": {
      "TYPE": "application",
      "expected_loc": 20,
      "to_be_coded": true,
      "logic": "1. Import FastAPI and CORS middleware\n2. Create FastAPI instance\n3. Add CORS middleware to allow all origins\n4. Include fibonacci router\n5. Add health check endpoint at /health",
      "dependencies": [
        "fastapi",
        "fastapi.middleware.cors"
      ],
      "framework_specifics": "Use FastAPI() instance creation and router inclusion",
      "example_usage": "app = FastAPI()\napp.include_router(fibonacci.router)"
    },
    "language": "python",
    "framework": "fastapi"
  },
  "./app\\schemas.py": {
    "name": "fibonacci_schemas",
    "description": "Define Pydantic models for request and response",
    "subtasks": [],
    "function_name": "FibonacciRequest, FibonacciResponse",
    "parameters": {},
    "return_type": "BaseModel",
    "file_path": "./app\\schemas.py",
    "implementation_details": {
      "TYPE": "model",
      "expected_loc": 15,
      "to_be_coded": true,
      "logic": "1. Create FibonacciRequest model with 'n' field (positive integer)\n2. Create FibonacciResponse model with 'sequence' field (list of integers)\n3. Add field validation for n (minimum=0, maximum=1000)",
      "dependencies": [
        "pydantic"
      ],
      "framework_specifics": "Use Pydantic BaseModel with Field validation",
      "example_usage": "class FibonacciRequest(BaseModel):\n    n: int = Field(ge=0, le=1000)"
    },
    "language": "python",
    "framework": "fastapi"
  },
  "./app\\utils\\calculations.py": {
    "name": "fibonacci_calculation",
    "description": "Implement iterative Fibonacci sequence generator",
    "subtasks": [],
    "function_name": "calculate_fibonacci",
    "parameters": {
      "n": "int"
    },
    "return_type": "List[int]",
    "file_path": "./app\\utils\\calculations.py",
    "implementation_details": {
      "TYPE": "function",
      "expected_loc": 15,
      "to_be_coded": true,
      "logic": "1. Handle n=0: return empty list\n2. Initialize first two Fibonacci numbers\n3. Iterate from 2 to n to build sequence\n4. Use iterative approach (O(n) time complexity)\n5. Return sequence as list of integers",
      "dependencies": [],
      "framework_specifics": "Pure Python implementation",
      "example_usage": "if n == 0: return []\nsequence = [0, 1][:n]"
    },
    "language": "python",
    "framework": null
  },
  "./app\\dependencies.py": {
    "name": "cache_dependency",
    "description": "Create LRU cache dependency for Fibonacci results",
    "subtasks": [],
    "function_name": "get_fib_cache",
    "parameters": {},
    "return_type": "cachetools.LRUCache",
    "file_path": "./app\\dependencies.py",
    "implementation_details": {
      "TYPE": "dependency",
      "expected_loc": 10,
      "to_be_coded": true,
      "logic": "1. Import cachetools\n2. Create LRUCache with maxsize=128\n3. Return cache instance as dependency",
      "dependencies": [
        "cachetools"
      ],
      "framework_specifics": "FastAPI dependency injection",
      "example_usage": "cache = LRUCache(maxsize=128)\nreturn cache"
    },
    "language": "python",
    "framework": "fastapi"
  },
  "./app\\routers\\fibonacci.py": {
    "name": "fibonacci_router",
    "description": "Create router for Fibonacci endpoint with validation and caching",
    "subtasks": [],
    "function_name": "router",
    "parameters": {},
    "return_type": "APIRouter",
    "file_path": "./app\\routers\\fibonacci.py",
    "implementation_details": {
      "TYPE": "router",
      "expected_loc": 30,
      "to_be_coded": true,
      "logic": "1. Create APIRouter instance\n2. Define POST endpoint at /fibonacci\n3. Use FibonacciRequest model for input validation\n4. Inject cache dependency\n5. Check cache for existing result\n6. Compute sequence if not cached\n7. Store result in cache\n8. Return FibonacciResponse\n9. Handle validation errors with HTTPException\n10. Set max n limit to 1000",
      "dependencies": [
        "fastapi",
        "..schemas",
        "..utils.calculations",
        "..dependencies"
      ],
      "framework_specifics": "FastAPI router with dependency injection",
      "example_usage": "@router.post('/fibonacci')\ndef fib_endpoint(request: FibonacciRequest, cache: dict = Depends(get_fib_cache))"
    },
    "language": "python",
    "framework": "fastapi"
  },
  "./app\\tests\\unit\\test_fibonacci.py": {
    "name": "fibonacci_tests",
    "description": "Implement unit tests for Fibonacci functionality",
    "subtasks": [],
    "function_name": "test_calculate_fibonacci, test_fib_endpoint",
    "parameters": {},
    "return_type": "None",
    "file_path": "./app\\tests\\unit\\test_fibonacci.py",
    "implementation_details": {
      "TYPE": "test",
      "expected_loc": 50,
      "to_be_coded": true,
      "logic": "1. Test calculation function with edge cases (n=0,1,5,10)\n2. Test API endpoint via TestClient\n3. Validate response status codes\n4. Test invalid inputs (negative, string, float)\n5. Test cache functionality\n6. Test n=1000 boundary\n7. Verify response structure\n8. Test unsupported HTTP methods",
      "dependencies": [
        "pytest",
        "fastapi.testclient",
        "..main",
        "..utils.calculations"
      ],
      "framework_specifics": "pytest with FastAPI TestClient",
      "example_usage": "def test_fib_endpoint():\n    response = client.post('/fibonacci', json={'n': 5})"
    },
    "language": "python",
    "framework": "pytest"
  },
  "./app\\requirements.txt": {
    "name": "requirements_file",
    "description": "Create requirements.txt with project dependencies",
    "subtasks": [],
    "function_name": null,
    "parameters": {},
    "return_type": "file",
    "file_path": "./app\\requirements.txt",
    "implementation_details": {
      "TYPE": "configuration",
      "expected_loc": 10,
      "to_be_coded": true,
      "logic": "List all required Python packages with versions",
      "dependencies": [],
      "framework_specifics": "Standard requirements format",
      "example_usage": "fastapi==0.103.0\nuvicorn==0.23.2\ncachetools==5.3.1"
    },
    "language": "text",
    "framework": null
  }
}
```

## How to Run
Language: python
Commands to try:
- python main.py
- python -m {module}

## Installation
Dependencies installation commands:
- pip install -r requirements.txt
- pip install -e .

## Generated Files
- ./app\main.py
- ./app\schemas.py
- ./app\utils\calculations.py
- ./app\dependencies.py
- ./app\routers\fibonacci.py
- ./app\tests\unit\test_fibonacci.py
- ./app\requirements.txt

## Task Breakdown
The project was broken down into the following main tasks:
- Parent Task: Root task container
