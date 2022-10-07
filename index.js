const app = require("./app");
const mongoose = require('mongoose')
const eventEmitter = require("./src/services/events/config");


const port = process.env.PORT || 4041;

eventEmitter.on("mongo_success", () => {
  app.listen(port, () => {
    console.log(`App running on http://localhost:${port}`);
  });
});

eventEmitter.on("mongo_failed", function () {
  process.exit();
});