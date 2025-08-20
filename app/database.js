import mongoose from 'mongoose';

/**
 * Establishes a connection to the MongoDB database using Mongoose.
 * 
 * This function:
 * 1. Retrieves the database URI from the environment variable DB_URI
 * 2. Sets up event listeners for connection events
 * 3. Attempts to connect to MongoDB with appropriate options
 * 4. Handles connection success and error scenarios
 * 
 * Events handled:
 * - 'connected': Logs successful connection
 * - 'error': Logs error and exits process
 * 
 * @returns {void}
 */
export function connectDB() {
    const DB_URI = process.env.DB_URI;
    
    if (!DB_URI) {
        console.error('DB_URI environment variable is not defined');
        process.exit(1);
    }

    mongoose.connection.on('connected', () => {
        console.log(`MongoDB connected successfully to ${mongoose.connection.host}`);
    });

    mongoose.connection.on('error', (err) => {
        console.error(`MongoDB connection error: ${err.message}`);
        process.exit(1);
    });

    mongoose.connect(DB_URI, {
        useNewUrlParser: true,
        useUnifiedTopology: true
    }).catch(err => {
        console.error(`Mongoose connection error: ${err.message}`);
        process.exit(1);
    });
}

Database connection error: ${err.message}