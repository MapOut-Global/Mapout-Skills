const axios = require("axios");
const projects = require("./projects.json");

module.exports = async (req, res) => {
  try {
    const gitlab_token = req.headers["x-gitlab-token"];

    if (gitlab_token != "qQ40ViqfNaaCrSX247l2NvkijQKSi0")
      return res.status(401).send({
        status: false,
        message: "Unauthorised request"
      });

    const { object_attributes, project } = req.body;
    const { ref, status } = object_attributes;

    console.table({ project: project.name, ref, status });

    if (status == "failed" && ref == "db_migration" && project.id == "22941178") {
      await runPipeline(project.id);
    } else if (status == "failed" && ref == "development" && project.id == "22941031") {
      await runPipeline(project.id);
    }
    return res.status(200).send({ status: true });
  } catch (error) {
    console.error("error", error);
    res.status(500).send({
      status: false,
      message: "Something went wrong!",
      error: error.message
    });
  }
};

const runPipeline = async (project_id) => {
  try {
    const { ref, token } = projects[project_id];

    const config = {
      method: "post",
      url: `https://gitlab.com/api/v4/projects/22941031/ref/${ref}/trigger/pipeline?token=${token}`
    };

    await axios(config).then((o) => console.log(JSON.stringify(o.data)));
  } catch (error) {
    throw error;
  }
};
