// models/employee.js
import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js';

const Employee = sequelize.define('Employee', {
  firstName: { type: DataTypes.STRING, allowNull: false },
  lastName: { type: DataTypes.STRING, allowNull: false },
  email: { type: DataTypes.STRING, unique: true },
  salary: { type: DataTypes.DECIMAL },
  departmentId: { type: DataTypes.INTEGER }
}, {
  tableName: 'employees', // 👈 This MUST match your SQL error target
  timestamps: true
});

// THIS IS THE CRITICAL LINE
export default Employee;