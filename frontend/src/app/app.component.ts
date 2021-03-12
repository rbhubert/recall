import { Component, Inject } from "@angular/core";
import {
	MatDialog,
	MatDialogRef,
	MAT_DIALOG_DATA,
} from "@angular/material/dialog";
import { UserService } from "./http/user.service";
import { ModelService } from "./http/model.service";

import { Subscription } from "rxjs";

import { DialogUserComponent } from "./dialog-user/dialog-user.component";

@Component({
	selector: "app-root",
	templateUrl: "./app.component.html",
	styleUrls: ["./app.component.css"],
})
export class AppComponent {
	title = "frontendAL";
	subscription_user: Subscription;
	subscription_model: Subscription;

	user: string;
	user_selected: boolean = false;

	model: string;

	constructor(
		private dialog: MatDialog,
		private userService: UserService,
		private modelService: ModelService
	) {}

	ngOnInit() {
		this.subscription_user = this.userService.user$.subscribe((user) => {
			if (user != null) {
				this.user = user.username;
				this.user_selected = true;
			}
		});

		this.subscription_model = this.modelService.model$.subscribe(
			(model) => {
				this.model = model;
			}
		);
	}

	// This open the dialog right away
	ngAfterViewInit() {
		if (this.user == null) {
			setTimeout(() => {
				const dialogRef = this.dialog.open(DialogUserComponent, {
					width: "250px",
					disableClose: true,
				});
			}, 0);
		}
	}

	changeUser() {
		const dialogRef = this.dialog.open(DialogUserComponent, {
			width: "250px",
		});
	}
}
