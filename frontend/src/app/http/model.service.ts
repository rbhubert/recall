import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";

@Injectable({
	providedIn: "root",
})
export class ModelService {
	private model = new BehaviorSubject<string>("");
	model$ = this.model.asObservable();

	constructor() {}

	changeMessage(model: string) {
		this.model.next(model);
	}
}
