
// routes/avgScore.routes.js
const express = require('express');
const { getAvgScores } = require('../controllers/avgScore.controller');

const router = express.Router();

// POST /api/avg-scores - Fetch average scores
router.post('/', getAvgScores);

module.exports = router;
