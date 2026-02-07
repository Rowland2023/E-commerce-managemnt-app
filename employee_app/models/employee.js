const Employee = sequelize.define('Employee', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  firstName: { type: DataTypes.STRING, allowNull: false },
  lastName: { type: DataTypes.STRING, allowNull: false },
  email: { type: DataTypes.STRING, unique: true, allowNull: false },
  salary: { type: DataTypes.FLOAT, allowNull: false },
  departmentId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    // Change 'Departments' to 'departments' to match your Department model
    references: { model: 'departments', key: 'id' } 
  }
}, {
  tableName: 'employees', // Add this line
  timestamps: true        // Match your department settings
});