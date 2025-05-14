
// routes/take_test.routes.js
const express = require('express');
const { takeTest } = require('../controllers/take_test.controller');

const router = express.Router();

router.post('/', takeTest);

module.exports = router;
