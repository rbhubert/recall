import { Component, OnInit, ViewChild } from "@angular/core";
import { UserService, User } from "../http/user.service";
import { ModelService } from "../http/model.service";
import { JobsService, Jobs } from "../http/jobs.service";
import { ApiService } from "../http/api.service";
import { Subscription } from "rxjs";
import { PageEvent, MatPaginator } from "@angular/material/paginator";
import { Clipboard } from "@angular/cdk/clipboard";

@Component({
	selector: "app-classification-loop",
	templateUrl: "./classification-loop.component.html",
	styleUrls: ["./classification-loop.component.css"],
	providers: [Clipboard],
})
export class ClassificationLoopComponent implements OnInit {
	@ViewChild(MatPaginator) paginator: MatPaginator;

	subscription_user: Subscription;
	subscription_model: Subscription;
	subscription_jobs: Subscription;

	model: string = "";
	user: User;
	jobs: Jobs;

	// MatPaginator Output
	pageEvent: PageEvent;
	length = 100;
	pageSize = 4;

	slider = 0.5;

	showPlotBoolean: boolean = false;
	columnsDocs = 30;

	documentsInRange = [];
	documentsToClassify = [];
	classifiedAsRelevants = [];
	classifiedAsNotRelevants = [];

	updateDocBoolean: boolean = false;
	updateTitle: string = "";
	updateText: string = "";
	updateDoc;

	graph = {
		data: [],
		layout: {},
	};

