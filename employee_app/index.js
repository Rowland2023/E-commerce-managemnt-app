import 'dotenv/config'; 
import express from 'express';
import cors from 'cors';
import sequelize from './config/database.js'; 

// IMPORTANT: Models must be imported before sequelize.sync() is called
// so that Sequelize knows which tables to create in Postgres.
import Employee from './models/employee.js';  
import Department from './models/department.js';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json()); 
app.use(express.urlencoded({ extended: true }));

// --- HEALTH CHECKS ---
app.get('/', (req, res) => {
  res.json({ status: "success", message: "Employee API is live" });
});

app.get('/health', (req, res) => {
    res.status(200).send('OK');
});

const startServer = async () => {
  try {
    console.log('⏳ Connecting to Database...');
    await sequelize.authenticate();
    
    console.log('⏳ Syncing Database Models...');
    // force: true drops existing tables and recreates them based on the imported models
    await sequelize.sync({ force: true }); 
    console.log('✅ Database synchronized.');

    // Dynamic Imports for Controllers
    const { default: authRouter } = await import('./controller/authController.js');
    const { default: employeeRouter } = await import('./controller/employeeController.js');
    const { default: departmentRouter } = await import('./controller/departmentController.js');
    const { default: authMiddleware } = await import('./Middleware/authMiddleware.js');

    // 1. Official Versioned API Routes (Optional: commented out for now)
    // app.use('/api/v1/auth', authRouter);
    // app.use('/api/v1/employees', authMiddleware, employeeRouter);

    // 2. Short-URL Aliases (Matching your Nginx config and Admin links)
    app.use('/employee', employeeRouter);
    app.use('/department', departmentRouter);
    app.use('/auth', authRouter);

    app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 Server is listening on port ${PORT}`);
    });

  } catch (error) {
    console.error('❌ Startup Error:', error.message);
    // Retry connection after 5 seconds if DB is not ready
    setTimeout(startServer, 5000);
  }
};

startServer();