import { Component, OnInit, Inject, ViewChild } from "@angular/core";
import { FormControl } from "@angular/forms";
import { ApiService } from "../http/api.service";
import { Clipboard } from "@angular/cdk/clipboard";
import { PageEvent, MatPaginator } from "@angular/material/paginator";

interface sourceSearch {
	name: string;
	viewValue: string;
	value: number;
}

interface models {
	name: string;
	value: number;
}

interface jobs {
	training: string;
	searching: string;
	classifying_relevant: string;
}

type jobsKeys = keyof jobs;

@Component({
	selector: "app-search-query",
	templateUrl: "./search-query.component.html",
	styleUrls: ["./search-query.component.css"],
	providers: [Clipboard],
})
export class SearchQueryComponent implements OnInit {
	@ViewChild(MatPaginator) paginator: MatPaginator;

	sources: sourceSearch[] = [
		{ name: "google", viewValue: "Google", value: 0 },
		{ name: "reddit", viewValue: "Reddit", value: 1 },
		{ name: "twitter", viewValue: "Twitter", value: 2 },
	];

	length = 100;
	pageSize = 4;

	// MatPaginator Output
	pageEvent: PageEvent;

	models: models[] = [];

	f_isNewModel = 0;
	f_typeOfData;
	f_selectedModel: string = "";
	f_newModelName: string = "";

	f_relevantNews: string = "";
	f_irrelevantNews: string = "";

	f_search = 0;
	f_selectedSource: string = "";
	f_query: string = "";

	step = 0;

	selectedModel_package = {
		model_isnew: true,
		model_name: "",
		model_type_data: this.f_typeOfData,
	};
	selectedModel_correct: boolean = false;

	documents_in_range = [];
	documents_to_classify = [];
	classified_relevants = [];
	classified_not_relevants = [];

	value_copy_clipboard = "";

	jobIDs: jobs = {
		training: "",
		searching: "",
		classifying_relevant: "",
	};

	intervalToCheck;

	graph = {
		data: [],
		layout: {},
	};

	value_slider = 0.5;
	last_range = 0.5;
	show_plot = false;
	update_document = false;
	document_to_update;
	form_title;
	form_content;

	colsDocs = 30;

	constructor(private apiService: ApiService, private clipboard: Clipboard) {}

	ngOnInit(): void {
		var jids = sessionStorage.getItem("jobsIDs");
		if (jids != null) {
			this.jobIDs = JSON.parse(jids);
		}
		this.askForModels();
		this.intervalToCheck = setInterval(() => {
			this.checkJobID();
		}, 2000);
	}

	copyRelevants() {
		this.value_copy_clipboard = "";

		this.classified_relevants.forEach((element, index) => {
			this.value_copy_clipboard =
				this.value_copy_clipboard + "\n\r" + element["url"];
		});

		this.copyToClipboard();
	}

	copyNotRelevants() {
		this.value_copy_clipboard = "";

		this.classified_not_relevants.forEach((element, index) => {
			this.value_copy_clipboard =
				this.value_copy_clipboard + "\n\r" + element["url"];
		});

		this.copyToClipboard();
	}

	copyDocumentsToClassify() {
		this.value_copy_clipboard = "";

		this.documents_to_classify.forEach((element, index) => {
			this.value_copy_clipboard =
				this.value_copy_clipboard + "\n\r" + element["url"];
		});

		this.copyToClipboard();
	}

	copyToClipboard() {
		this.clipboard.copy(this.value_copy_clipboard);
	}

	updateClassified(classified) {
		classified["relevants"].forEach((element, index) => {
			var new_element = {
				title: element["title"],
				url: element["url"],
			};
			this.classified_relevants.push(new_element);
		});
		classified["not_relevants"].forEach((element, index) => {
			var new_element = {
				title: element["title"],
				url: element["url"],
			};
			this.classified_not_relevants.push(new_element);
		});
	}

