
// controllers/avgScore.controller.js
const AvgScoreStateWise = require('../models/avgScoreStateWise.model');
const AvgScoreCityWise = require('../models/avgScoreCityWise.model');
const AvgScoreCenterWise = require('../models/avgScoreCenterWise.model');

const getAvgScores = async (req, res) => {
  const { testId, state, city } = req.body;

  // Validate that at least testId is provided
  if (!testId) {
    return res.status(400).json({ message: 'testId is required.' });
  }

  try {
    let data = [];

    // Case 1: Only testId is provided (state-wise scores)
    if (!state && !city) {
      const stateWiseScores = await AvgScoreStateWise.find({ test_id: testId });
      data = stateWiseScores.map(entry => ({
        state: entry.state,
        avg_score: entry.no_of_students > 0 ? entry.score / entry.no_of_students : 0,
        no_of_students: entry.no_of_students,
      }));
      return res.status(200).json({
        message: 'State-wise average scores fetched successfully.',
        data,
      });
    }

    // Case 2: testId and state are provided (city-wise scores)
    if (state && !city) {
      const cityWiseScores = await AvgScoreCityWise.find({ test_id: testId, state });
      data = cityWiseScores.map(entry => ({
        city: entry.city,
        avg_score: entry.no_of_students > 0 ? entry.score / entry.no_of_students : 0,
        no_of_students: entry.no_of_students,
      }));
      return res.status(200).json({
        message: 'City-wise average scores fetched successfully.',
        data,
      });
    }

    // Case 3: testId, state, and city are provided (center-wise scores)
    if (state && city) {
      const centerWiseScores = await AvgScoreCenterWise.find({ test_id: testId, city });
      data = centerWiseScores.map(entry => ({
        center_id: entry.center_id,
        avg_score: entry.no_of_students > 0 ? entry.score / entry.no_of_students : 0,
        no_of_students: entry.no_of_students,
      }));
      return res.status(200).json({
        message: 'Center-wise average scores fetched successfully.',
        data,
      });
    }
  } catch (error) {
    console.error('Error fetching average scores:', error);
    res.status(500).json({ message: 'An error occurred while fetching average scores.' });
  }
};

module.exports = {
  getAvgScores,
};

