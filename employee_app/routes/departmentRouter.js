// routes/departmentRoutes.js
import express from "express";
import departmentController from "../controller/departmentController.js";
import authMiddleware from "./Middleware/authMiddleware.js";

const router = express.Router();

router.use(authMiddleware);

router.get("/", departmentController.getAllDepartment);
router.post("/", departmentController.createDepartment);
router.get("/:id", departmentController.getDepartmentById);
router.put("/:id", departmentController.updateDepartment);
router.delete("/:id", departmentController.deleteDepartment);

export default router;
