const { PythonShell } = require("python-shell");

module.exports = async (req , res) => {
//console.log("/api/resume-parser  | ", req.body);
//console.log("the link  :  ", req.body.url);
  try {
  
    var url = req.query.url
    //console.log("URL : ",url)
    let options = {
      mode: "text",
      pythonOptions: ["-u"],
      pythonPath: "python3",
      args: [url] 
      //args : ["https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/sample_resume_2021.pdf"]
    };  

    const result = await new Promise((resolve, reject) => {
      PythonShell.run("./src/controllers/resume-parser/resume_parser(offline).py", options, (err, result) => {
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
