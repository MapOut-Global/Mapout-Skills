const getSkillScore = require("./skills/skill2vec");
const getDegreeScore = require("./degree/degree");

module.exports = async (req, res) => {
  const { cv, jd } = req.body;
  console.log("/api/employScore", req.body);
  try {
    let scores = new Array();
    for (let i = 0; i < jd.length; i++) {
      const _score = await calculateScore(cv, jd[i]);
      scores.push(_score);
    }
    return res.status(200).send({ status: true, score: scores });
  } catch (error) {
    console.error(error);
    res.status(500).send({
      status: false,
      message: "Something went wrong!",
      error: error.message
    });
  }
};

// Calculates final score
const calculateScore = async (cv, jd) => {
  try {
    let yearScore = 0;
    let industryScore = 0;
    let degreeScore = 0;

    cv.experience = Number(cv.experience);

    const condition = cv.experience;
    const minExpYear = Number(getMinYear(jd.experience));
    const weightage = getWeightage(condition);

    // Gets skill_score from python script
    let skillScore = (await getSkillScore(cv.skills, jd.skills)) || 0;
    skillScore = adjustPyValues(skillScore);

    // Gets degree_score from python script
    degreeScore = await getDegreeScore(cv, jd);
    jd.degreeScore = degreeScore;

    if (jd.experience != "" && condition >= minExpYear) {
      yearScore = experienceNormalize(minExpYear, cv.experience);
    }

    const { skillWeight, degreeWeight, yearWeight, industryWeight } = weightDistribute(jd, weightage);

    // Experience [0,3]
    if (condition <= 3) {
      skillScore = Number(skillScore) * skillWeight;
      degreeScore = Number(degreeScore) * degreeWeight;

      if (condition >= minExpYear) {
        yearScore = yearScore * yearWeight;
      }
      if (cv.industry == jd.industry) {
        industryScore = industryWeight;
      }
    }
    // Experience (3,8)
    else if (condition > 3 && condition < 8) {
      skillScore = Number(skillScore) * skillWeight;
      degreeScore = Number(degreeScore) * degreeWeight;

      if (condition >= minExpYear) {
        yearScore = yearScore * yearWeight;
      }
      if (cv.industry == jd.industry) {
        industryScore = industryWeight;
      }
    }
    // Experience (7+)
    else {
      skillScore = Number(skillScore) * skillWeight;
      degreeScore = Number(degreeScore) * degreeWeight;

      if (condition >= minExpYear) {
        yearScore = yearScore * yearWeight;
      }
      if (cv.industry == jd.industry) {
        industryScore = industryWeight;
      }
    }

    let scoreObj = {};

    const totalScore = yearScore + degreeScore + industryScore + skillScore;

    scoreObj.skillScore = skillScore;
    scoreObj.totalScore = totalScore;

    if (yearWeight) {
      scoreObj.yearScore = yearScore;
    }
    if (degreeWeight) {
      scoreObj.degreeScore = degreeScore;
    }
    if (industryWeight) {
      scoreObj.industryScore = industryScore;
    }

    return scoreObj;
  } catch (error) {
    throw error;
  }
};

// Normalise years of experience
const getMinYear = (data) => {
  // 3+ -> 4
  if (data.match(/\d+\+/)) {
    const minYears = data.match(/\d+/);
    return Number(minYears[0]) + 1;
  }
  // 1-3 -> 1
  else if (data.match(/\d+\-\d+/)) {
    const minYears = data.match(/\d+/);
    return Number(minYears[0]);
  }
  // 1 -> 1
  else {
    return data;
  }
};

