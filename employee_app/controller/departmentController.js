// controller/departmentController.js
import { Router } from 'express';
import Department from '../models/department.js'; // Ensure the path is correct

const router = Router();

router.post('/', async (req, res) => {
  // DEBUG LOG - This will tell us if the body is actually reaching the controller
  console.log("--- INCOMING DEPARTMENT DATA ---");
  console.log("Body:", req.body); 

  try {
    const { name, budgetCode } = req.body;

    // 1. Manual validation check
    if (!name || name.trim() === "") {
      return res.status(400).json({ 
        message: "Department name is required",
        receivedData: req.body // Send this back so you can see what the server saw
      });
    }

    // 2. Create in PostgreSQL
    const newDepartment = await Department.create({
      name: name,
      budgetCode: budgetCode || 'N/A'
    });

    return res.status(201).json(newDepartment);

  } catch (err) {
    console.error("PostgreSQL Error:", err.message);
    return res.status(500).json({ message: "Internal Server Error", error: err.message });
  }
});

export default router;