module.exports = async (req, res) => {
  const fileName = await req.params.name;
  console.log("resume-viewer |", fileName);
  const directoryPath = __basedir + "/resources/temp/resume/";

  res.sendFile(directoryPath + fileName, fileName, (err) => {
    if (err) {
      console.error(err);
      res.status(500).send({
        status: false,
        message: "Something went wrong",
        error: err.message
      });
    }
  });
};
