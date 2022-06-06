const { PythonShell } = require("python-shell");

module.exports = async (cv, jd) => {
  try {
    let options = {
      mode: "text",
      pythonOptions: ["-u"],
      pythonPath: "python3",
      // args: [["iOS", "Node.js", "Swift"],["iOS", "Python", "React.js"]]
      args: [getPyArray(cv), getPyArray(jd)]
    };

    const result = await new Promise((resolve, reject) => {
      PythonShell.run("./src/controllers/score/skills/skill2vec.py", options, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result[0]);
        }
      });
    });

    return result;
  } catch (error) {
    throw error;
  }
};

//removes text enclosed in bracket/replace spacing with _ /text in lowercase
const getPyArray = (array) => {
  return array.map((o) => {
    return o
      .replace(/\((.+?)\)/g, "")
      .trim()
      .replace(" ", "_")
      .toLowerCase();
  });
};
