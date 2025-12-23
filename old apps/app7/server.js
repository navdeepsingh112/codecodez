import express from 'express';
import dotenv from 'dotenv';
import cookieParser from 'cookie-parser';
import helmet from 'helmet';
import morgan from 'morgan';
import session from 'express-session';

// Load environment variables from .env file
dotenv.config();

/**
 * Initializes and configures an Express application with core middleware.
 * 
 * Steps performed:
 * 1. Creates Express app instance
 * 2. Configures trust proxy for reverse proxy setups
 * 3. Registers essential middleware (JSON parsing, URL encoding, cookies)
 * 4. Sets security headers via Helmet
 * 5. Configures request logging with Morgan
 * 6. Initializes session management with secure settings
 * 7. Serves static files from 'public' directory
 * 8. Adds health check endpoint
 * 
 * @returns {express.Express} Configured Express application instance
 */
function createApp() {
  const app = express();

  // Trust first proxy if behind reverse proxy (e.g., Nginx)
  app.set('trust proxy', 1);

  // Core middleware for request parsing
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  app.use(cookieParser());

  // Security headers
  app.use(helmet());

  // Request logging
  app.use(morgan('dev'));

  // Session configuration
  app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
  }));

  // Static file serving
  app.use(express.static('public'));

  // Health check endpoint
  app.get('/health', (req, res) => res.sendStatus(200));

  return app;
}

export default createApp;