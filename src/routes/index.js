const express = require("express");
const router = new express.Router();
const mongoose = require('mongoose');
const Model = require('../controllers/professiontoskill/Model/model');

const parseSkill = require("../controllers/emsi/data.controller");
const parseResume = require("../controllers/resume-parser/resume.controller");
const getScore = require("../controllers/score/score.controller");
const getExperience = require("../controllers/emsi/experience");
const skillsExtraction = require("../controllers/skillsExtraction/Extractor.js");
const resumeViewer = require("../controllers/resume-parser/resume-viewer");
const resumeDelete = require("../controllers/resume-parser/resume-delete");
const cicd = require("../controllers/ci-cd/cicd.controller");
const resumeParser = require("../controllers/resume-parser/Parser.js");
const offline = require("../controllers/resume-parser/Parser_sample.js");
const professiontoskill = require("../controllers/professiontoskill/professiontoskill.js")
//const trial = require("../controllers/resume-parser/trial.js");
//const skill2vec = require("../controllers/score/skills/skill2vec.js");
const checkactionverb = require("../controllers/check-action-verbs/action-verbs.js");
const { search } = require("../controllers/professiontoskill/professionSearch");


router.get("/", (req, res) => {
  res.send("Mapout Skills application");
});

router.get("/skills/api/professiontoskill", professiontoskill.getByName);
router.get("/skills/api/professiontoskill/:id", professiontoskill.getById);
router.post("/skills/api/skills", parseSkill);
router.post("/skills/api/resume", parseResume);
router.post("/skills/api/employScore", getScore);
router.post("/skills/api/getExperience", getExperience.API);
router.post("/skills/api/skillsExtraction", skillsExtraction);
router.get("/skills/get/resume/:name", resumeViewer);
router.get("/skills/delete/resume", resumeDelete);
router.get("/skills/delete/resume", resumeDelete);
router.post("/skills/cicd/build", cicd);
router.post("/skills/api/sample", offline);
//router.post("/skills/api/timetrial", trial);
//router.post("/skills/api/skill2vec", skill2vec)
router.post("/skills/api/resumeParser", resumeParser);
router.get("/skills/api/checkactionverb", checkactionverb)

router.get("/skills/api/professions/search",search)


module.exports = router;
