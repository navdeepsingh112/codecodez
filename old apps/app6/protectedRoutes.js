import express from 'express';
import authenticateUser from '../middleware/authMiddleware.js';

const router = express.Router();

// Apply authentication middleware to all routes in this router
router.use(authenticateUser);

/**
 * @route GET /profile
 * @description Fetch authenticated user's profile
 * @access Private
 * @returns {Object} User profile data
 * @throws {401} Unauthorized if authentication fails
 */
router.get('/profile', (req, res) => {
  try {
    // Extract user data from authentication middleware
    const userProfile = {
      id: req.user.id,
      username: req.user.username,
      email: req.user.email,
      role: req.user.role
      // Add other non-sensitive fields as needed
    };
    res.json(userProfile);
  } catch (error) {
    console.error('Profile fetch error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

export default router;