const mongoose = require('mongoose');
const Log = require('../models/log.model');
const Test = require('../models/test.model');
const FlaggedResult = require('../models/flaggedResult.model');
const User = require('../models/user.model');
const axios = require('axios'); // Added axios for HTTP requests

exports.evaluateTest = async (req, res) => {
  try {
    const { testId } = req.body;

    if (!testId || !mongoose.Types.ObjectId.isValid(testId)) {
      return res.status(400).json({ error: 'Valid testId is required' });
    }

    const test = await Test.findById(testId).populate('questions');
    if (!test) {
      return res.status(404).json({ error: 'Test not found' });
    }

    // const existingFlaggedResult = await FlaggedResult.findOne({ test_id: testId }).populate('flagged_users', 'username').populate('flagged_centers', 'name'); // Assuming center model has a name
    // if (existingFlaggedResult) {
    //   return res.status(200).json({
    //     message: 'Evaluation already completed',
    //     flagged_users: existingFlaggedResult.flagged_users.map(user => ({ _id: user._id, username: user.username })),
    //     flagged_centers: existingFlaggedResult.flagged_centers.map(center => ({ _id: center._id, name: center.name || center._id.toString() })),
    //     summary: existingFlaggedResult.summary,
    //   });
    // }

    // Calculate Total Registered and Total Given Students
    const allUsersForTestStats = await User.find({}, { registered_tests: 1, given_tests: 1, username: 1 });
    let totalRegistered = 0;
    let totalGiven = 0;
    const givenUserIds = new Set();

    allUsersForTestStats.forEach((user) => {
      const isRegistered = user.registered_tests.some((t) => t.test_id.equals(testId)) || user.given_tests.some((t) => t.test_id.equals(testId));
      if (isRegistered) totalRegistered++;
      if (user.given_tests.some((t) => t.test_id.equals(testId))) {
        totalGiven++;
        givenUserIds.add(user._id.toString());
      }
    });
    const totalNotGiven = totalRegistered - totalGiven;

    // Fetch all logs for the test
    const logsForTest = await Log.find({ test_id: testId }); 

    if (logsForTest.length === 0) {
        // No logs, so no one to flag based on logs. Save a default flagged result.
        const emptyFlaggedResult = new FlaggedResult({
            test_id: testId,
            flagged_users: [],
            flagged_centers: [],
            summary: {
                total_registered: totalRegistered,
                total_given: totalGiven,
                total_not_given: totalNotGiven,
                total_flagged: 0,
            },
        });
        await emptyFlaggedResult.save();
        return res.status(200).json({
            message: 'Evaluation complete (no logs found for this test)',
            flagged_users: [],
            flagged_centers: [],
            summary: emptyFlaggedResult.summary,
        });
    }

    // 1. Prepare questions_data for Python service
    const questions_data_for_python = test.questions.map(q => ({
        id: q._id.toString(),
        text: q.question_text,
        options: q.options, 
        correct_answer: q.correct_answer,
    }));

    // 2. Prepare all_user_logs for Python service
    const all_user_logs_for_python = logsForTest.map(logDoc => ({
        userId: logDoc.user_id.toString(),
        session_log_events: logDoc.logs.map(event => ({
            timestamp: event.timestamp,
            activity_text: event.activity_text,
            location: event.location ? event.location.toString() : null,
        }))
    }));    

    // 3. Call Python Service
    const PYTHON_SERVICE_URL = process.env.PYTHON_PREDICTION_SERVICE_URL || 'http://localhost:5001/predict_batch';
    let pythonServiceResponseData;
    try {
        const response = await axios.post(PYTHON_SERVICE_URL, {
            all_user_logs: all_user_logs_for_python,
            questions_data: questions_data_for_python
        });
        pythonServiceResponseData = response.data;
    } catch (axiosError) {
        console.error('Error calling Python prediction service:', axiosError.message);
        return res.status(500).json({ error: 'Failed to get predictions from Python service. ' + (axiosError.response ? axiosError.response.data.error : axiosError.message) });
    }

    // 4. Process Python Service Response to get flaggedUserIds
    const flaggedUserIdsFromPython = new Set();
    if (Array.isArray(pythonServiceResponseData)) {
        pythonServiceResponseData.forEach(pred => {
            if (pred.prediction_label === 1) { // cheating
                flaggedUserIdsFromPython.add(pred.userId);
            }
        });
    } else {
        console.error('Unexpected response format from Python service:', pythonServiceResponseData);
        return res.status(500).json({ error: 'Invalid response format from Python service.' });
    }

    // 5. Calculate Flagged Centers based on Python's output
    const centerStats = {};

    logsForTest.forEach(logDoc => {
        const userId = logDoc.user_id.toString();
        const center = logDoc.center_id; 
        if (!center || !center._id) return; 
        
        const centerId = center._id.toString();

        if (!centerStats[centerId]) {
            centerStats[centerId] = { total_submitted_by_center: 0, flagged_by_center: 0 };
        }
        centerStats[centerId].total_submitted_by_center++;

        if (flaggedUserIdsFromPython.has(userId)) {
            centerStats[centerId].flagged_by_center++;
        }
    });

    const flaggedCenters = Object.keys(centerStats).filter(centerId => {
        const stats = centerStats[centerId];
        return stats.total_submitted_by_center > 0 && (stats.flagged_by_center / stats.total_submitted_by_center) >= 0.1;
    });

    const flaggedUserDetails = await User.find(
      { _id: { $in: Array.from(flaggedUserIdsFromPython)}},
      { username: 1 }
    );

    // Save Flagged Results
    const newFlaggedResult = new FlaggedResult({
      test_id: testId,
      flagged_users: Array.from(flaggedUserIdsFromPython),
      flagged_centers: flaggedCenters.map(fc => fc._id),
      summary: {
        total_registered: totalRegistered,
        total_given: totalGiven,
        total_not_given: totalNotGiven,
        total_flagged: flaggedUserIdsFromPython.size,
      },
    });
    await newFlaggedResult.save();

    // Respond with Results
    return res.status(200).json({
      message: 'Evaluation complete using Python service predictions',
      flagged_users: flaggedUserDetails.map(user => ({ _id: user._id, username: user.username })),
      flagged_centers: flaggedCenters, 
      summary: newFlaggedResult.summary,
    });

  } catch (error) {
    console.error('Error evaluating test logs:', error);
    return res.status(500).json({ error: 'An error occurred during evaluation.' });
  }
};
