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

// Generate a random MongoDB-like ObjectId
function generateObjectId() {
  const timestamp = Math.floor(new Date().getTime() / 1000).toString(16);
  const randomPart = Math.random().toString(16).substr(2, 16);
  return timestamp + randomPart.padStart(16, '0');
}

// Generate logs for a normal test taker
function generateNormalLogs() {
  const startTime = new Date();
  let currentTime = 0;
  const logs = [];
  const times = [];
  
  // Generate sample IDs
  const userId = generateObjectId();
  const testId = generateObjectId();
  const centerId = generateObjectId();
  const questionIds = Array.from({ length: 20 }, () => generateObjectId());
  
  // Determine if this user will switch tabs (20% chance)
  const willSwitchTabs = Math.random() < 0.2;
  const tabSwitches = willSwitchTabs ? Math.floor(normalDistribution(3, 1)) : 0;
  let tabSwitchPoints = [];
  
  if (willSwitchTabs) {
    // Generate random points for tab switches
    for (let i = 0; i < tabSwitches; i++) {
      tabSwitchPoints.push(Math.floor(Math.random() * 600));
    }
    tabSwitchPoints.sort((a, b) => a - b);
  }

  // Track visited questions to simulate realistic navigation
  const visitedQuestions = new Set();
  const questionOrder = [...questionIds];
  
  // Simulate natural question navigation
  while (visitedQuestions.size < questionIds.length) {
    let currentQuestionIndex;
    if (Math.random() < 0.8) {
      currentQuestionIndex = visitedQuestions.size;
    } else {
      const unvisitedQuestions = questionOrder.filter(q => !visitedQuestions.has(q));
      currentQuestionIndex = questionOrder.indexOf(unvisitedQuestions[Math.floor(Math.random() * unvisitedQuestions.length)]);
    }

    const questionId = questionOrder[currentQuestionIndex];
    visitedQuestions.add(questionId);

    // Log question selection
    logs.push({
      location: questionId,
      timestamp: generateTimestamp(startTime, currentTime),
      activity_text: `Selected question ${currentQuestionIndex}`
    });

    // Normal distribution for reading time
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

    // Normal distribution for answer selection time
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

    // Add small pause between questions
    currentTime += 2 + Math.random() * 3;
  }

  // Add test submission log
  logs.push({
    location: questionOrder[questionOrder.length - 1],
    timestamp: generateTimestamp(startTime, currentTime),
    activity_text: 'Submitted Test'
  });

  return {
    _id: generateObjectId(),
    user_id: userId,
    test_id: testId,
    center_id: centerId,
    logs,
    tab_switch: tabSwitches * 2,
    times
  };
}

// Generate sample data for 2 different types of test takers
console.log("\n=== Sample Test Taker 1 (No Tab Switches) ===");
const sampleLog1 = generateNormalLogs();
console.log("Total time taken:", (sampleLog1.logs[sampleLog1.logs.length - 1].timestamp - sampleLog1.logs[0].timestamp) / 1000, "seconds");
console.log("Number of tab switches:", sampleLog1.tab_switch);
console.log("Sample of activities:");
console.log(sampleLog1.logs.slice(0, 5));
console.log("\nTime spent on first 3 questions:");
console.log(sampleLog1.times.slice(0, 3));

console.log("\n=== Sample Test Taker 2 (With Tab Switches) ===");
const sampleLog2 = generateNormalLogs();
console.log("Total time taken:", (sampleLog2.logs[sampleLog2.logs.length - 1].timestamp - sampleLog2.logs[0].timestamp) / 1000, "seconds");
console.log("Number of tab switches:", sampleLog2.tab_switch);
console.log("Sample of activities:");
console.log(sampleLog2.logs.slice(0, 5));
console.log("\nTime spent on first 3 questions:");
console.log(sampleLog2.times.slice(0, 3)); 