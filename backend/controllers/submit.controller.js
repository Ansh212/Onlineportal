// controllers/submit.controller.js
const mongoose = require('mongoose');
const Log = require('../models/log.model');
const User = require('../models/user.model');
const Test = require('../models/test.model');
const Question = require('../models/question.model');
const Center = require('../models/center.model');
const AvgScoreCityWise = require('../models/avgScoreCityWise.model');
const AvgScoreStateWise = require('../models/avgScoreStateWise.model');
const AvgScoreCenterWise = require('../models/avgScoreCenterWise.model');
const AvgTime = require('../models/avgTime.model');



const submitTest = async (req, res) => {
  const { userId, testId, centerId, logs, focusedTimeSeconds, distractionTimeSeconds } = req.body;
  // Check for required data
  if (!userId || !testId || !centerId || !logs) {
    return res.status(400).json({ message: 'User ID, Test ID, Center ID, and logs are required.' });
  }

  try {
    // Fetch user, test, and center details
    const user = await User.findById(userId);
    const test = await Test.findById(testId).populate('questions');
    const center = await Center.findById(centerId);
    const focused = Number(focusedTimeSeconds) || 0;
    const distracted = Number(distractionTimeSeconds) || 0;
    const total = focused + distracted;
    const focus_ratio = total > 0 ? focused / total : 0;

    if (!user || !test || !center) return res.status(404).json({ message: 'User, Test, or Center not found.' });

    // Calculate time spent on each question and tab switch count
    const times = {}; // Store time spent per question
    let tabSwitches = 0;
    let lastTimestamp = new Date(logs[0].timestamp);

    logs.forEach(log => {
      const currentTimestamp = new Date(log.timestamp);
      const timeSpent = (currentTimestamp - lastTimestamp) / 1000; // Time in seconds 
      if(log.location){
        // Update time for specific question
        const questionId = log.location.toString();
        times[questionId] = (times[questionId] || 0) + timeSpent;
        // Update tab switches count
      } else{
        tabSwitches+=timeSpent; 
      }

      lastTimestamp = currentTimestamp;
    });
    // Calculate user score based on the last selected option per question
    let score = 0;
    const timeEntries = [];
    const lastSelectedOptions = {};

    // Extract the last selected option for each question
    logs.forEach(log => {
      if (log.location && log.activity_text.includes('Selected option')) {
        const optionMatch = log.activity_text.match(/Selected option (\d+)/);
        if (optionMatch) {
          // Parse the selected option if it’s a valid number
          const selectedOption = parseInt(optionMatch[1], 10);
          lastSelectedOptions[log.location.toString()] = selectedOption; // Update with the last valid option
        } else {
            // If "null" was selected, we simply ignore this entry
            lastSelectedOptions[log.location.toString()] = null;
        }
      }
    });

    // Calculate the score based on last selected options
    for (const question of test.questions) {
      const questionId = question._id.toString();
      if (times[questionId]) {
        timeEntries.push({ question_id: new mongoose.Types.ObjectId(questionId), time_spent: times[questionId] });
      }
      const lastOption = lastSelectedOptions[questionId];
      if (lastOption !== null && lastOption === question.correct_answer) {
        score++;
      }
    }

    // Insert log into the Log model
    const logEntry = new Log({
      user_id: userId,
      test_id: testId,
      center_id: centerId,
      logs,
      tab_switch: tabSwitches,
      times: timeEntries,
      focus_ratio: focus_ratio,
    });
    await logEntry.save();

    // Update User model: move test from registered_tests to given_tests
    user.registered_tests = user.registered_tests.filter(test => test.test_id.toString() !== testId);
    user.given_tests.push({
      test_id: testId,
      score,
      city: center.city,
      state: center.state,
    });
    await user.save();

    // Update average tables
    await AvgScoreCityWise.updateOne(
      { test_id: testId,state: center.state, city: center.city },
      { $inc: { score, no_of_students: 1 } },
      { upsert: true }
    );

    await AvgScoreStateWise.updateOne(
      { test_id: testId, state: center.state },
      { $inc: { score, no_of_students: 1 } },
      { upsert: true }
    );

    await AvgScoreCenterWise.updateOne(
      { test_id: testId, city: center.city, center_id: centerId },
      { $inc: { score, no_of_students: 1 } },
      { upsert: true }
    );

    // Update AvgTime model with time per question
    for (const entry of timeEntries) {
      await AvgTime.updateOne(
        { center_id: centerId, test_id: testId, question_id: entry.question_id },
        { $inc: { time: entry.time_spent, no_of_students: 1 } },
        { upsert: true }
      );
    }

    res.status(200).json({ message: 'Test submitted successfully.', score });
  } catch (error) {
    console.error('Error submitting test:', error);
    res.status(500).json({ message: 'An error occurred while submitting the test.' });
  }
};

module.exports = {
  submitTest,
};
