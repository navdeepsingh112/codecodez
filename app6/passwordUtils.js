import bcrypt from 'bcrypt';
import dotenv from 'dotenv';

dotenv.config();

const SALT_ROUNDS = parseInt(process.env.SALT_ROUNDS) || 10;

/**
 * Hashes a plain text password using bcrypt.
 * 
 * @param {string} plainText - The plain text password to hash.
 * @returns {Promise<string>} A promise that resolves to the hashed password.
 * @throws {Error} If hashing fails or input is invalid.
 */
async function hashPassword(plainText) {
    if (!plainText || typeof plainText !== 'string') {
        throw new Error('Invalid input: plainText must be a non-empty string');
    }
    
    try {
        return await bcrypt.hash(plainText, SALT_ROUNDS);
    } catch (error) {
        throw new Error(`Password hashing failed: ${error.message}`);
    }
}

/**
 * Compares a plain text password with a bcrypt hash.
 * 
 * @param {string} plainText - The plain text password to verify.
 * @param {string} hash - The hashed password to compare against.
 * @returns {Promise<boolean>} A promise that resolves to true if passwords match, false otherwise.
 * @throws {Error} If comparison fails or inputs are invalid.
 */
async function comparePassword(plainText, hash) {
    if (!plainText || typeof plainText !== 'string' || !hash || typeof hash !== 'string') {
        throw new Error('Invalid inputs: Both plainText and hash must be non-empty strings');
    }
    
    try {
        return await bcrypt.compare(plainText, hash);
    } catch (error) {
        throw new Error(`Password comparison failed: ${error.message}`);
    }
}

export { hashPassword, comparePassword };