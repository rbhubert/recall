import { Component, OnInit, Inject, ViewChild } from "@angular/core";
import { FormControl } from "@angular/forms";
import { UserService, User } from "../http/user.service";
import { ModelService } from "../http/model.service";
import { JobsService, Jobs } from "../http/jobs.service";
import { ApiService } from "../http/api.service";
import { Clipboard } from "@angular/cdk/clipboard";
import { PageEvent, MatPaginator } from "@angular/material/paginator";
import { Subscription } from "rxjs";

interface searchSources {
	name: string;
	viewValue: string;
	value: number;
}

@Component({
	selector: "app-search-query",
	templateUrl: "./search-query.component.html",
	styleUrls: ["./search-query.component.css"],
	providers: [Clipboard],
})
export class SearchQueryComponent implements OnInit {
	subscription_user: Subscription;
	subscription_model: Subscription;
	subscription_jobs: Subscription;

	model: string = "";
	user: User;
	jobs: Jobs;

	sources: searchSources[] = [
		{ name: "google", viewValue: "Google", value: 0 },
		{ name: "reddit", viewValue: "Reddit", value: 1 },
		{ name: "twitter", viewValue: "Twitter", value: 2 },
	];

	searchOrigin = 0;
	query: string = "";
	searchSource: string = "";

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

	searchQuery() {
		this.apiService
			.searchQuery(this.model, this.searchSource, this.query)
			.subscribe((response) => {
				var job_searching = response.toString();
				this.jobsService.addIDSearching(job_searching);
			});
	}

	queryFormIsCorrect() {
		return (
			this.searchSource != "" &&
			this.query != "" &&
			this.jobs.searching === ""
		);
	}
}
