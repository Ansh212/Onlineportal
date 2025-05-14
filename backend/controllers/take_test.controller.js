const mongoose = require('mongoose');
const User = require('../models/user.model');
const Test = require('../models/test.model');
const Question = require('../models/question.model');

const takeTest = async (req, res) => {
  const { userId, testId } = req.body;
  if (!userId || !testId) {
    return res.status(400).json({ message: 'User ID and Test ID are required.' });
  }

  if (!mongoose.Types.ObjectId.isValid(userId) || !mongoose.Types.ObjectId.isValid(testId)) {
    return res.status(400).json({ message: 'Invalid User ID or Test ID format.' });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found.' });
    }

    const test = await Test.findById(testId);
    if (!test) {
      return res.status(404).json({ message: 'Test not found.' });
    }

    // Admin shortcut
    if (user.role === "admin") {
      const adminQuestions = await Question.find(
        { _id: { $in: test.questions } },
        { correct_answer: 0 }
      );

      if (adminQuestions.length === 0) {
        return res.status(404).json({ message: 'No questions are associated with this test.' });
      }

      return res.status(200).json({
        message: 'Admin Test Questions',
        duration: test.duration,
        questions: adminQuestions.map((q) => ({
          _id: q._id,
          question_text: q.question_text,
          options: q.options,
        })),
      });
    }

    // Check enrollment
    const isEnrolled = user.registered_tests.some(
      (t) => t.test_id.toString() === testId
    );
    if (!isEnrolled) {
      return res.status(403).json({ message: 'User is not enrolled in this test.' });
    }

    const currentTime = new Date();
    if (test.start_time > currentTime) {
      return res.status(403).json({ message: `Test will be available on ${test.start_time.toLocaleString()}. Please check back later.` });
    }

    if (test.end_time <= currentTime) {
      return res.status(403).json({ message: 'Test has already expired.' });
    }

    const questions = await Question.find(
      { _id: { $in: test.questions } },
      { correct_answer: 0 }
    );

    if (questions.length === 0) {
      return res.status(404).json({ message: 'No questions are associated with this test.' });
    }

    res.status(200).json({
      message: 'Test is ready to take.',
      duration: test.duration,
      questions: questions.map((q) => ({
        _id: q._id,
        question_text: q.question_text,
        options: q.options,
      })),
    });
  } catch (error) {
    console.error('Error preparing test:', error);
    res.status(500).json({ message: 'An error occurred while preparing the test.' });
  }
};

module.exports = {
  takeTest,
};
