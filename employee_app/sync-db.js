import sequelize from "./config/database.js";
import "./models/department.js";
import "./models/employee.js";

async function sync() {
  try {
    await sequelize.authenticate();
    console.log("��� Connected");
    await sequelize.sync({ force: true });
    console.log("✅ Success");
    process.exit(0);
  } catch (err) {
    console.error("❌ Error:", err.message);
    process.exit(1);
  }
}
sync();