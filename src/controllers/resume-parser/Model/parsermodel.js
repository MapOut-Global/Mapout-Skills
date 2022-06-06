const mongoose = require('mongoose');

const Schema = mongoose.Schema;

const resumeParserSchema = new Schema(
  {
    user_id: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    education: {
      type: Object,
    },
    technical_skills: {
      type: Array,
    },
    soft_skills: {
      type: Array,
    },
    experience: {
      type: Object
    },
    soft_skills_accuracy: {
      type: Number,
    },
    technical_skills_accuracy: {
      type: Number,
    },
    education_accuracy: {
      type: Number,
    },
    experience_accuracy: {
      type: Number,
    },
    dates_accuracy: {
      type: Number,
    },
    overall_accuracy: {
      type: Number,
    }

  },
  { timestamps: true }
);

resumeParserSchema.index({ user_id: 1 }, { unique: true });

const parsedData = mongoose.model('parsedData', resumeParserSchema, 'parserAccuracy');

module.exports = parsedData;
