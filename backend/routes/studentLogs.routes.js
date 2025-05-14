
// routes/student.routes.js
const express = require('express');
const { getStudentData } = require('../controllers/studentLogs.controller');

const router = express.Router();

// POST /api/student-data - Fetch student data dynamically
router.post('/', getStudentData);

module.exports = router;
