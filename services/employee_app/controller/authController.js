// controller/authController.js
import { Router } from 'express';
import jwt from 'jsonwebtoken';

const router = Router();

router.post('/login', (req, res) => {
  // 1. Validation Check (The "Senior" mindset)
  // In a real Ecobank app, you'd verify credentials against the DB here.
  const { username, password } = req.body; 

  // For now, using your mock user
  const user = { id: 1, name: "Rowland", role: "admin" };

  // 2. Secret Key Guard
  const secret = process.env.JWT_SECRET;

  if (!secret) {
    console.error("❌ CRITICAL ERROR: JWT_SECRET is not defined in environment variables.");
    return res.status(500).json({ 
      message: "Internal server configuration error. Please contact the administrator." 
    });
  }

  try {
    // 3. Signing the token
    // We pass a specific payload rather than the whole object to keep the token small.
    const token = jwt.sign(
      { id: user.id, name: user.name }, 
      secret, 
      { expiresIn: '1h', algorithm: 'HS256' }
    );

    console.log(`✅ Token generated successfully for user: ${user.name}`);
    
    return res.json({ 
      success: true,
      token: token 
    });

  } catch (error) {
    console.error("JWT Signing Error:", error.message);
    return res.status(500).json({ message: "Failed to generate authentication token." });
  }
});

export default router;