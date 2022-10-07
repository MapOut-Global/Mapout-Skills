require('dotenv').config();
const Model = require('./Model/model');
const express = require('express');
const router = express.Router()
const mongoose = require('mongoose');
//const mongoString = process.env.DATABASE_URL;
const mongoString = "mongodb+srv://mapout:mapout@mapoutdb.hj2on.mongodb.net/mapout-staging?authSource=admin&replicaSet=atlas-1389yt-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true"

mongoose.connect(mongoString);
const database = mongoose.connection;

database.on('error', (error) => {
    console.log(error)
})

database.once('connected', () => {
    console.log('Database Connected');
})

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
