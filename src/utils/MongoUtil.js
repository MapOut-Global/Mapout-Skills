const mongoose = require('mongoose');
const eventEmitter = require('../services/events/config');
require('dotenv').config()

var uri = `${process.env.MONGODB_URI}`;

mongoose.connect(
  uri,
  {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  },
  (err) => {
    if (err) {
      console.log('Mongoose failed to connect:', err.message);
      return eventEmitter.emit('mongo_failed');
    }
    console.log('Mongoose connected');
    return eventEmitter.emit('mongo_success');
  }
);

module.exports = mongoose;