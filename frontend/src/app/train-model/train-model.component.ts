import { Component, OnInit } from "@angular/core";
import { UserService, User } from "../http/user.service";
import { ModelService } from "../http/model.service";
import { JobsService, Jobs } from "../http/jobs.service";
import { ApiService } from "../http/api.service";

import { Subscription } from "rxjs";

@Component({
	selector: "app-train-model",
	templateUrl: "./train-model.component.html",
	styleUrls: ["./train-model.component.css"],
	providers: [],
})
export class TrainModelComponent implements OnInit {
	subscription_user: Subscription;
	subscription_model: Subscription;
	subscription_jobs: Subscription;

	model: string = "";
	user: User;
	jobs: Jobs;
	allModels: string[] = [];

	createModelForm = 0;
	selectedModel: string;

	newModelName: string = "";
	relevantDocs: string = "";
	noRelevantDocs: string = "";

	constructor(
		private userService: UserService,
		private modelService: ModelService,
		private jobsService: JobsService,
		private apiService: ApiService
	) {}

	ngOnInit(): void {
		this.subscription_user = this.userService.user$.subscribe((user) => {
			if (user != null) {
				this.user = user;
				this.getModels();
			}
		});

		this.subscription_model = this.modelService.model$.subscribe(
			(model) => {
				this.model = model;
			}
		);

		this.subscription_jobs = this.jobsService.jobs$.subscribe((jobs) => {
			this.jobs = jobs;
		});
	}

	getModels() {
		this.allModels = this.user.models;
	}

	selectModel() {
		this.modelService.changeMessage(this.selectedModel);

		this.apiService.loadModel(this.model).subscribe((response) => {
			console.log("Load model correctly");
		});
	}

	trainModel() {
		var trainingDocs = [];

		let relDocs = this.relevantDocs.split("\n");

		relDocs.forEach((doc) => {
			trainingDocs.push([doc, "relevant"]);
		});

		let noRelDocs = this.noRelevantDocs.split("\n");

		noRelDocs.forEach((doc) => {
			trainingDocs.push([doc, "no_relevant"]);
		});

		this.apiService
			.createModel(this.newModelName, trainingDocs, this.user.username)
			.subscribe((response) => {
				var job_training = response.toString();
				this.jobsService.addIDTraining(job_training);
			});
	}

	createFormModelIsCorrect() {
		var lowerName = this.newModelName.toLowerCase();
		var existModel = this.allModels.some(
			(e) => e.toLowerCase() === lowerName
		);

		return !existModel && this.newModelName != "";
	}

	selectFormModelIsCorrect() {
		var change = this.selectedModel != this.model;
		return change && this.selectedModel != "";
	}

	toTrainFormIsCorrect() {
		return (
			this.createFormModelIsCorrect() &&
			this.relevantDocs != "" &&
			this.noRelevantDocs != ""
		);
	}
}
