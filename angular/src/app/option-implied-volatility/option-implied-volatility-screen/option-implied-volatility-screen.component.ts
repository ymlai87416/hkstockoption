

import { Component, OnInit } from '@angular/core';
import { IVSeries, Stock } from '../../option-result.model';

@Component({
  selector: 'app-option-implied-volatility-screen',
  templateUrl: './option-implied-volatility-screen.component.html',
  styleUrls: ['./option-implied-volatility-screen.component.css']
})
export class OptionImpliedVolatilityScreenComponent implements OnInit {

  loading: boolean;
  ivseriesResult: IVSeries[];
  priceResult: Stock;
  error: boolean;
  selectedDate: Date;

  constructor() {
    this.error = false;
    this.loading = false;
    this.ivseriesResult = null;
    this.priceResult = null;
    this.selectedDate = null;

    console.log(this.ivseriesResult == null || this.ivseriesResult == undefined);
  }

  ngOnInit() {
  }

  updateIvSeries(ivseriesResult: IVSeries[]){
    this.ivseriesResult = ivseriesResult;
  }

}
