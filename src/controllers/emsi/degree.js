const keys = require("../../../resources/degree.keys");

module.exports = {
  degree: async (desc) => {
    try {
      let descrption = await desc;

      descrption = descrption
        .replace(/[&\/\\#,+()$~%":*?<>{}]/g, " ")
        .replace(/\MS Excel/gi, " ")
        .replace(/\MS Word/gi, " ")
        .replace(/\MS Office/gi, " ")
        .replace(/\MS SQL/gi, " ")
        .replace(/\  /g, " ");

      const degrees = keys.map((d) => {
        return d.degree;
      });

      let match = descrption.match(new RegExp(degrees.join("|"), "g"));

      //removes white spaces
      match = match
        ? match.map((word) => {
            return word.trim();
          })
        : [];

      //removes duplicates
      match = [...new Set(match)];

      //removes data if not found in degree.keys & gets complete object
      match = match.map((data) => {
        return keys.find((o) => o.degree == data);
      });

      return mapDegree(match.filter(Boolean));
    } catch (error) {
      console.error(error);
      return "";
    }
  }
};

const mapDegree = (matches) => {
  let minimum = [];
  let preferred = [];

  matches = matches.sort((a, b) => {
    return a.level - b.level;
  });

  const maxVal = matches[matches.length - 1];

  matches.forEach((o) => {
    if (o.level < maxVal.level) {
      minimum.push(o.degree);
    } else {
      preferred.push(o.degree);
    }
  });

  return { minimum, preferred };
};
