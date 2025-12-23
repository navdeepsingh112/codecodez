import { requireAuth } from '../middleware/authMiddleware';

/**
 * Protected route handler for dashboard data
 * 
 * @param {import('express').Request} req - Express request object with authenticated user
 * @param {import('express').Response} res - Express response object
 * @returns {void} Sends response with dashboard data or error
 */
async function getDashboard(req, res) {
    try {
        // Access authenticated user from request
        const user = req.user;
        if (!user) {
            return res.status(401).json({ error: 'Unauthorized: User not authenticated' });
        }

        // Fetch dashboard data (example implementation)
        const dashboardData = {
            userId: user.id,
            username: user.username,
            stats: { logins: 24, activities: 89 },
            recentActivity: [
                { id: 1, action: 'Profile update', timestamp: new Date() },
                { id: 2, action: 'Document upload', timestamp: new Date() }
            ]
        };

        // Send successful response with dashboard data
        res.status(200).json(dashboardData);
    } catch (error) {
        console.error('Dashboard error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}