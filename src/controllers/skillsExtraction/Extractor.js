const { PythonShell } = require("python-shell");

module.exports = async (req, res) => {
  console.log("/api/skill-extraction  | ", req.body);
  try {
    let { inference_text } = req.body;

    let options = {
      mode: "text",
      pythonOptions: ["-u"],
      pythonPath: "python3",
      args: [inference_text]
    };

    const result = await new Promise((resolve, reject) => {
      PythonShell.run("./src/controllers/skillsExtraction/skillExtraction.py", options, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);
        }
      });
    });

    res.status(200).send({ status: true, data: result });
  } catch (error) {
    console.error(error.message);
    res.status(500).send({
      status: false,
      message: "Something went wrong",
      error: error.message
    });
  }
};
