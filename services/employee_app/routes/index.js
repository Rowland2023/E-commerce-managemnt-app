import express from 'express';
const router = express.Router();

// POINT THESE TO THE ACTUAL CONTROLLER FILES
import employeeRouter from '../controller/employeeController.js'; 
import departmentRouter from '../controller/departmentController.js';
import authMiddleware from '../Middleware/authMiddleware.js';

router.use('/employee', authMiddleware, employeeRouter);
router.use('/department', authMiddleware, departmentRouter);

export default router;