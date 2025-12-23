import express from 'express';
import { registerUser, loginUser, logoutUser } from '../controllers/authController.js';
import { validateRegister, validateLogin } from '../validators/authValidator.js';

/**
 * Creates and configures the authentication router.
 * Defines routes for user registration, login, and logout with appropriate validation.
 * @returns {express.Router} Configured Express router instance
 */
function authRouter() {
    const router = express.Router();

    // Register route with validation
    router.post('/register', validateRegister, registerUser);
    
    // Login route with validation
    router.post('/login', validateLogin, loginUser);
    
    // Logout route to clear authentication token
    router.post('/logout', logoutUser);

    return router;
}

export default authRouter;