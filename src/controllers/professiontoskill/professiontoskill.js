require('dotenv').config();
const Model = require('./Model/model');
const express = require('express');
const router = express.Router()
const db = require("../../utils/MongoUtil")

const toProfessionDTO = (profession) => ({
    _id: profession._id,
    profession: profession.profession,
    necessary_skills: profession.necessary_skills,
    helpful_skills: profession.helpful_skills,
});

module.exports = {
    async getByName(req, res) {
        try {
            const data = await Model
                .findOne({"profession": req.query.profession})
                .lean();

            res.json(toProfessionDTO(data));
        } catch (error) {
            res.status(500).json({message: error.message})
        }
    },

    async getById(req, res) {
        try {
            const data = await Model.findById(req.params.id).lean();

            return res.json(toProfessionDTO(data));
        } catch (e) {
            res.status(500).json({message: error.message})
        }
    }
};
