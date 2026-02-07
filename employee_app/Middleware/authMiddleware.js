// Middleware/authMiddleware.js
import jwt from 'jsonwebtoken';

const authMiddleware = (req, res, next) => {
  try {
    console.log("DEBUG: Authorization Header Received:", req.headers.authorization);
    const authHeader = req.headers.authorization;
    
    // 1. Check if header exists and starts with "Bearer "
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: "Access Denied: No Token Provided" });
    }

    // 2. Extract the token
    const token = authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({ message: "Access Denied: Malformed Header" });
    }

    // 3. Verify the token
    const verified = jwt.verify(token, process.env.JWT_SECRET);
    
    // Attach user data to the request object
    req.user = verified;
    next(); 
    
  } catch (err) {
    // 4. Catch "jwt malformed" or "jwt expired" errors here
    console.error("Auth Error:", err.message);
    return res.status(403).json({ message: "Invalid or Expired Token" });
  }
};

export default authMiddleware;