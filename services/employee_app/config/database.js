// database.js
import { Sequelize } from 'sequelize';
import dotenv from 'dotenv';

// Load environment variables depending on NODE_ENV
const envFile = `.env.${process.env.NODE_ENV || 'development'}`;
dotenv.config({ path: envFile });

// Create a new Sequelize instance using env variables
const sequelize = new Sequelize(
  process.env.DB_NAME,     // database name
  process.env.DB_USER,     // database username
  process.env.DB_PASSWORD, // database password
  {
    host: process.env.DB_HOST, // database host (should be 'db' in Docker)
    port: process.env.DB_PORT || 5432, // Added port for Postgres
    dialect: 'postgres',       // CHANGED: from 'mysql' to 'postgres'
    logging: false,            // disable SQL query logging
    dialectOptions: {
      // Optional: Helps with some Postgres versions/hosting
      connectTimeout: 60000 
    }
  }
);



export default sequelize;