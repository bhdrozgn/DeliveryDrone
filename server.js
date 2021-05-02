const express = require("express");
const mongoose = require("mongoose");

const app = express();

mongoose.connect("mongodb://admin:123456789@127.0.0.1:27017/fdrone", { 
	useNewUrlParser: true,
	useFindAndModify: false,
	useCreateIndex: true,
	useUnifiedTopology: true });

const Schema = mongoose.Schema;
const DroneSchema = new Schema({
    dId: {
        type: Number,
        unique: true
    },
	isAvailable: {
		type: Boolean,
		default: true
	},
	lat: {
		type: Number
	},
	long: {
		type: Number
	}
});

const Drone = mongoose.model("Drone", DroneSchema);

app.use(express.json());

app.post("/assign-drone", async (req, res, next) => {
	const { lat, long } = req.body;
	
	const availableDrone = await Drone.findOne({
		isAvailable: true
	});
	
	if (!availableDrone)
		return res.json({
			success: false,
			message: "No available drone"
		});
		
		
	availableDrone.lat = lat;
	availableDrone.long = long;
	await availableDrone.save();
	
	res.json({
		success: true,
		data: {
			dId: availableDrone.dId
		}
	});
});

app.get("/get-coords", {
	const dId = req.params;
	
	const drone = await Drone.findOne({
		dId
	});
	
	if (!drone)
		return res.json({
			success: false,
			message: "Not found"
		});
		
	res.json({
		lat: drone.lat,
		long: drone.long
	});
});

app.listen(process.env.PORT, () => {
    console.log(`App is started on ${process.env.PORT} with ${process.env.NODE_ENV} mode!`);
});
