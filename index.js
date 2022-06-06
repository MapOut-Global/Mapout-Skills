const app = require("./app");
const mongoose = require('mongoose')

const port = process.env.PORT || 4041;

app.listen(port, () => {
  console.log("App running on http://localhost:4041");
});
