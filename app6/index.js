import express from 'express';
import dotenv from 'dotenv';
import cookieParser from 'cookie-parser';
import helmet from 'helmet';
import csurf from 'csurf';
import session from 'express-session';
import MongoStore from 'connect-mongo';
import mongoose from 'mongoose';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();

// Configure session storage
const sessionStore = MongoStore.create({
  mongoUrl: process.env.MONGODB_URI,
  collectionName: 'sessions'
});

// Session configuration
const sessionOptions = {
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: sessionStore,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'strict'
  }
};

// Apply middleware
app.use(helmet());
app.use(express.json());
app.use(cookieParser());
app.use(session(sessionOptions));
app.use(csurf({ cookie: true }));

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error('MongoDB connection error:', err));

// Routes
import router from './routes/index.js';
app.use('/', router);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  
  // CSRF token errors
  if (err.code === 'EBADCSRFTOKEN') {
    return res.status(403).json({ 
      error: 'Invalid CSRF token' 
    });
  }

  // General error response
  res.status(500).json({ 
    error: 'Internal Server Error' 
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

import dotenv from 'dotenv';
import process from 'process';

dotenv.config();

const requiredEnvVars = ['MONGODB_URI', 'SESSION_SECRET'];
const config = {
    PORT: parseInt(process.env.PORT || '3000', 10),
    MONGODB_URI: process.env.MONGODB_URI,
    SESSION_SECRET: process.env.SESSION_SECRET,
    BCRYPT_ROUNDS: parseInt(process.env.BCRYPT_ROUNDS || '10', 10)
};

for (const envVar of requiredEnvVars) {
    if (!config[envVar]) {
        throw new Error(`Missing required environment variable: ${envVar}`);
    }
}

if (isNaN(config.PORT) || config.PORT < 1 || config.PORT > 65535) {
    throw new Error('Invalid PORT value. Must be between 1 and 65535');
}

if (isNaN(config.BCRYPT_ROUNDS) || config.BCRYPT_ROUNDS < 1) {
    throw new Error('Invalid BCRYPT_ROUNDS value. Must be a positive integer');
}

export default config;

import helmet from 'helmet';
import csurf from 'csurf';
import cors from 'cors';
import rateLimit from 'express-rate-limit';

// Apply security headers via Helmet
app.use(helmet());

// Configure CORS with origin and credentials support
app.use(cors({
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
}));

// Configure CSRF protection with secure cookies in production
app.use(csurf({
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        httpOnly: true,
        sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax'
    }
}));

// Rate limiting configuration for authentication routes
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: 'Too many requests, please try again later'
});

// Apply rate limiting to authentication endpoints
app.use('/login', authLimiter);
app.use('/register', authLimiter);