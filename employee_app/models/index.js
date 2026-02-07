// models/index.js
import Employee from './employee.js';
import Department from './department.js';

// Associations
Department.hasMany(Employee, {
  foreignKey: 'departmentId',
  onDelete: 'CASCADE',
});
Employee.belongsTo(Department, {
  foreignKey: 'departmentId',
});

export { Employee, Department };
