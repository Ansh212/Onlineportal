const mongoose = require('mongoose');
const User = require('../models/user.model');
const Test = require('../models/test.model');
const Center = require('../models/center.model');

const enrollInTest = async (req, res) => {
  const { userId, testId } = req.body;

  // Validate that both userId and testId are provided and valid ObjectIds
  if (!userId || !testId) {
    return res.status(400).json({ message: 'User ID and Test ID are required.' });
  }
  if (!mongoose.Types.ObjectId.isValid(userId) || !mongoose.Types.ObjectId.isValid(testId)) {
    return res.status(400).json({ message: 'Invalid User ID or Test ID format.' });
  }

  try {
    // Check if user exists
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found.' });
    }

    // Check if test exists
    const test = await Test.findById(testId);
    if (!test) {
      return res.status(404).json({ message: 'Test not found.' });
    }

    // Check if the test has expired
    const currentTime = new Date();
    if (test.end_time <= currentTime) {
      return res.status(400).json({ message: 'Cannot enroll in a test that has already ended.' });
    }

    // Check if the user is already registered for the test
    const isAlreadyRegistered = user.registered_tests.some((registeredTest) =>
      registeredTest.test_id.toString() === testId
    );
    if (isAlreadyRegistered) {
      return res.status(400).json({ message: 'You are already registered for this test.' });
    }

    // Fetch all centers and pick one at random
    const centers = await Center.find({});
    if (centers.length === 0) {
      return res.status(500).json({ message: 'No centers available for allocation.' });
    }
    const randomCenter = centers[Math.floor(Math.random() * centers.length)];

    if (!randomCenter) {
      return res.status(500).json({ message: 'Failed to allocate a center. Please try again.' });
    }

    // Add the test to the user's registered_tests array
    user.registered_tests.push({
      test_id: test._id,
      test_name: test.name,
      center_id: randomCenter._id,
      city: randomCenter.city,
      state: randomCenter.state,
    });

    // Save the updated user document
    await user.save();

    res.status(200).json({
      message: 'Enrollment successful',
      registered_test: {
        _id: test._id,
        test_name: test.name,
        center_id: randomCenter._id,
        city: randomCenter.city,
        state: randomCenter.state,
      },
    });
  } catch (error) {
    console.error('Error enrolling in test:', error);
    res.status(500).json({ message: 'An error occurred during enrollment.' });
  }
};

module.exports = {
  enrollInTest,
};
