
// models/avgTime.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const avgTimeSchema = new Schema({
  center_id: {
    type: Schema.Types.ObjectId,
    ref: 'Center',
    required: true,
  },
  test_id: {
    type: Schema.Types.ObjectId,
    ref: 'Test',
    required: true,
  },
  question_id: {
    type: Schema.Types.ObjectId,
    ref: 'Question',
    required: true,
  },
  time: {
    type: Number,
    required: true,
  },
  no_of_students: {
    type: Number,
    required: true,
  }
});

module.exports = mongoose.model('AvgTime', avgTimeSchema);
