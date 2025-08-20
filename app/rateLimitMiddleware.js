import rateLimit from 'express-rate-limit';

/**
 * Rate limiter middleware for authentication routes.
 * Limits requests to 5 attempts per 15 minutes window.
 * Skips rate limiting for authenticated users (with req.user).
 * 
 * @returns {import('express-rate-limit').RateLimitRequestHandler} Configured rate limiter middleware
 */
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // Limit each IP to 5 requests per window
    message: {
        success: false,
        error: 'Too many attempts, please try again after 15 minutes'
    },
    skip: (req) => req.user, // Skip if user is authenticated
    standardHeaders: true, // Return rate limit info in headers
    legacyHeaders: false // Disable legacy headers
});

export default authLimiter;