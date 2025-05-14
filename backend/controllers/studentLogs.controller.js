const User = require('../models/user.model');
const Log = require('../models/log.model');
const Test = require('../models/test.model');
const mongoose = require('mongoose');

const getStudentData = async (req, res) => {
  const { studentId, testId } = req.body;

  try {
    // Case 1: No studentId is provided
    if (!studentId) {
      let students = await User.find({ role: null }, { _id: 1, username: 1 });

      students = students.sort((a, b) => {
        const numA = parseInt(a.username.replace(/\D/g, ''), 10); // extract numbers
        const numB = parseInt(b.username.replace(/\D/g, ''), 10);
        return numA - numB;
      });
      const studentData = students.map(student => ({
        id: student._id,
        username: student.username || "Unknown"
      }));

      return res.status(200).json({
        message: 'Student data fetched successfully.',
        students: studentData,
      });
    }

    // Validate studentId
    if (!mongoose.Types.ObjectId.isValid(studentId)) {
      return res.status(400).json({ message: 'Invalid student ID.' });
    }

    const student = await User.findById(studentId);
    if (!student) {
      return res.status(404).json({ message: 'Student not found.' });
    }

    // Case 2: studentId is provided, but no testId
    if (!testId) {
      const givenTests = student.given_tests || [];
      const testIds = givenTests.map(t => t.test_id);

      // Fetch test names for these testIds
      const tests = await Test.find({ _id: { $in: testIds } }, { name: 1 });
      
      // Map testIds to their names
      const testData = tests.map(test => ({
        test_id: test._id,
        test_name: test.name
      }));

      return res.status(200).json({
        message: 'Given tests fetched successfully.',
        tests: testData,
      });
    }

    // Validate testId
    if (!mongoose.Types.ObjectId.isValid(testId)) {
      return res.status(400).json({ message: 'Invalid test ID.' });
    }

    // Case 3: studentId and testId are provided
    const givenTest = student.given_tests.find(
      test => test.test_id.toString() === testId
    );

    if (!givenTest) {
      return res.status(404).json({ message: 'Test not found in student records.' });
    }

    const logs = await Log.find({ user_id: studentId, test_id: testId });

    if (!logs || logs.length === 0) {
      return res.status(200).json({
        message: 'No logs found for this test and student.',
        logs: [],
        score: givenTest.score
      });
    }

    return res.status(200).json({
      message: 'Logs and score fetched successfully.',
      logs,
      score: givenTest.score,
    });

  } catch (error) {
    console.error('Error fetching student data:', error);
    return res.status(500).json({ message: 'An error occurred while fetching student data.' });
  }
};

module.exports = {
  getStudentData,
};
