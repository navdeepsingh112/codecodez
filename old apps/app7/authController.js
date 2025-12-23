import User from '../models/User';
import bcrypt from 'bcrypt';
import validator from 'validator';

/**
 * Controller for user registration
 * @async
 * @function registerUser
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next middleware function
 * @returns {Promise<void>}
 */
async function registerUser(req, res, next) {
    try {
        const { username, email, password } = req.body;

        // Validate required fields
        if (!username || !email || !password) {
            return res.status(400).json({ error: 'All fields are required' });
        }

        // Validate email format
        if (!validator.isEmail(email)) {
            return res.status(400).json({ error: 'Invalid email format' });
        }

        // Validate password strength
        if (!validator.isStrongPassword(password, { 
            minLength: 8, 
            minLowercase: 1, 
            minUppercase: 1, 
            minNumbers: 1, 
            minSymbols: 1 
        })) {
            return res.status(400).json({ 
                error: 'Password must be at least 8 characters with uppercase, lowercase, number, and symbol' 
            });
        }

        // Check for existing user
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
            return res.status(409).json({ error: 'Email or username already in use' });
        }

        // Create new user instance
        const newUser = new User({ username, email, password });

        // Save user (password hashing handled by pre-save hook in model)
        const savedUser = await newUser.save();

        // Set session
        req.session.userId = savedUser._id;

        // Prepare response without password
        const userResponse = savedUser.toObject();
        delete userResponse.password;

        res.status(201).json({ user: userResponse });
    } catch (error) {
        // Handle duplicate key error from MongoDB
        if (error.code === 11000) {
            return res.status(409).json({ error: 'Email or username already in use' });
        }
        // Handle validation errors
        if (error.name === 'ValidationError') {
            return res.status(400).json({ error: error.message });
        }
        // Pass other errors to error handler
        next(error);
    }
}

export default registerUser;

import User from '../models/User';

/**
 * Controller for user authentication with session creation
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next middleware function
 * @returns {Promise<void>}
 */
