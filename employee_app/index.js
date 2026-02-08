import 'dotenv/config'; 
import express from 'express';
import cors from 'cors';
import sequelize from './config/database.js'; 

// IMPORTANT: Models must be imported before sequelize.sync() is called
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
    console.log('⏳ Authenticating with Database...');
    await sequelize.authenticate();
    console.log('✅ Connection has been established successfully.');

    console.log('⏳ Syncing Database Models...');
    // force: true drops existing tables and recreates them
    await sequelize.sync({ alter: true }); 
    
    // Check if models are actually registered in the Sequelize instance
    console.log('📦 Registered Models:', Object.keys(sequelize.models)); 
    console.log('✅ Database synchronized. Tables created.');

    // Dynamic Imports for Controllers
    const { default: authRouter } = await import('./controller/authController.js');
    const { default: employeeRouter } = await import('./controller/employeeController.js');
    const { default: departmentRouter } = await import('./controller/departmentController.js');
    const { default: authMiddleware } = await import('./Middleware/authMiddleware.js');

    // API Routes & Short-URL Aliases
    app.use('/employee', employeeRouter);
    app.use('/department', departmentRouter);
    app.use('/auth', authRouter);

    app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 Server is listening on port ${PORT}`);
    });

  } catch (error) {
    console.error('❌ Startup Error:', error); // Logs the full error stack for debugging
    // Exponential backoff or simple delay for DB reconnection
    setTimeout(startServer, 5000);
  }
};

startServer();