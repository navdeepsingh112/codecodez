import { validationResult } from 'express-validator';
import createError from 'http-errors';
import User from '../models/User';
import { hashPassword, comparePassword } from '../utils/passwordUtils';

/**
 * Registers a new user
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next function
 */
async function registerUser(req, res, next) {
    try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            throw createError(400, 'Validation failed', { errors: errors.array() });
        }

        const { email, password } = req.body;
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            throw createError(409, 'Email already exists');
        }

        const hashedPassword = await hashPassword(password);
        const newUser = new User({ email, password: hashedPassword });
        const savedUser = await newUser.save();

        req.session.userId = savedUser._id;
        req.session.email = savedUser.email;

        res.status(201).json({
            id: savedUser._id,
            email: savedUser.email
        });
    } catch (error) {
        next(error);
    }
}

/**
 * Authenticates an existing user
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next function
 */
async function loginUser(req, res, next) {
    try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            throw createError(400, 'Validation failed', { errors: errors.array() });
        }

        const { email, password } = req.body;
        const user = await User.findOne({ email });
        if (!user) {
            throw createError(401, 'Invalid credentials');
        }

        const isMatch = await comparePassword(password, user.password);
        if (!isMatch) {
            throw createError(401, 'Invalid credentials');
        }

        req.session.userId = user._id;
        req.session.email = user.email;

        res.status(200).json({
            id: user._id,
            email: user.email
        });
    } catch (error) {
        next(error);
    }
}

/**
 * Terminates user session
 * @param {import('express').Request} req - Express request object
 * @param {import('express').Response} res - Express response object
 * @param {import('express').NextFunction} next - Express next function
 */
function logoutUser(req, res, next) {
    try {
        req.session.destroy(err => {
            if (err) {
                throw createError(500, 'Could not log out');
            }
            res.clearCookie('connect.sid');
            res.status(204).end();
        });
    } catch (error) {
        next(error);
    }
}

export { registerUser, loginUser, logoutUser };