const fs = require("fs");

module.exports = async (req, res) => {
  const directoryPath = __basedir + "/resources/temp/resume/";
  let fileInfos = [];
  // 10 minutes before time
  const thresholdTime = Date.now() - 10 * 60 * 1000;

  fs.readdir(directoryPath, (err, files) => {
    if (err) {
      return res.status(500).send({
        message: "Unable to scan files!"
      });
    }

    files.forEach((file) => {
      fileInfos.push(file);
    });

    for (let i = 0; i < fileInfos.length; i++) {
      const fileTime = fileInfos[i].split(".pdf")[0];
      if (fileTime <= thresholdTime) {
        fs.rmSync(directoryPath + fileInfos[i], {
          force: true
        });
      }
    }

    console.log("/delete/resume", fileInfos);

    res.status(200).send(fileInfos);
  });
};