	constructor(
		private userService: UserService,
		private modelService: ModelService,
		private jobsService: JobsService,
		private apiService: ApiService,
		private clipboard: Clipboard
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

	getDocumentsInRange() {
		this.documentsInRange = [];
		this.documentsToClassify = [];

		this.apiService
			.getDocumentsInRange(this.model, this.slider)
			.subscribe((response) => {
				// response[0] is response code
				response = response[1];
				this.length = response["documents"].length;
				this.paginator.pageIndex = 0;

				response["documents"].forEach((element, index) => {
					console.log(element);
					if (
						element[this.model]["classification_label"] ===
						"no_relevant"
					) {
						element["classification_user"] = false;
					} else element["classification_user"] = true;

					element["probability"] =
						(
							element[this.model][
								"classification_probability"
							].toFixed(4) * 100
						)
							.toFixed(2)
							.toString() + "%";

					element["update"] = false;
					this.documentsInRange.push(element);
				});

				this.documentsToClassify = this.documentsInRange.slice(
					0,
					this.pageSize
				);
				console.log(this.documentsToClassify);
				console.log(this.documentsInRange);

			});
	}

	showPlot() {
		if (this.showPlotBoolean) {
			this.columnsDocs = 17;
		} else {
			if (!this.updateDoc) {
				this.columnsDocs = 30;
			}
		}
		this.apiService
			.getInformationPlot(this.model, true)
			.subscribe((response) => {
				this.__updatePlot(response["traces"]);
				this.__updateClassified(response["classified_by_user"]);
			});
	}

	__updateClassified(classified) {
		classified["relevants"].forEach((element, index) => {
			var new_element = {
				title: element["title"],
				url: element["url"],
			};
			this.classifiedAsRelevants.push(new_element);
		});
		classified["not_relevants"].forEach((element, index) => {
			var new_element = {
				title: element["title"],
				url: element["url"],
			};
			this.classifiedAsNotRelevants.push(new_element);
		});
	}

	__updatePlot(traces) {
		console.log("Updating plot...");

		var num_rel = traces["number_relevants"];
		var num_no_rel = traces["number_no_relevants"];
		var total = num_rel + num_no_rel;

		var text_rel = "Relevant (" + num_rel + ")";
		var text_no_rel = "Not relevant (" + num_no_rel + ")";

		var trace_user = "Classification by user (" + total + ")";

		var trace_model =
			"Classification by model (" + traces["number_model"] + ")";

		this.graph = {
			data: [
				{
					x: traces["trace_model"]["x"],
					y: traces["trace_model"]["y"],
					mode: "markers",
					type: "scatter",
					name: trace_model,
					text: traces["trace_model"]["text"],
					marker: { size: 2 },
				},
				{
					x: traces["trace_user"]["x"],
					y: traces["trace_user"]["y"],
					mode: "markers",
					type: "scatter",
					name: trace_user,
					text: traces["trace_user"]["text"],
					marker: { size: 3 },
				},
			],

			layout: {
				xaxis: {
					tickmode: "array",
					tickvals: [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1],
					ticktext: [
						text_no_rel,
						"10%",
						"25%",
						"50%",
						"75%",
						"90%",
						text_rel,
					],
					zeroline: false,
				},
				// xaxis: {
				// 	range: [-0.1, 1.1], // [0, 1]
				// },
				yaxis: {
					range: [0, traces["max_nwords"] + 10],
				},
				legend: {
					orientation: "h",
					yanchor: "bottom",
					y: 1.05,
					xanchor: "right",
					x: 0.8,
				},
			},
		};
	}

	nextPage(event) {
		var start = event.pageIndex * this.pageSize;
		var end = (event.pageIndex + 1) * this.pageSize;
		this.documentsToClassify = [];
		this.documentsToClassify = this.documentsInRange.slice(start, end);
	}

	updateInfoSection(document) {
		var isChecked = document.update;
		if (isChecked) {
			this.documentsToClassify.forEach((doc) => {
				doc.update = false;
			});
			document.update = true;
			this.updateDoc = true;
			this.columnsDocs = 17;
		} else {
			this.updateDoc = false;
			if (!this.showPlotBoolean) {
				this.columnsDocs = 30;
			}
		}

		this.updateDoc = document;
		this.updateTitle = document.title;
		this.updateText = document.content_text;
	}

	classifyDocuments() {
		this.apiService
			.classifyDocuments(this.model, this.documentsToClassify)
			.subscribe((response) => {
				var job_classifying = response.toString();
				this.jobsService.addIDClassifying(job_classifying);
			});
	}

	addClassificationByModel() {
		if (this.graph["data"].length == 5) {
			return;
		}

		this.apiService
			.getInformationPlot(this.model, false)
			.subscribe((response) => {
				var trace_relevant = {
					x: response["trace_relevant"]["x"],
					y: response["trace_relevant"]["y"],
					mode: "markers",
					type: "scatter",
					name: "Relevants classification",
					text: response["trace_relevant"]["text"],
					marker: { size: 3 },
				};

				var trace_no_relevant = {
					x: response["trace_no_relevant"]["x"],
					y: response["trace_no_relevant"]["y"],
					mode: "markers",
					type: "scatter",
					name: "Not relevants classification",
					text: response["trace_no_relevant"]["text"],
					marker: { size: 3 },
				};
				// relevant
				this.graph["data"].push(trace_relevant);
				// no relevant
				this.graph["data"].push(trace_no_relevant);
			});
	}

	copyDocumentsToClassify() {
		var valueToCopy = "";
		this.documentsToClassify.forEach((element, index) => {
			valueToCopy = valueToCopy + "\n\r" + element["url"];
		});

		this.__copyToClipboard(valueToCopy);
	}

	copyRelevants() {
		var valueToCopy = "";
		this.classifiedAsRelevants.forEach((element, index) => {
			valueToCopy = valueToCopy + "\n\r" + element["url"];
		});

		this.__copyToClipboard(valueToCopy);
	}

	copyNotRelevants() {
		var valueToCopy = "";
		this.classifiedAsNotRelevants.forEach((element, index) => {
			valueToCopy = valueToCopy + "\n\r" + element["url"];
		});

		this.__copyToClipboard(valueToCopy);
	}

	__copyToClipboard(text) {
		this.clipboard.copy(text);
	}

	updateDocument() {
		var url = this.updateDocument["url"];
		this.apiService
			.updateDocument(url, this.updateTitle, this.updateText)
			.subscribe((response) => {
				console.log("Document information updated");
			});
	}
}
