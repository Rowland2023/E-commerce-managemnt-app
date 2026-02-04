// routes/employeeRoutes.js
import express from "express";
import employeeController from "../controller/employeeController.js";
import authMiddleware from "./Middleware/authMiddleware.js";

const router = express.Router();

router.use(authMiddleware);

router.get("/", employeeController.getAllEmployee);
router.post("/", employeeController.createEmployee);
router.get("/:id", employeeController.getEmployeeById);
router.put("/:id", employeeController.updateEmployee);
router.delete("/:id", employeeController.deleteEmployee);

export default router;
