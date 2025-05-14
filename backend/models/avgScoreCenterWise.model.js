
// models/avgScoreCenterWise.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const avgScoreCenterWiseSchema = new Schema({
  test_id: {
    type: Schema.Types.ObjectId,
    ref: 'Test',
    required: true,
  },
  city: {
    type: String,
    required: true,
  },
  center_id: {
    type: Schema.Types.ObjectId,
    ref: 'Center',
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

module.exports = mongoose.model('AvgScoreCenterWise', avgScoreCenterWiseSchema);
