import 'dotenv/config'; 
import express from 'express';
import cors from 'cors';
import sequelize from './config/database.js'; 

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json()); 
app.use(express.urlencoded({ extended: true }));

// --- HEALTH CHECKS ---
// Standard root check
app.get('/', (req, res) => {
  res.json({ status: "success", message: "Employee API is live" });
});

// Docker-specific health check
app.get('/health', (req, res) => {
    res.status(200).send('OK');
});

const startServer = async () => {
  try {
    console.log('⏳ Connecting to Database...');
    await sequelize.authenticate();
    
    console.log('⏳ Syncing Database Models...');
    await sequelize.sync({ force: true });
    console.log('✅ Database synchronized.');

    // Dynamic Imports
    const { default: authRouter } = await import('./controller/authController.js');
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
    setTimeout(startServer, 5000);
  }
};

startServer();