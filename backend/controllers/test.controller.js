const mongoose = require('mongoose');
const User = require('../models/user.model');
const Test = require('../models/test.model');

const getUpcomingUnregisteredTests = async (req, res) => {
  const { userId } = req.body;

  // Validate that userId is provided and is a valid ObjectId
  if (!userId || !mongoose.Types.ObjectId.isValid(userId)) {
    return res.status(400).json({ message: 'Invalid or missing User ID.' });
  }

  try {
    // Find the user by ID
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found.' });
    }

    // If the user is an admin, return all tests
    if (user.role === 'admin') {
      const allTests = await Test.find({}, "_id name start_time end_time");
      return res.status(200).json({ tests: allTests });
    }

    // If the user is not an admin, apply filtering logic
    const registeredTestIds = user.registered_tests.map((test) => test.test_id.toString());
    const givenTestIds = user.given_tests.map((test) => test.test_id.toString());

    // Combine the two arrays into a Set to remove duplicates
    const excludedTestIds = new Set([...registeredTestIds, ...givenTestIds]);

    // Get the current date and time
    const currentTime = new Date();

    const upcomingUnregisteredTests = await Test.find(
      {
        _id: { $nin: Array.from(excludedTestIds) },
        end_time: { $gt: currentTime },
      },
      "_id name start_time end_time" // Only include essential fields
    );

    // Return unregistered and ungiven upcoming tests
    res.status(200).json({ tests: upcomingUnregisteredTests });
  } catch (error) {
    console.error('Error fetching unregistered upcoming tests:', error);
    res.status(500).json({ message: 'An error occurred while fetching tests.' });
  }
};

module.exports = {
  getUpcomingUnregisteredTests,
};
