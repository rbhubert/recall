import { BrowserModule } from "@angular/platform-browser";
import { NgModule } from "@angular/core";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
//import { NoopAnimationsModule } from "@angular/platform-browser/animations";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { SearchQueryComponent } from "./search-query/search-query.component";

import { FormsModule } from "@angular/forms";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatSelectModule } from "@angular/material/select";
import { MatInputModule } from "@angular/material/input";
import { MatButtonModule } from "@angular/material/button";
import { HttpClientModule } from "@angular/common/http";
import { MatGridListModule } from "@angular/material/grid-list";
import { MatCardModule } from "@angular/material/card";
import { MatIconModule } from "@angular/material/icon";
import { MatExpansionModule } from "@angular/material/expansion";
import { MatRadioModule } from "@angular/material/radio";
import { MatDividerModule } from "@angular/material/divider";
import { MatListModule } from "@angular/material/list";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import { MatBadgeModule } from "@angular/material/badge";
import { ClipboardModule } from "@angular/cdk/clipboard";
import { MatSliderModule } from "@angular/material/slider";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatPaginatorModule } from "@angular/material/paginator";

import * as PlotlyJS from "plotly.js/dist/plotly.js";
import { PlotlyModule } from "angular-plotly.js";
import { TrainModelComponent } from './train-model/train-model.component';
import { ClassificationLoopComponent } from './classification-loop/classification-loop.component';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
    declarations: [AppComponent, SearchQueryComponent, TrainModelComponent, ClassificationLoopComponent],
    imports: [
        BrowserModule,
        AppRoutingModule,
        //  NoopAnimationsModule,
        BrowserAnimationsModule,
        FormsModule,
        MatSelectModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        HttpClientModule,
        MatGridListModule,
        MatCardModule,
        MatIconModule,
        MatExpansionModule,
        MatRadioModule,
        MatDividerModule,
        MatListModule,
        MatProgressSpinnerModule,
        MatSlideToggleModule,
        PlotlyModule,
        MatBadgeModule,
        ClipboardModule,
        MatTooltipModule,
        MatSliderModule,
        MatCheckboxModule,
        MatPaginatorModule,
    ],
    providers: [],
    bootstrap: [AppComponent],
})
export class AppModule {}
