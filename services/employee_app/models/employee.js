import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js';

const Employee = sequelize.define('Employee', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  firstName: { type: DataTypes.STRING, allowNull: false },
  lastName: { type: DataTypes.STRING, allowNull: false },
  email: { type: DataTypes.STRING, unique: true, allowNull: false },
  salary: { type: DataTypes.FLOAT, allowNull: false },
  departmentId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: { model: 'Departments', key: 'id' }
  }
});
export default Employee