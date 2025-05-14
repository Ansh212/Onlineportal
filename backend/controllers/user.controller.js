
// controllers/user.controller.js
const User = require('../models/user.model');

const createUser = async (req, res) => {
  const { username, password, role, registered_tests, given_tests } = req.body;

  try {
    // Create new user document
    const user = new User({
      username,
      password,
      role: role || null,
      registered_tests: registered_tests || [],
      given_tests: given_tests || [],
    });

    // Save user to database
    await user.save();

    // Send JSON response of created user
    res.status(201).json(user);
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ message: 'An error occurred while creating the user.' });
  }
};

module.exports = {
  createUser,
};
