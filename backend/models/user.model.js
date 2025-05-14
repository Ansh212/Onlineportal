// models/user.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const userSchema = new Schema({
  username: {
    type: String,
    required: true,
    unique: true,
  },
  password: {
    type: String,
    required: true,
  },
  role: {
    type: String,
    enum: ['admin', null],
    default: null,
  },
  registered_tests: [{
    test_id: {
      type: Schema.Types.ObjectId,
      ref: 'Test',
    },
    test_name: {
      type:String,
    },
    center_id: {
      type: Schema.Types.ObjectId,
      ref: 'Center',
    },
    city: {
      type: String,
      required: true,
    },
    state: {
      type: String,
      required: true,
    },
  }],
  given_tests: [{
    test_id: {
      type: Schema.Types.ObjectId,
      ref: 'Test',
    },
    score: {
      type: Number,
      required: true,
    },
    city: {
      type: String,
      required: true,
    },
    state: {
      type: String,
      required: true,
    },
  }],
});

module.exports = mongoose.model('User', userSchema);
