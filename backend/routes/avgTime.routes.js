
// routes/avgTime.routes.js
const express = require('express');
const { getAvgTimeForQuestion } = require('../controllers/avgTime.controller');

const router = express.Router();

// POST /api/avg-time/question - Fetch average time for a question for all centers of a test
router.post('/', getAvgTimeForQuestion);

module.exports = router;
