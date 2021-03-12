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

	getUser(username) {
		var url = this.url_base + "user/" + username;
		return this.http.get(url);
	}

	createModel(modelName, documents, username) {
		var url = this.url_base + "model/" + modelName;

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("training_documents", JSON.stringify(documents));
		body = body.set("username", username);

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	loadModel(modelName) {
		var url = this.url_base + "model/" + modelName;

		return this.http.get(url);
	}

	searchQuery(modelName, searchSource, query) {
		var url = this.url_base + "search/" + searchSource + "/" + modelName;

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("query", query);

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	getDocumentsInRange(modelName, range) {
		var url = this.url_base + "documents_in_range/" + modelName + "/" + range;

		return this.http.get(url);
	}

	getInformationPlot(modelName, alreadyClassified) {
		var url = this.url_base + "plot/" + modelName + "/" + alreadyClassified;

		return this.http.get(url);
	}

	updateDocument(url_item, title, text) {
		var url = this.url_base + "update/";

		const myheader = new HttpHeaders().set(
			"Content-Type",
			"application/x-www-form-urlencoded"
		);
		let body = new HttpParams();
		body = body.set("url", url_item);
		body = body.set("title", title);
		body = body.set("text", text);

		return this.http.post(url, body, {
			headers: myheader,
		});
	}

	classifyDocuments(modelName, documents) {
		var url = this.url_base + "classify/" + modelName;

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
}
