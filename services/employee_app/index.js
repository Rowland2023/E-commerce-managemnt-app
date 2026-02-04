import 'dotenv/config'; 
import express from 'express';
import cors from 'cors';
import sequelize from './config/database.js'; 

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json()); 
app.use(express.urlencoded({ extended: true }));

// 1. Define the Health Check early
app.get('/', (req, res) => {
  res.json({ status: "success", message: "Employee API is live" });
});

// 2. The Startup Wrapper
const startServer = async () => {
  try {
    console.log('⏳ Connecting to Database...');
    await sequelize.authenticate();
    
    // THIS MUST RUN BEFORE WE IMPORT ROUTERS THAT USE MODELS
    console.log('⏳ Syncing Database Models...');
    await sequelize.sync({ alter: true });
    console.log('✅ Database synchronized.');

    // 3. NOW IMPORT THE ROUTERS (Dynamic Import)
    // This prevents them from querying the DB before the sync is done
    // Check these filenames against your actual folder structure!
    const { default: authRouter } = await import('./controller/authController.js'); // Changed from authRouter
    const { default: employeeRouter } = await import('./controller/employeeController.js');
    const { default: departmentRouter } = await import('./controller/departmentController.js');
    const { default: authMiddleware } = await import('./Middleware/authMiddleware.js');

    app.use('/api/v1/auth', authRouter);
    app.use('/api/v1/employee', authMiddleware, employeeRouter);
    app.use('/api/v1/department', authMiddleware, departmentRouter);

    app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 Server is listening on port ${PORT}`);
    });

  } catch (error) {
    console.error('❌ Startup Error:', error.message);
    // Wait 5 seconds and try again instead of crashing nodemon
    setTimeout(startServer, 5000);
  }
};

startServer();