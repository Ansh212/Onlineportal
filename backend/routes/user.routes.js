
// routes/user.routes.js
const express = require('express');
const { createUser } = require('../controllers/user.controller');

const router = express.Router();

// POST /api/users - Create user endpoint
router.post('/users', createUser);

module.exports = router;