// Returns weightage according to condition
const getWeightage = (condition) => {
  let weightage = new Object();

  if (condition <= 3) {
    weightage = {
      skillWeight: 40,
      degreeWeight: 40,
      yearWeight: 10,
      industryWeight: 10
    };
    return weightage;
  } else if (condition > 3 && condition < 8) {
    weightage = {
      skillWeight: 40,
      degreeWeight: 30,
      yearWeight: 15,
      industryWeight: 15
    };
    return weightage;
  } else {
    weightage = {
      skillWeight: 40,
      degreeWeight: 10,
      yearWeight: 25,
      industryWeight: 25
    };
    return weightage;
  }
};

// Adjusting value according to range
const adjustPyValues = (val) => {
  if (val < 0.65) {
    return val * 0.33;
  } else if (val >= 0.65 && val <= 0.85) {
    return val * 0.66;
  } else {
    return val;
  }
};

// Checks missing [experience/qualifications/industry] in JD
const missingKeys = (jd) => {
  let keys = new Array();

  if (jd.experience == "") {
    keys.push("experience");
  }
  if (jd.industry == "") {
    keys.push("industry");
  }
  if (jd.degreeScore == 0) {
    keys.push("qualifications");
  }

  return keys;
};

// Weightage distribution when missing [experience/qualifications/industry] in JD
const weightDistribute = (jd, weightage) => {
  const missKeys = missingKeys(jd);

  let { skillWeight, degreeWeight, yearWeight, industryWeight } = weightage;

  switch (missKeys.length) {
    case 1:
      let equaliser;
      const key = missKeys[0];
      if (key == "experience") {
        equaliser = yearWeight / 3;
        skillWeight += equaliser;
        industryWeight += equaliser;
        degreeWeight += equaliser;
        yearWeight = 0;
        return { skillWeight, degreeWeight, yearWeight, industryWeight };
      } else if (key == "qualifications") {
        equaliser = degreeWeight / 3;
        skillWeight += equaliser;
        industryWeight += equaliser;
        yearWeight += equaliser;
        degreeWeight = 0;
        return { skillWeight, degreeWeight, yearWeight, industryWeight };
      } else {
        equaliser = industryWeight / 3;
        skillWeight += equaliser;
        yearWeight += equaliser;
        degreeWeight += equaliser;
        industryWeight = 0;
        return { skillWeight, degreeWeight, yearWeight, industryWeight };
      }
    case 2:
      let equaliser1, equaliser2;
      if (missKeys.join(",") == "experience,industry") {
        equaliser1 = yearWeight / 2;
        equaliser2 = industryWeight / 2;
        skillWeight += equaliser1 + equaliser2;
        degreeWeight += equaliser1 + equaliser2;
        industryWeight = 0;
        yearWeight = 0;
        return { skillWeight, degreeWeight, yearWeight, industryWeight };
      } else if (missKeys.join(",") == "industry,qualifications") {
        equaliser1 = industryWeight / 2;
        equaliser2 = degreeWeight / 2;
        skillWeight += equaliser1 + equaliser2;
        yearWeight += equaliser1 + equaliser2;
        industryWeight = 0;
        degreeWeight = 0;
        return { skillWeight, degreeWeight, yearWeight, industryWeight };
      } else {
        equaliser1 = yearWeight / 2;
        equaliser2 = degreeWeight / 2;
        skillWeight += equaliser1 + equaliser2;
        industryWeight += equaliser1 + equaliser2;
        yearWeight = 0;
        degreeWeight = 0;
        return { skillWeight, degreeWeight, yearWeight, industryWeight };
      }
    case 3:
      skillWeight = 100;
      industryWeight = 0;
      yearWeight = 0;
      degreeWeight = 0;
      return { skillWeight, degreeWeight, yearWeight, industryWeight };
    default:
      return weightage;
  }
};

// CV experience normalization -> [0,1]
const experienceNormalize = (jd_exp, cv_exp) => {
  const k = 15;
  const pLower = 0;
  const pUpper = 1;
  const diff = Math.abs(jd_exp - cv_exp);

  const pValue = pLower - Math.pow(Math.exp(1), -(diff / k)) * (pLower - pUpper);

  return pValue;
};
