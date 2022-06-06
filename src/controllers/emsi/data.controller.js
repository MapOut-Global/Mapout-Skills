const { experience } = require("./experience");
const { job_type } = require("./job-type");
const { degree } = require("./degree");
const skills = require("./skills");

module.exports = async (req, res) => {
  try {
    const jobDesc = await req.body.desc;
    const skill = await skills(jobDesc);
    const qualification = await degree(jobDesc);
    const exp = await experience(jobDesc);
    const jobType = await job_type(jobDesc);

    console.log("/api/skills");

    res.status(200).send({
      jobType,
      qualification,
      experience: exp,
      skills: skill
    });
  } catch (error) {
    console.error(error);
    res.status(500).send("Something went wrong");
  }
};
