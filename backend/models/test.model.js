// models/test.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const testSchema = new Schema({
  name: {
    type: String,
    required: true,
  },
  duration: {
    type: Number,
    required: true,
  },
  start_time: {
    type: Date,
    required: true,
  },
  end_time: {
    type: Date,
    required: true,
  },
  questions: [{
    type: Schema.Types.ObjectId,
    ref: 'Question',
  }],
});

module.exports = mongoose.model('Test', testSchema);
