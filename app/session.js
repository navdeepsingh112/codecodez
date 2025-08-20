import session from 'express-session';
import MongoStore from 'connect-mongo';

/**
 * Configures express-session with secure settings and MongoDB storage.
 * Note: In production, ensure Express app sets 'trust proxy' and uses HTTPS.
 * @returns {import('express-session').SessionOptions} Session configuration object
 * @throws {Error} If required environment variables are missing
 */
function sessionConfig() {
    // Validate required environment variables
    if (!process.env.SESSION_SECRET) {
        throw new Error('SESSION_SECRET environment variable is required');
    }
    if (!process.env.MONGODB_URI) {
        throw new Error('MONGODB_URI environment variable is required');
    }

    const isProduction = process.env.NODE_ENV === 'production';
    const maxAge = process.env.SESSION_MAX_AGE 
        ? parseInt(process.env.SESSION_MAX_AGE, 10) 
        : 24 * 60 * 60 * 1000; // Default: 24 hours

    return {
        secret: process.env.SESSION_SECRET,
        resave: false,
        saveUninitialized: false,
        store: MongoStore.create({
            mongoUrl: process.env.MONGODB_URI,
            collectionName: 'sessions'
        }),
        cookie: {
            secure: isProduction,
            httpOnly: true,
            sameSite: 'strict',
            maxAge: maxAge
        }
    };
}

export default sessionConfig;