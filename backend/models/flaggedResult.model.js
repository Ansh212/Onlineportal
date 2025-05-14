const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const flaggedResultSchema = new Schema({
  test_id: {
    type: Schema.Types.ObjectId,
    ref: 'Test',
    required: true,
  },
  flagged_users: [
    {
      type: Schema.Types.ObjectId,
      ref: 'User',
    },
  ],
  flagged_centers: [
    {
      type: Schema.Types.ObjectId,
      ref: 'Center',
    },
  ],
  flagged_date: {
    type: Date,
    default: Date.now,
  },
  summary: {
    total_registered: { type: Number, default: 0 },
    total_given: { type: Number, default: 0 },
    total_not_given: { type: Number, default: 0 },
    total_flagged: { type: Number, default: 0 },
  },
});

module.exports = mongoose.model('FlaggedResult', flaggedResultSchema);
