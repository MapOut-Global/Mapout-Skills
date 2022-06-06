const { PythonShell } = require("python-shell");

module.exports = async (req , res) => {

  try {
    var text = req.query.text
    let options = {
      mode: "text",
      pythonOptions: ["-u"],
      pythonPath: "python3",
      args: [text] 
      
    };  

    const result = await new Promise((resolve, reject) => {
      PythonShell.run("./src/controllers/check-action-verbs/action-verbs.py", options, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);  
        }
      });
    });
    res.status(200).send({ status: true, data: result });  
  }
   catch (error) {
    console.error(error.message);
    res.status(500).send({
      status: false,
      message: "Something went wrong",
      error: error.message
    });
  }
};


