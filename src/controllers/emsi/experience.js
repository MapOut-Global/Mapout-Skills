const keys = require("../../../resources/experience.keys");

const experience = async (desc) => {
  try {
    let descrption = await desc;
    descrption = descrption.replace(/[&\/\\#,.()$~%":*;?\n<>{}]/g, " ").trim();

    const match = descrption.toLowerCase().match(new RegExp(keys.join("|"), "g"));

    if (!match) return "";

    let arrYears = descrption.toLowerCase().split(` ${match[0]}`)[0].split(" ");

    let years = arrYears[arrYears.length - 1];

    if (years < 0) {
      return `${years * -1} years of experience`;
    }
    return `${checkKeyword(years)} years of experience`;
  } catch (error) {
    console.error(error);
    return "";
  }
};

const checkKeyword = (years) => {
  //noise1-2 Years of experience -> 1-2 Years of experience
  return years.replace(/[a-z]/gi, "");
};

module.exports = {
  API: async (req, res) => {
    try {
      const { desc } = req.body;
      const expYears = await experience(desc);

      res.status(200).send({
        status: true,
        experience: expYears
      });
    } catch (error) {
      console.error(error);
      res.status(500).send({
        status: false,
        message: "Something went wrong"
      });
    }
  },
  experience
};
