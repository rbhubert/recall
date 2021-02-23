import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";
import { environment } from "../../environments/environment";

@Injectable({
	providedIn: "root",
})
export class ApiService {
	//url_base = "http://127.0.0.1:5000/";
	url_base = environment.api_url;

	constructor(private http: HttpClient) {}

	getJobsStatus(list_jobIDs) {
		var url = this.url_base + "task/" + list_jobIDs;
		return this.http.get(url);
	}

	getModels() {
		var url = this.url_base + "models";
		return this.http.get(url);
	}

	createModel(model_info) {
		var url = this.url_base + "model/" + model_info.model_name;

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("model_info", JSON.stringify(model_info));

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	selectModel(model_name) {
		var url = this.url_base + "model/" + model_name;
		return this.http.get(url);
	}

	trainModel(model_info, relevant_news, irrelevant_news) {
		var url = this.url_base + "train";

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("model_info", JSON.stringify(model_info));
		body = body.set("relevant_docs", relevant_news);
		body = body.set("irrelevant_docs", irrelevant_news);

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	searchQuery(model_info, source, query) {
		var url = this.url_base + "search/" + source;

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("model_info", JSON.stringify(model_info));
		body = body.set("query", query);

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	getDocumentsToClassify(model_info) {
		var url =
			this.url_base +
			"relevant/" +
			model_info.model_type_data +
			"/" +
			model_info.model_name;

		return this.http.get(url);
	}

	getDocumentsInRange(model_info, range) {
		var url =
			this.url_base +
			"relevant/" +
			model_info.model_type_data +
			"/" +
			model_info.model_name +
			"/" +
			range;

		return this.http.get(url);
	}

	documentsClassifiedByUser(model_info, documents) {
		var url =
			this.url_base +
			"classify/" +
			model_info.model_type_data +
			"/" +
			model_info.model_name;

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("documents", JSON.stringify(documents));

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	getInfoPlot(model_info) {
		var url =
			this.url_base +
			"plot/" +
			model_info.model_type_data +
			"/" +
			model_info.model_name;

		return this.http.get(url);
	}

	getClassifiedPlot(model_info) {
		var url =
			this.url_base +
			"plot/classified/" +
			model_info.model_type_data +
			"/" +
			model_info.model_name;

		return this.http.get(url);
	}
}
