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
const checkactionverb = require("../controllers/check-action-verbs/action-verbs.js")

router.get("/", (req, res) => {
  res.send("Mapout Skills application");
});

router.get("/api/professiontoskill", professiontoskill);
router.post("/api/skills", parseSkill);
router.post("/api/resume", parseResume);
router.post("/api/employScore", getScore);
router.post("/api/getExperience", getExperience.API);
router.post("/api/skillsExtraction", skillsExtraction);
router.get("/get/resume/:name", resumeViewer);
router.get("/delete/resume", resumeDelete);
router.get("/delete/resume", resumeDelete);
router.post("/cicd/build", cicd);
router.post("/api/sample", offline);
//router.post("/api/timetrial", trial); 
//router.post("/api/skill2vec", skill2vec)
router.post("/api/resumeParser", resumeParser);
router.get("/api/checkactionverb", checkactionverb)

module.exports = router;
