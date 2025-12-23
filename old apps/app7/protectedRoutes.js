import { Request, Response } from 'express';

/**
 * Protected route handler that returns user-specific data
 * Requires authentication middleware to be applied to the route
 * @param {Request} req - Express request object with authenticated user
 * @param {Response} res - Express response object
 * @returns {Response} JSON response with user data or error message
 */
function getProtectedData(req, res) {
    try {
        // Check if user information exists in request (set by auth middleware)
        if (!req.user) {
            return res.status(401).json({ 
                success: false,
                message: 'Unauthorized: User information not available' 
            });
        }

        // Return user-specific data with 200 status
        return res.status(200).json({
            success: true,
            data: {
                userId: req.user.id,
                username: req.user.username,
                email: req.user.email,
                // Add other relevant user-specific data here
                message: 'Protected data accessed successfully'
            }
        });
    } catch (error) {
        console.error('Error in getProtectedData:', error);
        return res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
}