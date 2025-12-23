import request from 'supertest';
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import app from '../app'; // Adjust path as per your project structure

let mongoServer;

// Setup in-memory database before tests
beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  const mongoUri = mongoServer.getUri();
  await mongoose.connect(mongoUri);
});

// Clear database and disconnect after each test
afterEach(async () => {
  await mongoose.connection.db.dropDatabase();
});

// Cleanup after all tests
afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

describe('Authentication API Tests', () => {
  const validUser = {
    name: 'Test User',
    email: 'test@example.com',
    password: 'Password123'
  };

  describe('POST /api/auth/register', () => {
    it('should register a new user with valid data', async () => {
      const res = await request(app)
        .post('/api/auth/register')
        .send(validUser);
      
      expect(res.statusCode).toEqual(201);
      expect(res.body).toHaveProperty('token');
      expect(res.body).toHaveProperty('userId');
    });

    it('should reject duplicate email registration', async () => {
      // Create first user
      await request(app).post('/api/auth/register').send(validUser);
      
      // Attempt duplicate
      const res = await request(app)
        .post('/api/auth/register')
        .send(validUser);
      
      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error');
    });

    it('should reject invalid input data', async () => {
      const invalidUser = {
        name: 'T',
        email: 'invalid-email',
        password: '123'
      };

      const res = await request(app)
        .post('/api/auth/register')
        .send(invalidUser);
      
      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('errors');
    });
  });

  describe('POST /api/auth/login', () => {
    beforeEach(async () => {
      await request(app).post('/api/auth/register').send(validUser);
    });

    it('should login with valid credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: validUser.email,
          password: validUser.password
        });
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('token');
    });

    it('should reject login with invalid email', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'wrong@example.com',
          password: validUser.password
        });
      
      expect(res.statusCode).toEqual(401);
      expect(res.body).toHaveProperty('error');
    });

    it('should reject login with wrong password', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({
          email: validUser.email,
          password: 'WrongPassword123'
        });
      
      expect(res.statusCode).toEqual(401);
      expect(res.body).toHaveProperty('error');
    });
  });

  describe('GET /api/auth/protected', () => {
    let authToken;

    beforeEach(async () => {
      // Register and login to get token
      await request(app).post('/api/auth/register').send(validUser);
      const loginRes = await request(app)
        .post('/api/auth/login')
        .send({
          email: validUser.email,
          password: validUser.password
        });
      authToken = loginRes.body.token;
    });

    it('should access protected route with valid token', async () => {
      const res = await request(app)
        .get('/api/auth/protected')
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('message', 'Protected content');
    });

    it('should reject access without token', async () => {
      const res = await request(app)
        .get('/api/auth/protected');
      
      expect(res.statusCode).toEqual(401);
      expect(res.body).toHaveProperty('error');
    });

    it('should reject access with invalid token', async () => {
      const res = await request(app)
        .get('/api/auth/protected')
        .set('Authorization', 'Bearer invalidtoken123');
      
      expect(res.statusCode).toEqual(401);
      expect(res.body).toHaveProperty('error');
    });
  });
});