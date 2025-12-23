import mongoose from 'mongoose';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

/**
 * Establishes a connection to the MongoDB database using Mongoose.
 * 
 * This async function configures and initiates the database connection with error handling.
 * It uses environment variables for configuration and handles connection events:
 * - Logs success message on successful connection
 * - Logs error and exits process on connection failure
 * 
 * @async
 * @function connectDB
 * @returns {void}
 */
async function connectDB() {
    const connectionString = process.env.MONGO_URI;
    
    // Validate connection string exists
    if (!connectionString) {
        console.error('MONGO_URI is not defined in environment variables');
        process.exit(1);
    }

    // Configure connection options
    const options = {
        useNewUrlParser: true,
        useUnifiedTopology: true
    };

    try {
        // Attempt database connection
        await mongoose.connect(connectionString, options);
        console.log('Database connected successfully');
    } catch (error) {
        console.error('Database connection failed:', error.message);
        process.exit(1);
    }

    // Handle connection events
    const db = mongoose.connection;
    db.on('error', (err) => {
        console.error('Database connection error:', err);
        process.exit(1);
    });
}

export default connectDB;