require('dotenv').config();
const Model = require('./Model/model');
const express = require('express');
const router = express.Router()
const db = require("../../utils/MongoUtil")

module.exports = async (req, res) => {

  try {
    const data = await Model.findOne({"profession": req.query.profession});

    res.json({
      profession: data.profession,
      necessary_skills: data.necessary_skills,
      helpful_skills: data.helpful_skills
    })
  } catch (error) {
    res.status(500).json({message: error.message})
  }


}
