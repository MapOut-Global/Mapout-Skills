const Model = require('./src/controllers/professiontoskill/Model/model');
const mongoose = require('mongoose')
const express = require("express");
const cors = require("cors");
const morgan = require('morgan');

const indexRouter = require("./src/routes/index");
require("./services/redis/config");

const app = express();

global.__basedir = __dirname;

app.use(morgan('dev'));
app.use(cors());
app.use(express.json());
app.use(indexRouter);

module.exports = app;
