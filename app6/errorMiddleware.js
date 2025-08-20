const createHttpError = require('http-errors');

/**
 * Centralized error handling middleware for Express applications.
 * Handles various error types, sets appropriate HTTP status codes,
 * and returns JSON responses while preventing sensitive data leakage.
 * 
 * @param {Error} err - The error object passed to the middleware
 * @param {object} req - Express request object
 * @param {object} res - Express response object
 * @param {function} next - Express next middleware function
 * @returns {void} Sends JSON response with error details
 */
function errorHandler(err, req, res, next) {
    // Initialize status code and message from error or defaults
    let status = err.status || err.statusCode || 500;
    let message = err.message || 'An unexpected error occurred';
    
    // Handle specific error types
    if (err.name === 'ValidationError') {
        // Mongoose validation error
        status = 400;
        message = 'Validation failed: ' + Object.values(err.errors).map(e => e.message).join(', ');
    } else if (err.name === 'NotFoundError') {
        status = 404;
        message = 'Resource not found';
    } else if (err.name === 'UnauthorizedError') {
        status = 401;
        message = 'Authentication required';
    } else if (err.code === 11000) {
        // MongoDB duplicate key error
        status = 409;
        const key = Object.keys(err.keyPattern)[0];
        message = `Duplicate value detected for field: ${key}`;
    } else if (err instanceof createHttpError.HttpError) {
        // Handle http-errors package instances
        status = err.status;
        message = err.message;
    }
    
    // Obfuscate 500 errors in production
    if (status >= 500 && process.env.NODE_ENV === 'production') {
        message = 'Internal Server Error';
    }
    
    // Error logging
    if (process.env.NODE_ENV === 'development') {
        console.error(`[${new Date().toISOString()}] Error:`, {
            message: err.message,
            status: status,
            stack: err.stack,
            path: req.path,
            method: req.method
        });
    } else {
        console.error(`[${new Date().toISOString()}] ${status} - ${message}`, {
            path: req.path,
            method: req.method
        });
    }
    
    // Send error response
    const response = { message };
    if (process.env.NODE_ENV === 'development') {
        response.stack = err.stack;
        response.type = err.name;
    }
    
    res.status(status).json(response);
}

module.exports = errorHandler;