
// models/log.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const logSchema = new Schema({
  user_id: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  test_id: {
    type: Schema.Types.ObjectId,
    ref: 'Test',
    required: true,
  },
  center_id: {
    type: Schema.Types.ObjectId,
    ref: 'Center',
    required: true,
  },
  logs: [
    {
      location: {
        type: Schema.Types.ObjectId,
        ref: 'Question',
        default: null,
      },
      timestamp: {
        type: Date,
        required: true,
      },
      activity_text: {
        type: String,
        required: true,
      },
    }
  ],
  tab_switch: {
    type: Number,
    required: true,
    default: 0,
  },
  times: [
    {
      question_id: {
        type: Schema.Types.ObjectId,
        ref: 'Question',
        required: true,
      },
      time_spent: {
        type: Number,
        required: true,
      }
    }
  ],
  focus_ratio: {
    type: Number,
    required: true,
  }
});

module.exports = mongoose.model('Log', logSchema);
