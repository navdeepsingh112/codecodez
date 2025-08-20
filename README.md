# Generated Javascript Project

## Project Details
- **Language**: javascript
- **Framework**: express
- **Generated from**: Build a Express.js web server with user authentication

## Project Structure
```
{
  "./app/app.js": {
    "name": "setup_express_server",
    "description": "Initialize Express server with basic configuration and middleware",
    "subtasks": [],
    "function_name": "app",
    "parameters": {},
    "return_type": "ExpressApplication",
    "file_path": "./app/app.js",
    "implementation_details": {
      "TYPE": "configuration",
      "expected_loc": 30,
      "to_be_coded": true,
      "logic": "1. Import express, dotenv, and required middleware packages. 2. Create express instance. 3. Configure dotenv for environment variables. 4. Add middleware: express.json() for body parsing, morgan for logging, helmet for security headers, cors for cross-origin requests. 5. Set default route for health check. 6. Start server listening on configured port.",
      "dependencies": [
        "express",
        "dotenv",
        "morgan",
        "helmet",
        "cors"
      ],
      "framework_specifics": "Use express.json() instead of body-parser. Apply middleware in correct order.",
      "example_usage": "const app = express(); app.use(express.json());"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/database.js": {
    "name": "configure_database",
    "description": "Establish connection to MongoDB database using Mongoose",
    "subtasks": [],
    "function_name": "connectDB",
    "parameters": {},
    "return_type": "void",
    "file_path": "./app/database.js",
    "implementation_details": {
      "TYPE": "function",
      "expected_loc": 20,
      "to_be_coded": true,
      "logic": "1. Import mongoose and dotenv. 2. Retrieve DB_URI from process.env. 3. Use mongoose.connect() with connection options. 4. Handle connection events: log success/error. 5. Export connection function.",
      "dependencies": [
        "mongoose",
        "dotenv"
      ],
      "framework_specifics": "Set mongoose connection options: useNewUrlParser, useUnifiedTopology.",
      "example_usage": "mongoose.connect(process.env.DB_URI, { useNewUrlParser: true, useUnifiedTopology: true });"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/User.js": {
    "name": "create_user_model",
    "description": "Define Mongoose schema and model for User with validation",
    "subtasks": [],
    "function_name": "User",
    "parameters": {},
    "return_type": "MongooseModel",
    "file_path": "./app/User.js",
    "implementation_details": {
      "TYPE": "model",
      "expected_loc": 40,
      "to_be_coded": true,
      "logic": "1. Define schema with fields: username (unique, required), email (unique, required, validate format), password (required, min length). 2. Add pre-save hook to hash password using bcrypt before saving. 3. Add method to compare passwords using bcrypt.compare. 4. Export Mongoose model.",
      "dependencies": [
        "mongoose",
        "bcrypt"
      ],
      "framework_specifics": "Use mongoose Schema and model creation. Apply pre-save middleware.",
      "example_usage": "userSchema.pre('save', async function(next) { if (this.isModified('password')) { this.password = await bcrypt.hash(this.password, 10); } next(); });"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/authController.js": {
    "name": "login_user_controller",
    "description": "Handle user authentication and JWT token generation",
    "subtasks": [],
    "function_name": "loginUser",
    "parameters": {
      "req": "Request",
      "res": "Response"
    },
    "return_type": "Response",
    "file_path": "./app/authController.js",
    "implementation_details": {
      "TYPE": "function",
      "expected_loc": 40,
      "to_be_coded": true,
      "logic": "1. Validate input fields. 2. Find user by email. 3. If not found, return 401. 4. Compare hashed password. 5. If invalid, return 401. 6. Generate JWT token with user ID and expiration. 7. Set secure HTTP-only cookie with token. 8. Return user data (excluding password) and token.",
      "dependencies": [
        "jsonwebtoken",
        "bcrypt",
        "../models/User"
      ],
      "framework_specifics": "Use res.cookie() with secure flags: httpOnly, sameSite. Set JWT expiration.",
      "example_usage": "const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/authMiddleware.js": {
    "name": "auth_middleware",
    "description": "Verify JWT token for protected routes",
    "subtasks": [],
    "function_name": "protect",
    "parameters": {
      "req": "Request",
      "res": "Response",
      "next": "NextFunction"
    },
    "return_type": "void",
    "file_path": "./app/authMiddleware.js",
    "implementation_details": {
      "TYPE": "function",
      "expected_loc": 30,
      "to_be_coded": true,
      "logic": "1. Extract token from cookies/headers. 2. If no token, return 401. 3. Verify token using JWT secret. 4. Find user by decoded ID. 5. If invalid token/user, return 401. 6. Attach user to request object. 7. Call next().",
      "dependencies": [
        "jsonwebtoken",
        "../models/User"
      ],
      "framework_specifics": "Handle token verification errors (expired, malformed). Use express middleware signature.",
      "example_usage": "const decoded = jwt.verify(token, process.env.JWT_SECRET); req.user = await User.findById(decoded.userId);"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/protectedRoutes.js": {
    "name": "protected_route_handler",
    "description": "Example protected route that requires authentication",
    "subtasks": [],
    "function_name": "getProtectedData",
    "parameters": {
      "req": "Request",
      "res": "Response"
    },
    "return_type": "Response",
    "file_path": "./app/protectedRoutes.js",
    "implementation_details": {
      "TYPE": "function",
      "expected_loc": 15,
      "to_be_coded": true,
      "logic": "1. Use authMiddleware to protect route. 2. Access user from req.user. 3. Return user-specific data with 200 status.",
      "dependencies": [
        "express",
        "../middleware/authMiddleware"
      ],
      "framework_specifics": "Apply middleware to route using router.get() with middleware parameter.",
      "example_usage": "router.get('/protected', protect, getProtectedData);"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/errorMiddleware.js": {
    "name": "error_handling_middleware",
    "description": "Centralized error handler for Express application",
    "subtasks": [],
    "function_name": "errorHandler",
    "parameters": {
      "err": "Error",
      "req": "Request",
      "res": "Response",
      "next": "NextFunction"
    },
    "return_type": "Response",
    "file_path": "./app/errorMiddleware.js",
    "implementation_details": {
      "TYPE": "function",
      "expected_loc": 25,
      "to_be_coded": true,
      "logic": "1. Determine status code from error or default to 500. 2. Log error details. 3. Return consistent error response format. 4. Handle specific error types (validation, JWT errors). 5. Avoid leaking sensitive information.",
      "dependencies": [],
      "framework_specifics": "Must be last middleware in chain. Use Express error-handling signature.",
      "example_usage": "const statusCode = err.statusCode || 500; res.status(statusCode).json({ message: err.message });"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/authRoutes.js": {
    "name": "auth_routes",
    "description": "Define authentication-related routes",
    "subtasks": [],
    "function_name": "authRouter",
    "parameters": {},
    "return_type": "Router",
    "file_path": "./app/authRoutes.js",
    "implementation_details": {
      "TYPE": "router",
      "expected_loc": 20,
      "to_be_coded": true,
      "logic": "1. Create Express Router. 2. POST /register route calling registerUser. 3. POST /login route calling loginUser. 4. POST /logout route to clear token cookie. 5. Apply input validation middleware to routes.",
      "dependencies": [
        "express",
        "../controllers/authController",
        "express-validator"
      ],
      "framework_specifics": "Use express.Router(). Apply validation chains as middleware.",
      "example_usage": "router.post('/register', validateRegister, registerUser);"
    },
    "language": "javascript",
    "framework": "express"
  },
  "./app/auth.test.js": {
    "name": "test_auth_flow",
    "description": "Write Jest tests for authentication endpoints",
    "subtasks": [],
    "function_name": "describe",
    "parameters": {},
    "return_type": "void",
    "file_path": "./app/auth.test.js",
    "implementation_details": {
      "TYPE": "tests",
      "expected_loc": 100,
      "to_be_coded": true,
      "logic": "1. Test registration: success, duplicate email, invalid input. 2. Test login: valid credentials, invalid email, wrong password. 3. Test protected route: with valid token, without token, with invalid token. 4. Use supertest to simulate requests. 5. Reset database before each test.",
      "dependencies": [
        "jest",
        "supertest",
        "mongodb-memory-server"
      ],
      "framework_specifics": "Use Jest test structure. Handle async tests properly.",
      "example_usage": "test('POST /register - success', async () => { const res = await request(app).post('/api/auth/register').send({...}); expect(res.statusCode).toEqual(201); });"
    },
    "language": "javascript",
    "framework": "jest"
  },
  "./app/authConfig.js": {
    "name": "configure_environment",
    "description": "Set up environment variables and security configurations",
    "subtasks": [],
    "function_name": "config",
    "parameters": {},
    "return_type": "void",
    "file_path": "./app/authConfig.js",
    "implementation_details": {
      "TYPE": "configuration",
      "expected_loc": 15,
      "to_be_coded": true,
      "logic": "1. Define JWT_SECRET with strong default. 2. Set token expiration time. 3. Configure cookie options: httpOnly, secure (production only), sameSite. 4. Export configurations.",
      "dependencies": [
        "dotenv"
      ],
      "framework_specifics": "Use process.env with fallbacks. Conditionally set secure flags based on NODE_ENV.",
      "example_usage": "const cookieOptions = { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'strict' };"
    },
    "language": "javascript",
    "framework": "express"
  }
}
```

## How to Run
Language: javascript
Commands to try:
- node index.js
- npm start
- npm run dev

## Installation
Dependencies installation commands:
- npm install
- yarn install

## Generated Files
- ./app/app.js
- ./app/database.js
- ./app/User.js
- ./app/authController.js
- ./app/authMiddleware.js
- ./app/protectedRoutes.js
- ./app/errorMiddleware.js
- ./app/authRoutes.js
- ./app/auth.test.js
- ./app/authConfig.js

## Task Breakdown
The project was broken down into the following main tasks:
- Parent Task: Root task container
