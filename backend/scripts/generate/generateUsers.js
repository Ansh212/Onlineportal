const mongoose = require('mongoose');
const User = require('../../models/user.model');
const faker = require('faker');

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/onlineportal', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const states = [
  'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat',
  'Uttar Pradesh', 'West Bengal', 'Telangana', 'Rajasthan', 'Kerala'
];

const cities = {
  'Maharashtra': ['Mumbai', 'Pune', 'Nagpur'],
  'Delhi': ['New Delhi', 'North Delhi', 'South Delhi'],
  'Karnataka': ['Bangalore', 'Mysore', 'Hubli'],
  // Add more cities for other states as needed
};

async function generateUsers(count) {
  const users = [];
  
  // Create one admin user
  const adminUser = new User({
    username: 'admin',
    password: 'admin123', // In production, use proper password hashing
    role: 'admin',
    registered_tests: [],
    given_tests: []
  });
  users.push(adminUser);

  // Create regular users
  for (let i = 0; i < count; i++) {
    const state = states[Math.floor(Math.random() * states.length)];
    const citiesInState = cities[state] || ['Unknown City'];
    const city = citiesInState[Math.floor(Math.random() * citiesInState.length)];

    const user = new User({
      username: faker.internet.userName(),
      password: faker.internet.password(), // In production, use proper password hashing
      role: null,
      registered_tests: [],
      given_tests: []
    });

    // Add some random registered and given tests
    const numTests = Math.floor(Math.random() * 5) + 1;
    for (let j = 0; j < numTests; j++) {
      const testId = mongoose.Types.ObjectId();
      const centerId = mongoose.Types.ObjectId();
      
      // Add registered test
      user.registered_tests.push({
        test_id: testId,
        test_name: `Test ${j + 1}`,
        center_id: centerId,
        city,
        state
      });

      // 70% chance the user has given the test
      if (Math.random() < 0.7) {
        user.given_tests.push({
          test_id: testId,
          score: Math.floor(Math.random() * 100),
          city,
          state
        });
      }
    }

    users.push(user);
  }

  return User.insertMany(users);
}

// Generate 50 users
generateUsers(50)
  .then(() => {
    console.log('Users generated successfully!');
    mongoose.connection.close();
  })
  .catch(err => {
    console.error('Error generating users:', err);
    mongoose.connection.close();
  }); 