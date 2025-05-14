const express = require('express');
const router = express.Router();
const evaluateTestController = require('../controllers/flaggedResult.Controller');

// POST route to evaluate test logs
router.post('/', evaluateTestController.evaluateTest);

module.exports = router;
