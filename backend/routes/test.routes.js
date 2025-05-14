
// routes/test.routes.js
const express = require('express');
const { getUpcomingUnregisteredTests } = require('../controllers/test.controller');

const router = express.Router();

// POST /api/tests/unregistered/upcoming - Get unregistered, ungiven, and upcoming tests for a user
router.post('/', getUpcomingUnregisteredTests);

module.exports = router;
