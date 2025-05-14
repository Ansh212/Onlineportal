// models/center.model.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const centerSchema = new Schema({
  city: {
    type: String,
    required: true,
  },
  state: {
    type: String,
    required: true,
  },
});

module.exports = mongoose.model('Center', centerSchema);
