
// routes/log.routes.js
const express = require('express');
const { submitTest } = require('../controllers/submit.controller');

const router = express.Router();

// POST /api/submit-test - Submit test results and logs
router.post('/', submitTest);

module.exports = router;
