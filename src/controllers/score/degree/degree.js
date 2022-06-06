const { json } = require("express");
const { PythonShell } = require("python-shell");
const abbreviations = require("./abbrevations.json");
const pyDegrees = require("./script-degrees.json");

module.exports = async (cv, jd) => {
  try {
    const degreeArr = [getDegree(cv.qualifications), getDegree(jd.qualifications)];

    let cvDegrees = degreeArr[0];
    let jdDegrees = degreeArr[1];

    if (cvDegrees.length > 0 && jdDegrees.length > 0) {
      let options = {
        mode: "text",
        pythonOptions: ["-u"],
        pythonPath: "python3",
        args: degreeArr
      };

      const result = await new Promise((resolve, reject) => {
        PythonShell.run("./src/controllers/score/degree/degrees_proxomity.py", options, (err, result) => {
          if (err) {
            reject(err);
          } else {
            resolve(result[0]);
          }
        });
      });

      return result;
    } else if (cvDegrees.length == 0 || jdDegrees.length == 0) {
      if (cvDegrees.length == 0 && cv.industry) {
        cvDegrees.push(cv.industry);

        let options = {
          mode: "text",
          pythonOptions: ["-u"],
          pythonPath: "python3",
          args: degreeArr
        };

        const result = await new Promise((resolve, reject) => {
          PythonShell.run("./src/controllers/score/degree/degrees_proxomity.py", options, (err, result) => {
            if (err) {
              reject(err);
            } else {
              resolve(result[0]);
            }
          });
        });

        return result;
      } else if (jdDegrees.length == 0 && jd.industry) {
        jdDegrees.push(jd.industry);

        let options = {
          mode: "text",
          pythonOptions: ["-u"],
          pythonPath: "python3",
          args: degreeArr
        };

        const result = await new Promise((resolve, reject) => {
          PythonShell.run("./src/controllers/score/degree/degrees_proxomity.py", options, (err, result) => {
            if (err) {
              reject(err);
            } else {
              resolve(result[0]);
            }
          });
        });

        return result;
      } else {
        return 0;
      }
    } else {
      if (cvDegrees.length == 0 && jdDegrees.length == 0 && cv.industry && jd.industry) {
        cvDegrees.push(cv.industry);
        jdDegrees.push(jd.industry);

        let options = {
          mode: "text",
          pythonOptions: ["-u"],
          pythonPath: "python3",
          args: degreeArr
        };

        const result = await new Promise((resolve, reject) => {
          PythonShell.run("./src/controllers/score/degree/degrees_proxomity.py", options, (err, result) => {
            if (err) {
              reject(err);
            } else {
              resolve(result[0]);
            }
          });
        });

        return result;
      } else {
        return 0;
      }
    }
  } catch (error) {
    console.error("degreeScore", error);
    return 0;
    // throw error;
  }
};

const getDegree = (degreeArr) => {
  let degrees = new Array();

  degreeArr.forEach((degree) => {
    for (i = 0; i < abbreviations.length; i++) {
      let o = abbreviations[i];
      if (degree.match(new RegExp(o), "i") && pyDegrees.includes(degree)) {
        degrees.push(degree);
        break;
      } else if (o.abbreviation.includes(degree) && pyDegrees.includes(o.degree)) {
        degrees.push(o.degree);
        break;
      }
    }
  });

  return degrees;
};
