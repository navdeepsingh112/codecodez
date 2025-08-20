import User from '../models/User';
import rateLimit from 'express-rate-limit';
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: false });
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    message: 'Too many authentication attempts, please try again later.'
});

/**
 * Middleware for user authentication, CSRF protection, and rate limiting.
 * Verifies user session, attaches user object to request, validates CSRF token,
 * and enforces rate limits on authenticated endpoints.
 * 
 * @param {object} req - Express request object
 * @param {object} res - Express response object
 * @param {function} next - Next middleware function
 * @returns {void}
 */
function authenticateUser(req, res, next) {
    // Apply rate limiting first to protect against brute-force
    authLimiter(req, res, (limiterError) => {
        if (limiterError) return next(limiterError);
        
        // Verify session exists
        if (!req.session?.userId) {
            return res.status(401).json({ message: 'Unauthorized: No active session' });
        }

        // Fetch user from database
        User.findById(req.session.userId)
            .then(user => {
                if (!user) {
                    return res.status(401).json({ message: 'Unauthorized: User not found' });
                }
                
                // Attach user to request object
                req.user = user;
                
                // Validate CSRF token
                csrfProtection(req, res, (csrfError) => {
                    if (csrfError) {
                        return res.status(403).json({ message: 'Forbidden: Invalid CSRF token' });
                    }
                    next();
                });
            })
            .catch(error => {
                next(error);
            });
    });
}

export default authenticateUser;