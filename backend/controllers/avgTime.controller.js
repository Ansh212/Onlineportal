
// controllers/avgTime.controller.js
const AvgTime = require('../models/avgTime.model');
const Center = require('../models/center.model');

const getAvgTimeForQuestion = async (req, res) => {
  const { test_id, question_id } = req.body;

  // Validate input
  if (!test_id || !question_id) {
    return res.status(400).json({ message: 'test_id and question_id are required.' });
  }

  try {
    // Query the avgTime collection for the specified test and question
    const avgTimes = await AvgTime.find({ test_id, question_id }).populate('center_id', 'city state');

    // Map the data to return center details and average time
    const results = avgTimes.map(entry => {
      const avgTimePerStudent = entry.no_of_students > 0 ? entry.time / entry.no_of_students : 0;

      return {
        center_id: entry.center_id._id,
        city: entry.center_id.city,
        state: entry.center_id.state,
        avg_time: avgTimePerStudent,
        no_of_students: entry.no_of_students,
      };
    });

    res.status(200).json({
      message: 'Average times fetched successfully.',
      data: results,
    });
  } catch (error) {
    console.error('Error fetching average times:', error);
    res.status(500).json({ message: 'An error occurred while fetching average times.' });
  }
};

module.exports = {
  getAvgTimeForQuestion,
};
