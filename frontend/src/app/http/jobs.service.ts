import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";

export class Jobs {
	training: string;
	searching: string;
	classifying: string;

	constructor(train: string, search: string, classi: string) {
		this.training = train;
		this.searching = search;
		this.classifying = classi;
	}
}
@Injectable({
	providedIn: "root",
})
export class JobsService {
	private jobs = new BehaviorSubject<Jobs>(new Jobs("", "", ""));

	jobs$ = this.jobs.asObservable();

	constructor() {}

	changeMessage(jobs: Jobs) {
		sessionStorage.setItem("jobsIDs", JSON.stringify(jobs));
		this.jobs.next(jobs);
	}

	addIDTraining(training: string) {
		var actual_jobs = this.jobs.getValue();
		actual_jobs.training = training;
		this.changeMessage(actual_jobs);
	}

	addIDSearching(searching: string) {
		var actual_jobs = this.jobs.getValue();
		actual_jobs.searching = searching;
		this.changeMessage(actual_jobs);
	}

	addIDClassifying(classifying: string) {
		var actual_jobs = this.jobs.getValue();
		actual_jobs.classifying = classifying;
		this.changeMessage(actual_jobs);
	}

	removeID(type: string) {
		var actual_jobs = this.jobs.getValue();
		actual_jobs[type] = "";
		this.changeMessage(actual_jobs);
	}
}
