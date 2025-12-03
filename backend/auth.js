const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET || 'dev_secret_change_me';

function sign(user) {
  return jwt.sign({ id: user.id, email: user.email, role: user.role }, SECRET, { expiresIn: '8h' });
}

function verifyToken(token) {
  return jwt.verify(token, SECRET);
}

function authMiddleware(req, res, next) {
  const h = req.headers.authorization;
  if (!h) return res.status(401).json({ error: 'Missing auth' });
  const parts = h.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') return res.status(401).json({ error: 'Bad auth format' });
  try {
    const payload = verifyToken(parts[1]);
    req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

function authorize(...allowedRoles) {
  return (req, res, next) => {
    authMiddleware(req, res, () => {
      if (!allowedRoles.includes(req.user.role)) return res.status(403).json({ error: 'Forbidden' });
      next();
    });
  };
}

module.exports = { sign, verifyToken, authMiddleware, authorize };