	updatePlot(traces) {
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

	checkJobID() {
		if (
			this.jobIDs.training === "" &&
			this.jobIDs.searching === "" &&
			this.jobIDs.classifying_relevant === ""
		) {
			return;
		}

		var keys_jobs = Object.keys(this.jobIDs);
		for (let entry of keys_jobs) {
			var value = this.jobIDs[entry];
			if (value === "") {
				continue;
			}
			this.apiService.getJobsStatus(value).subscribe((response) => {
				if (response["data"]["task_status"] === "finished") {
					this.jobIDs[entry] = "";
					sessionStorage.setItem(
						"jobsIDs",
						JSON.stringify(this.jobIDs)
					);

					if (entry === "classifying_relevant") {
						this.updatePlot(response["traces"]);
					}
				}
			});
		}
	}

	askForModels() {
		this.apiService.getModels().subscribe((response) => {
			this.models = [];
			response["models"].forEach((element, index) => {
				this.models.push({ name: element, value: index });
			});
		});
	}

	searchQuery() {
		this.apiService
			.searchQuery(
				this.selectedModel_package,
				this.f_selectedSource,
				this.f_query
			)
			.subscribe((response) => {
				this.jobIDs.searching = response.toString();
				sessionStorage.setItem("jobsIDs", JSON.stringify(this.jobIDs));
			});
	}

	createModel() {
		this.selectedModel_package = {
			model_isnew: true,
			model_name: this.f_newModelName,
			model_type_data: this.f_typeOfData,
		};
		this.apiService
			.createModel(this.selectedModel_package)
			.subscribe((response) => {
				this.selectedModel_correct = true;
				console.log("Modelo creado correctamente");
			});
	}

	selectModel() {
		this.apiService
			.selectModel(this.f_selectedModel)
			.subscribe((response) => {
				var typeData = response["model_info"]["data_type"];
				this.selectedModel_package = {
					model_isnew: false,
					model_name: this.f_selectedModel,
					model_type_data: typeData,
				};
				this.selectedModel_correct = true;

				this.update_document = false;
				this.document_to_update = "";
				this.form_title = "";
				this.form_content = "";

				this.value_slider = 0.5;
				this.last_range = 0.5;

				this.callFirstForDocuments();

				if (this.show_plot) {
					this.showPlot();
				}

				console.log("Modelo seleccionado correctamente");
			});
	}

	trainModel() {
		this.apiService
			.trainModel(
				this.selectedModel_package,
				this.f_relevantNews,
				this.f_irrelevantNews
			)
			.subscribe((response) => {
				this.jobIDs.training = response.toString();
				sessionStorage.setItem("jobsIDs", JSON.stringify(this.jobIDs));
			});
	}

	getDocumentsToClassify() {
		this.documents_to_classify = [];

		this.apiService
			.getDocumentsToClassify(this.selectedModel_package)
			.subscribe((response) => {
				this.updateClassified(response["classified_by_user"]);
				this.updatePlot(response["traces"]);
				response["documents"].forEach((element, index) => {
					if (
						element["classification_by_model"][
							"classification_value"
						] === "no_relevant"
					) {
						element["classification_user"] = false;
					} else element["classification_user"] = true;

					element["probability"] =
						(
							element["classification_by_model"][
								"classification_probability"
							].toFixed(4) * 100
						)
							.toFixed(2)
							.toString() + "%";

					this.documents_to_classify.push(element);
				});
			});
	}

	classifyDocuments() {
		this.apiService
			.documentsClassifiedByUser(
				this.selectedModel_package,
				this.documents_to_classify
			)
			.subscribe((response) => {
				this.jobIDs.classifying_relevant = response.toString();
				sessionStorage.setItem("jobsIDs", JSON.stringify(this.jobIDs));
			});
	}

	setStep(index: number) {
		this.step = index;
	}

	nextStep() {
		this.step++;
	}

	prevStep() {
		this.step--;
	}

	createFormModelIsCorrect() {
		var change =
			this.f_newModelName != this.selectedModel_package.model_name;
		var existModel = this.models.some(
			(e) => e.name === this.f_newModelName
		);

		return (
			change &&
			!existModel &&
			this.f_newModelName != "" &&
			this.f_typeOfData != undefined
		);
	}

	selectFormModelIsCorrect() {
		var change =
			this.f_selectedModel != this.selectedModel_package.model_name;
		return change && this.f_selectedModel != "";
	}

	relevantNewsFormIsCorrect() {
		return (
			this.selectedModel_correct &&
			this.f_relevantNews != "" &&
			this.f_irrelevantNews != ""
		);
	}

	queryFormIsCorrect() {
		return (
			this.selectedModel_correct &&
			this.f_query != "" &&
			this.f_selectedSource != "" &&
			this.jobIDs.searching === ""
		);
	}

	updateInfoSection(document) {
		var is_checked = document.update;
		if (is_checked) {
			this.documents_to_classify.forEach((doc) => {
				doc.update = false;
			});
			document.update = true;
			this.update_document = true;
			this.colsDocs = 17;
		} else {
			this.update_document = false;
			if (!this.show_plot) {
				this.colsDocs = 30;
			}
		}

		this.document_to_update = document;
		this.form_title = document.title;
		this.form_content = document.content_text;
	}

	updateInfoDocument(document, title, content) {
		console.log(document);
		console.log(title);
		console.log(content);
	}

	showPlot() {
		if (this.show_plot) {
			this.colsDocs = 17;
		} else {
			if (!this.update_document) {
				this.colsDocs = 30;
			}
		}
		this.apiService
			.getInfoPlot(this.selectedModel_package)
			.subscribe((response) => {
				console.log(response);
				this.updatePlot(response["traces"]);
				this.updateClassified(response["classified_by_user"]);
			});
	}

	callForDocuments(range) {
		this.last_range = range;
		this.documents_to_classify = [];
		this.documents_in_range = [];

		this.apiService
			.getDocumentsInRange(this.selectedModel_package, range)
			.subscribe((response) => {
				this.length = response["documents"].length;
				this.paginator.pageIndex = 0;

				response["documents"].forEach((element, index) => {
					if (
						element["classification_by_model"][
							"classification_value"
						] === "no_relevant"
					) {
						element["classification_user"] = false;
					} else element["classification_user"] = true;

					element["probability"] =
						(
							element["classification_by_model"][
								"classification_probability"
							].toFixed(4) * 100
						)
							.toFixed(2)
							.toString() + "%";

					element["update"] = false;
					this.documents_in_range.push(element);
				});

				this.documents_to_classify = this.documents_in_range.slice(
					0,
					4
				);
			});
	}

	callFirstForDocuments() {
		// Firs time opening mat expansion panel #2
		this.setStep(2);
		this.callForDocuments(0.5);
	}

	changeToClassify(event) {
		var start = event.pageIndex * this.pageSize;
		var end = (event.pageIndex + 1) * this.pageSize;
		this.documents_to_classify = [];
		this.documents_to_classify = this.documents_in_range.slice(start, end);
	}

	addClassificationByModel() {
		if (this.graph["data"].length == 5) {
			return;
		}

		this.apiService
			.getClassifiedPlot(this.selectedModel_package)
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
}
