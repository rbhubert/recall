import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";

export class User {
	username: string;
	models: string[];
}
@Injectable({
	providedIn: "root",
})
export class UserService {
	private user = new BehaviorSubject<User>(null as User);
	user$ = this.user.asObservable();

	constructor() {}

	ngOnInit() {
		var user = sessionStorage.getItem("user");
		if (user != null) {
			var obj = JSON.parse(user);
			this.changeMessage(obj);
		}

	}

	changeMessage(user: User) {
		sessionStorage.setItem("user", JSON.stringify(user));
		this.user.next(user);
	}
}
