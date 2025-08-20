import mongoose from 'mongoose';
import bcrypt from 'bcrypt';

/**
 * User Schema Definition
 * @typedef {Object} UserSchema
 * @property {string} username - Unique username (required)
 * @property {string} email - Unique email address (required, validated format)
 * @property {string} passwordHash - Hashed password (required)
 * @property {Date} createdAt - Timestamp of creation (default: Date.now)
 */
const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: [true, 'Username is required'],
    unique: true,
    trim: true,
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    trim: true,
    lowercase: true,
    validate: {
      validator: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
      message: 'Invalid email format',
    },
  },
  passwordHash: {
    type: String,
    required: [true, 'Password is required'],
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

/**
 * Pre-save hook to hash password before saving
 * @param {Function} next - Mongoose next middleware function
 */
userSchema.pre('save', async function (next) {
  if (!this.isModified('passwordHash')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.passwordHash = await bcrypt.hash(this.passwordHash, salt);
    next();
  } catch (error) {
    next(error);
  }
});

/**
 * Compare plain text password with stored hash
 * @param {string} plainText - Plain text password to compare
 * @returns {Promise<boolean>} Result of password comparison
 */
userSchema.methods.comparePassword = async function (plainText) {
  return bcrypt.compare(plainText, this.passwordHash);
};

/**
 * Find user by credentials for login
 * @param {string} email - User's email address
 * @param {string} password - Plain text password
 * @returns {Promise<import('mongoose').Document>} Found user document
 * @throws {Error} If user not found or password doesn't match
 */
userSchema.statics.findByCredentials = async function (email, password) {
  const user = await this.findOne({ email });
  if (!user) throw new Error('Invalid login credentials');

  const isMatch = await user.comparePassword(password);
  if (!isMatch) throw new Error('Invalid login credentials');

  return user;
};

const User = mongoose.model('User', userSchema);

export default User;