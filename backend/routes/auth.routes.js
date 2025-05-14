// routes/auth.routes.js
const express = require('express');
const { login } = require('../controllers/auth.controller');

const router = express.Router();

// POST /api/auth/login - Login endpoint
router.post('/login', login);

module.exports = router;
