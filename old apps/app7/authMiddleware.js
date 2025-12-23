import User from '../models/User';

/**
 * Middleware to protect routes by checking authentication status.
 * 
 * Steps:
 * 1. Checks if req.session.userId exists
 * 2. If session exists:
 *    a. Fetches user from database by ID
 *    b. Attaches user object to req.user
 *    c. Calls next()
 * 3. If no valid session:
 *    - Clears session cookie
 *    - Sends 401 Unauthorized response
 * 4. Handles database errors with 500 response
 * 
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next function
 * @returns {Promise<void>}
 */
async function requireAuth(req, res, next) {
    // Helper to destroy session and send 401 response
    const destroySessionAndRespond = () => {
        if (!req.session) return res.sendStatus(401);
        
        const cookieName = req.session.cookie.name;
        req.session.destroy(err => {
            if (err) console.error('Session destruction error:', err);
            res.clearCookie(cookieName);
            res.sendStatus(401);
        });
    };

    // Missing session userId
    if (!req.session?.userId) {
        return destroySessionAndRespond();
    }

    try {
        const user = await User.findById(req.session.userId);
        if (!user) return destroySessionAndRespond();
        
        req.user = user;
        next();
    } catch (error) {
        console.error('Authentication error:', error);
        res.sendStatus(500);
    }
}

export default requireAuth;

import jwt from 'jsonwebtoken';
import User from '../models/User.js';

/**
 * Express middleware to protect routes by verifying JWT tokens.
 * 
 * Steps:
 * 1. Extract token from cookies or Authorization header
 * 2. If no token exists, return 401 Unauthorized
 * 3. Verify token using JWT_SECRET
 * 4. Find user by decoded userId
 * 5. If invalid token or user not found, return 401
 * 6. Attach authenticated user to request object
 * 7. Proceed to next middleware
 * 
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next function
 * @returns {void}
 */
async function protect(req, res, next) {
    let token;
    
    // Check cookies first, then Authorization header
    if (req.cookies?.token) {
        token = req.cookies.token;
    } else if (req.headers.authorization?.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        return res.status(401).json({ message: 'Not authorized, no token provided' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.userId).select('-password');
        
        if (!user) {
            return res.status(401).json({ message: 'Not authorized, user not found' });
        }
        
        req.user = user;
        next();
    } catch (error) {
        let message = 'Not authorized, token failed';
        
        if (error instanceof jwt.TokenExpiredError) {
            message = 'Token expired';
        } else if (error instanceof jwt.JsonWebTokenError) {
            message = 'Invalid token';
        }
        
        res.status(401).json({ message });
    }
}