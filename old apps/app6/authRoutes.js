import express from 'express';
import rateLimit from 'express-rate-limit';
import { body } from 'express-validator';
import { registerUser, loginUser, logoutUser } from '../controllers/authController.js';

const router = express.Router();

// Rate limiter configuration for authentication endpoints
const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      message: 'Too many requests, please try again later'
    });
  }
});

// User registration route with validation and rate limiting
router.post(
  '/register',
  authRateLimiter,
  [
    body('email')
      .isEmail().withMessage('Valid email is required')
      .normalizeEmail(),
    body('password')
      .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
      .matches(/[0-9]/).withMessage('Password must contain a number')
      .matches(/[a-z]/).withMessage('Password must contain a lowercase letter')
      .matches(/[A-Z]/).withMessage('Password must contain an uppercase letter'),
    body('name')
      .trim()
      .notEmpty().withMessage('Name is required')
  ],
  registerUser
);

// User login route with validation and rate limiting
router.post(
  '/login',
  authRateLimiter,
  [
    body('email')
      .isEmail().withMessage('Valid email is required')
      .normalizeEmail(),
    body('password')
      .notEmpty().withMessage('Password is required')
  ],
  loginUser
);

// User logout route
router.post('/logout', logoutUser);

export default router;