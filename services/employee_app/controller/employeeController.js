import { Router } from 'express';
import Employee from '../models/employee.js'; 
import sequelize from '../config/database.js';
import axios from 'axios'; 

const router = Router();
const N8N_WEBHOOK_URL = 'https://rowland2026.app.n8n.cloud/webhook-test/employee-event';
const N8N_SECRET_TOKEN = 'your_super_secret_token_123'; 

/**
 * HELPER: Trigger n8n Automation (Non-blocking)
 */
function triggerN8n(employeeData, actionType) {
    // This replaces the axios.post in a high-scale environment
    //function triggerMessageBroker(employeeData, actionType) {
    //    const message = { employee_id: employeeData.id, action: actionType };
    
    // Instead of sending to a URL, we push to a 'queue'
    //    channel.sendToQueue('employee_events', Buffer.from(JSON.stringify(message)), {
    //        persistent: true // If the broker restarts, the message isn't lost
    //});
    
    //    console.log("🚀 Message queued in RabbitMQ!");
    //}
    // We do NOT 'await' this so the API stays responsive
    axios.post(N8N_WEBHOOK_URL, {
        request_id: `REQ-${actionType}-${Date.now()}`,
        employee_id: employeeData.id,
        // Combining firstName/lastName for n8n convenience
        name: `${employeeData.firstName} ${employeeData.lastName}`,
        email: employeeData.email,
        salary: employeeData.salary,
        action: actionType,
        timestamp: new Date().toISOString()
    }, {
        headers: {
            'Authorization': `Bearer ${N8N_SECRET_TOKEN}`,
            'Content-Type': 'application/json'
        },
        timeout: 5000 // Prevents hanging if n8n is down
    })
    .then(() => console.log(`✅ n8n successfully notified for ${actionType}`))
    .catch((err) => console.error("⚠️ n8n Notification background task failed:", err.message));
}

// 1. GET ALL EMPLOYEES
router.get('/', async (req, res) => {
    try {
        const employees = await Employee.findAll();
        return res.status(200).json(employees);
    } catch (err) {
        return res.status(500).json({ message: err.message });
    }
});

// 2. CREATE EMPLOYEE
router.post('/', async (req, res) => {
    try {
        console.log("Creating employee in DB...");
        const employee = await Employee.create(req.body);
        
        // Fire and forget - don't make the user wait for n8n
        triggerN8n(employee, "EMPLOYEE_CREATED");

        return res.status(201).json(employee);
    } catch (error) {
        console.error("Create Error:", error.message);
        return res.status(400).json({ message: "Error creating employee", error: error.message });
    }
});

// 3. ATOMIC SALARY UPDATE
router.patch('/:id/salary', async (req, res) => {
    const { id } = req.params;
    const { newSalary, amountToCredit, ledgerAccountId } = req.body;

    const t = await sequelize.transaction();

    try {
        const employee = await Employee.findByPk(id, { transaction: t });
        if (!employee) {
            await t.rollback();
            return res.status(404).json({ message: "Employee not found" });
        }

        await employee.update({ salary: newSalary }, { transaction: t });

        // Simulate Ledger logic (e.g., TigerBeetle)
        const ledgerSuccess = true; 
        if (!ledgerSuccess) throw new Error("Ledger rejected the transfer");

        await t.commit();

        // Notify n8n after successful commit
        triggerN8n(employee, "SALARY_DISBURSED");

        return res.status(200).json({ message: "Salary and Ledger updated successfully" });

    } catch (err) {
        if (t) await t.rollback();
        return res.status(500).json({ message: "Financial sync failed.", error: err.message });
    }
});

export default router;