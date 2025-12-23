import express from 'express';
import dotenv from 'dotenv';
import cookieParser from 'cookie-parser';
import morgan from 'morgan';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import session from 'express-session';
import MongoStore from 'connect-mongo';

dotenv.config();

function app() {
    const app = express();

    // Security headers middleware
    app.use(helmet());

    // Request logging middleware
    app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));

    // Rate limiting middleware
    const limiter = rateLimit({
        windowMs: 15 * 60 * 1000,
        max: 100,
        standardHeaders: true,
        legacyHeaders: false,
    });
    app.use(limiter);

    // Body parsing middleware
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));

    // Cookie parsing middleware
    app.use(cookieParser());

    // Static file serving
    app.use(express.static('public'));

    // Database connection initialization
    import('./database.js').then(({ initializeDatabase }) => {
        initializeDatabase();
    }).catch(err => {
        console.error('Database module import failed:', err);
        process.exit(1);
    });

    // Session configuration
    const sessionConfig = {
        secret: process.env.SESSION_SECRET,
        resave: false,
        saveUninitialized: false,
        store: MongoStore.create({
            mongoUrl: process.env.MONGO_URI,
            ttl: 24 * 60 * 60,
        }),
        cookie: {
            secure: process.env.NODE_ENV === 'production',
            httpOnly: true,
            maxAge: 24 * 60 * 60 * 1000,
        }
    };
    app.use(session(sessionConfig));

    // Error handling middleware
    app.use((err, req, res, next) => {
        console.error(err.stack);
        res.status(500).json({ error: 'Internal Server Error' });
    });

    return app;
}

export default app;

Server running on port ${port}