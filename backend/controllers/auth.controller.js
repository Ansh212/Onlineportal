const User = require('../models/user.model');
const Test = require('../models/test.model');

const login = async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: 'Username and password are required.' });
  }

  try {
    const user = await User.findOne({ username });

    if (!user) {
      return res.status(404).json({ message: 'User not found.' });
    }

    if (user.password !== password) {
      return res.status(401).json({ message: 'Invalid username or password.' });
    }

    // Get all registered test IDs
    const registeredTestIds = user.registered_tests.map(test => test.test_id);
    const registeredTestDetails = await Test.find({ _id: { $in: registeredTestIds } });

    // Create a map for quick lookup
    const registeredTestMap = {};
    registeredTestDetails.forEach(test => {
      registeredTestMap[test._id.toString()] = test;
    });

    const transformedRegisteredTests = user.registered_tests.map(test => ({
      _id: test.test_id,
      center_id: test.center_id,
      city: test.city,
      state: test.state,
      test_name: registeredTestMap[test.test_id.toString()]?.name || test.test_name,
    }));

    // Get all given test IDs
    const givenTestIds = user.given_tests.map(test => test.test_id);
    const givenTestDetails = await Test.find({ _id: { $in: givenTestIds } });

    // Create a map for quick lookup
    const givenTestMap = {};
    givenTestDetails.forEach(test => {
      givenTestMap[test._id.toString()] = test;
    });

    const transformedGivenTests = user.given_tests.map(test => ({
      _id: test.test_id,
      score: test.score,
      city: test.city,
      state: test.state,
      test_name: givenTestMap[test.test_id.toString()]?.name || null,
    }));

    const data = {
      id: user._id,
      username: user.username,
      role: user.role,
      registered_tests: transformedRegisteredTests,
      given_tests: transformedGivenTests,
    };

    res.json({
      message: 'Login successful',
      data,
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'An error occurred during login.' });
  }
};

module.exports = {
  login,
};
