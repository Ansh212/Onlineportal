
// routes/enrollment.routes.js
const express = require('express');
const { enrollInTest } = require('../controllers/enrollment.controller');

const router = express.Router();

// POST /api/enroll - Enroll user in a test
router.post('/', enrollInTest);

module.exports = router;
