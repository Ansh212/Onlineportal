const mongoose = require('mongoose');
const Log = require('../../models/log.model');
const User = require('../../models/user.model');

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/onlineportal', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Helper function for normal distribution (Box-Muller transform)
function normalDistribution(mean, stdDev) {
  let u = 0, v = 0;
  while(u === 0) u = Math.random();
  while(v === 0) v = Math.random();
  const num = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  return num * stdDev + mean;
}

// Helper function to generate timestamp
const generateTimestamp = (startTime, offsetSeconds) => {
  return new Date(startTime.getTime() + offsetSeconds * 1000);
};

// Helper function to ensure time is within reasonable bounds
function boundedTime(time, min, max) {
  return Math.min(Math.max(time, min), max);
}

// Generate logs for a normal test taker
async function generateNormalLogs(userId, testId, centerId, questionIds) {
  const startTime = new Date();
  let currentTime = 0;
  const logs = [];
  const times = [];
  
  // Determine if this user will switch tabs (20% chance)
  const willSwitchTabs = Math.random() < 0.2;
  const tabSwitches = willSwitchTabs ? Math.floor(normalDistribution(3, 1)) : 0;
  let tabSwitchPoints = [];
  
  if (willSwitchTabs) {
    // Generate random points for tab switches
    for (let i = 0; i < tabSwitches; i++) {
      tabSwitchPoints.push(Math.floor(Math.random() * 600)); // Within 10 minutes (600 seconds)
    }
    tabSwitchPoints.sort((a, b) => a - b);
  }

  // Track visited questions to simulate realistic navigation
  const visitedQuestions = new Set();
  const questionOrder = [...questionIds];
  
  // Simulate natural question navigation
  while (visitedQuestions.size < questionIds.length) {
    // Choose next question (80% chance of sequential, 20% chance of random jump)
    let currentQuestionIndex;
    if (Math.random() < 0.8) {
      // Sequential navigation
      currentQuestionIndex = visitedQuestions.size;
    } else {
      // Random jump to unvisited question
      const unvisitedQuestions = questionOrder.filter(q => !visitedQuestions.has(q.toString()));
      currentQuestionIndex = questionOrder.indexOf(unvisitedQuestions[Math.floor(Math.random() * unvisitedQuestions.length)]);
    }

    const questionId = questionOrder[currentQuestionIndex];
    visitedQuestions.add(questionId.toString());

    // Log question selection
    logs.push({
      location: questionId,
      timestamp: generateTimestamp(startTime, currentTime),
      activity_text: `Selected question ${currentQuestionIndex}`
    });

    // Normal distribution for reading time (mean: 25 seconds, stdDev: 5 seconds)
    const readingTime = boundedTime(normalDistribution(25, 5), 15, 40);
    currentTime += readingTime;

    // Check for tab switch during this question
    if (willSwitchTabs) {
      while (tabSwitchPoints.length > 0 && tabSwitchPoints[0] <= currentTime) {
        logs.push({
          location: null,
          timestamp: generateTimestamp(startTime, tabSwitchPoints[0]),
          activity_text: 'Tab Switched'
        });
        logs.push({
          location: null,
          timestamp: generateTimestamp(startTime, tabSwitchPoints[0] + 5),
          activity_text: 'Returned to Test Tab'
        });
        tabSwitchPoints.shift();
      }
    }

    // Normal distribution for answer selection time (mean: 15 seconds, stdDev: 5 seconds)
    const answerTime = boundedTime(normalDistribution(15, 5), 8, 25);
    currentTime += answerTime;

    // Log answer selection
    logs.push({
      location: questionId,
      timestamp: generateTimestamp(startTime, currentTime),
      activity_text: `Selected option ${Math.floor(Math.random() * 4)} for question ${currentQuestionIndex}`
    });

    // Record total time spent on question
    times.push({
      question_id: questionId,
      time_spent: readingTime + answerTime
    });

    // Add small pause between questions (2-5 seconds)
    currentTime += 2 + Math.random() * 3;
  }

  // Add test submission log
  logs.push({
    location: questionOrder[questionOrder.length - 1],
    timestamp: generateTimestamp(startTime, currentTime),
    activity_text: 'Submitted Test'
  });

  return new Log({
    user_id: userId,
    test_id: testId,
    center_id: centerId,
    logs,
    tab_switch: tabSwitches * 2, // Each switch counts as switch out and return
    times
  });
}

// // Generate suspicious behavior logs
// async function generateSuspiciousLogs(userId, testId, centerId, questionIds) {
//   const startTime = new Date();
//   let currentTime = 0;
//   const logs = [];
//   const times = [];
//   let tabSwitches = randomTime(5, 15); // Suspicious number of tab switches

//   for (const questionId of questionIds) {
//     // Suspiciously quick responses (10-30 seconds)
//     const timeSpent = randomTime(10, 30);
//     times.push({
//       question_id: questionId,
//       time_spent: timeSpent
//     });

//     // Add suspicious activity logs
//     logs.push({
//       location: questionId,
//       timestamp: generateTimestamp(startTime, currentTime),
//       activity_text: 'Question viewed'
//     });

//     // Simulate tab switching
//     if (Math.random() < 0.4) {
//       logs.push({
//         location: questionId,
//         timestamp: generateTimestamp(startTime, currentTime + 2),
//         activity_text: 'Tab switched'
//       });
//     }

//     // Rapid mouse movements
//     if (Math.random() < 0.3) {
//       logs.push({
//         location: questionId,
//         timestamp: generateTimestamp(startTime, currentTime + 3),
//         activity_text: 'Rapid mouse movement detected'
//       });
//     }

//     // Quick answer submission
//     logs.push({
//       location: questionId,
//       timestamp: generateTimestamp(startTime, currentTime + timeSpent),
//       activity_text: 'Answer submitted'
//     });

//     currentTime += timeSpent;
//   }

//   return new Log({
//     user_id: userId,
//     test_id: testId,
//     center_id: centerId,
//     logs,
//     tab_switch: tabSwitches,
//     times
//   });
// }

async function generateAllLogs() {
  try {
    const users = await User.find({ role: null });
    const logs = [];

    for (const user of users) {
      for (const test of user.registered_tests) {
        const questionIds = Array.from({ length: 20 }, () => mongoose.Types.ObjectId());
        const log = await generateNormalLogs(user._id, test.test_id, test.center_id, questionIds);
        logs.push(log);
      }
    }

    await Log.insertMany(logs);
    console.log('Logs generated successfully!');
  } catch (err) {
    console.error('Error generating logs:', err);
  } finally {
    mongoose.connection.close();
  }
}

generateAllLogs(); 