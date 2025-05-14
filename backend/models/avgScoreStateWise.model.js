
// models/avgScoreStateWise.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const avgScoreStateWiseSchema = new Schema({
  test_id: {
    type: Schema.Types.ObjectId,
    ref: 'Test',
    required: true,
  },
  state: {
    type: String,
    required: true,
  },
  score: {
    type: Number,
    required: true,
  },
  no_of_students: {
    type: Number,
    required: true,
  }
});

module.exports = mongoose.model('AvgScoreStateWise', avgScoreStateWiseSchema);
