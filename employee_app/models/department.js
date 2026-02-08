// models/department.js
import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js'; // adjust path to your DB config

const Department = sequelize.define("Department", {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
    allowNull: false,
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  location: {
    type: DataTypes.STRING,
    allowNull: true,
  },
}, {
  tableName: "departments",
  timestamps: true, // adds createdAt and updatedAt
});

// Associations
Department.associate = (models) => {
  Department.hasMany(models.Employee, {
    foreignKey: "departmentId",
    as: "employees",
  });
};

export default Department;
