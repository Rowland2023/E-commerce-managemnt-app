// models/department.js
import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js'; // adjust path to your DB config

const Department = sequelize.define('Department', {
  name: { 
    type: DataTypes.STRING, 
    allowNull: false 
  },
  budgetCode: { 
    type: DataTypes.STRING 
  }
}, {
  tableName: 'departments',   // 👈 explicit table name
  timestamps: true            // adds createdAt and updatedAt
});

export default Department;
