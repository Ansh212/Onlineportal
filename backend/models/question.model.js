// models/question.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const questionSchema = new Schema({
  question_text: {
    type: String,
    required: true,
  },
  options: {
    type: [String],
    required: true,
  },
  correct_answer: {
    type: Number,
    required: true,
  },
});

module.exports = mongoose.model('Question', questionSchema);