async function loginUser(req, res, next) {
    const { identifier, password } = req.body;
    
    // Validate required fields
    if (!identifier || !password) {
        return res.status(400).json({ message: 'Identifier and password are required' });
    }

    try {
        // Find user by email or username
        const user = await User.findOne({
            $or: [{ email: identifier }, { username: identifier }]
        });

        if (!user) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Check account lock status
        if (user.isLocked && user.lockUntil > Date.now()) {
            return res.status(403).json({ 
                message: 'Account locked. Try again after ' + 
                new Date(user.lockUntil).toLocaleTimeString() 
            });
        }

        // Verify password
        const isMatch = await user.comparePassword(password);
        if (!isMatch) {
            // Increment failed attempts and lock if threshold reached
            user.loginAttempts += 1;
            if (user.loginAttempts >= 5) {
                user.isLocked = true;
                user.lockUntil = Date.now() + 24 * 60 * 60 * 1000; // 24-hour lock
            }
            await user.save();
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Reset security fields on successful login
        user.loginAttempts = 0;
        if (user.isLocked) {
            user.isLocked = false;
            user.lockUntil = null;
        }
        await user.save();

        // Regenerate session to prevent fixation
        await new Promise((resolve, reject) => {
            req.session.regenerate((err) => {
                if (err) reject(err);
                else resolve();
            });
        });

        // Establish new session
        req.session.userId = user._id;
        await new Promise((resolve, reject) => {
            req.session.save((err) => {
                if (err) reject(err);
                else resolve();
            });
        });

        // Return user data without sensitive fields
        const userData = user.toObject();
        delete userData.password;
        delete userData.loginAttempts;
        delete userData.isLocked;
        delete userData.lockUntil;

        res.status(200).json({ user: userData });
        
    } catch (err) {
        next(err);
    }
}

export default loginUser;

import { Request, Response, NextFunction } from 'express';

/**
 * Controller to terminate user session
 * 
 * @param {Request} req - Express request object containing session information
 * @param {Response} res - Express response object for sending responses
 * @param {NextFunction} next - Express next function for error handling
 * @returns {void}
 */
function logoutUser(req, res, next) {
    // Capture session cookie details before destruction
    const sessionCookie = req.session.cookie;
    const cookieOptions = {
        domain: sessionCookie.domain,
        path: sessionCookie.path,
        sameSite: sessionCookie.sameSite,
        secure: sessionCookie.secure,
        httpOnly: sessionCookie.httpOnly
    };

    // Destroy current session
    req.session.destroy((err) => {
        if (err) {
            return next(err);
        }
        
        // Clear session cookie using captured options
        res.clearCookie(sessionCookie.name, cookieOptions);
        
        // Send 204 No Content response
        res.sendStatus(204);
    });
}

import User from '../models/User';
import createError from 'http-errors';
import validator from 'validator';

/**
 * Handles user registration with validation and password hashing
 * @async
 * @function registerUser
 * @param {object} req - Express request object
 * @param {object} res - Express response object
 * @param {function} next - Express next middleware function
 * @returns {Promise<void>} Sends response or passes error to next middleware
 */
const registerUser = async (req, res, next) => {
    try {
        const { username, email, password } = req.body;

        // Validate required fields
        if (!username || !email || !password) {
            throw createError.BadRequest('Username, email, and password are required');
        }

        // Validate and sanitize inputs
        if (!validator.isEmail(email)) {
            throw createError.BadRequest('Invalid email format');
        }
        const sanitizedEmail = validator.normalizeEmail(email);
        const sanitizedUsername = validator.escape(username.trim());

        // Check for existing user
        const existingUser = await User.findOne({ 
            $or: [{ email: sanitizedEmail }, { username: sanitizedUsername }] 
        });
        if (existingUser) {
            if (existingUser.email === sanitizedEmail) {
                throw createError.Conflict('Email already registered');
            }
            throw createError.Conflict('Username already taken');
        }

        // Create and save new user
        const newUser = new User({
            username: sanitizedUsername,
            email: sanitizedEmail,
            password  // Password hashing handled in User model pre-save hook
        });

        const savedUser = await newUser.save();

        // Prepare response without password
        const userResponse = savedUser.toObject();
        delete userResponse.password;

        res.status(201).json(userResponse);
    } catch (error) {
        next(error);
    }
};

export default registerUser;

import { body, validationResult } from 'express-validator';
import User from '../models/User';
import bcrypt from 'bcrypt';

/**
 * Handles user registration with validation and duplicate checks
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @returns {Promise<import('express').Response>} Response object with status and JSON data
 */
async function registerUser(req, res) {
    // Validate input using express-validator
    await body('email').isEmail().normalizeEmail().run(req);
    await body('password').isStrongPassword({
        minLength: 8,
        minLowercase: 1,
        minUppercase: 1,
        minNumbers: 1,
        minSymbols: 1
    }).run(req);

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ 
            message: 'Validation failed',
            errors: errors.array() 
        });
    }

    const { email, password } = req.body;

    try {
        // Check for existing user
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(409).json({ message: 'Email already registered' });
        }

        // Hash password
        const saltRounds = 10;
        const hashedPassword = await bcrypt.hash(password, saltRounds);

        // Create and save new user
        const newUser = new User({
            email,
            password: hashedPassword
        });

        await newUser.save();

        return res.status(201).json({ 
            message: 'User registered successfully',
            userId: newUser._id 
        });
    } catch (error) {
        console.error('Registration error:', error);
        
        // Handle Mongoose validation errors
        if (error.name === 'ValidationError') {
            return res.status(400).json({ 
                message: 'Validation error',
                errors: Object.values(error.errors).map(err => err.message) 
            });
        }

        // Handle duplicate key error (fallback)
        if (error.code === 11000) {
            return res.status(409).json({ message: 'Email already exists' });
        }

        return res.status(500).json({ message: 'Internal server error' });
    }
}

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import User from '../models/User.js';

/**
 * Authenticates user and generates JWT token
 * @async
 * @function loginUser
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @returns {Promise<Response>} JSON response with user data and token
 */
export const loginUser = async (req, res) => {
    try {
        const { email, password } = req.body;

        // Validate input fields
        if (!email || !password) {
            return res.status(400).json({ message: 'Email and password are required' });
        }

        // Find user by email
        const user = await User.findOne({ email }).select('+password');
        if (!user) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Compare hashed password
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Generate JWT token
        const token = jwt.sign(
            { userId: user._id },
            process.env.JWT_SECRET,
            { expiresIn: '1h' }
        );

        // Set secure HTTP-only cookie
        res.cookie('token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 3600000 // 1 hour
        });

        // Return user data (excluding password) and token
        const { password: _, ...userData } = user.toObject();
        return res.status(200).json({ user: userData, token });
        
    } catch (error) {
        console.error('Login error:', error);
        return res.status(500).json({ message: 'Internal server error' });
    }
};