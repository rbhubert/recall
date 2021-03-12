import { Component, OnInit } from "@angular/core";
import { UserService, User } from "../http/user.service";
import { ApiService } from "../http/api.service";
import { MatDialogRef } from "@angular/material/dialog";
import { Subscription } from "rxjs";

@Component({
	selector: "app-dialog-user",
	templateUrl: "./dialog-user.component.html",
	styleUrls: ["./dialog-user.component.css"],
})
export class DialogUserComponent implements OnInit {
	user: User;
	subscription: Subscription;

	f_username: string = "";
	error_message: string = "";

	constructor(
		private userService: UserService,
		private apiService: ApiService,
		public dialogRef: MatDialogRef<DialogUserComponent>
	) {}

	ngOnInit() {
		this.subscription = this.userService.user$.subscribe(
			(user) => (this.user = user)
		);
	}

	ngOnDestroy() {
		this.subscription.unsubscribe();
	}

	changeUser() {
		this.userService.changeMessage(this.user);
	}

	checkUsername() {
		this.apiService.getUser(this.f_username).subscribe((response) => {
			response = response["user_info"];
			var code = response[0];
			var info = response[1];

			if (code == 0) {
				this.error_message = info;
			} else {
				this.user = info;
				this.error_message = "";
				this.changeUser();
				this.closeDialog();
			}
		});
	}

	closeDialog() {
		this.dialogRef.close();
	}
}
