import { Component, OnInit, Input } from '@angular/core';
import { IVSeries, Stock } from '../../option-result.model';
import { sprintf } from 'sprintf-js';

@Component({
  selector: 'app-implied-volatility-summary',
  templateUrl: './implied-volatility-summary.component.html',
  styleUrls: ['./implied-volatility-summary.component.css']
})
export class ImpliedVolatilitySummaryComponent implements OnInit {
  @Input() ivseriesResult: IVSeries[];
  @Input() priceResult: Stock;
  @Input() selectedDate: Date;

  constructor() { }

  ngOnInit() {
  }

  getStockName(priceResult: Stock) : string{
    if(priceResult != null)
      return priceResult.name;
    else return "";
  }

  getFormattedDate(selectedDate: Date): string{
    if(selectedDate != null)
      return selectedDate.toLocaleDateString();
    else return "";
  }

  getClosingPrice(priceResult: Stock): string{
    if(priceResult != null && priceResult.historyList != null && priceResult.historyList.length >= 1)
      return priceResult.historyList[0].adjClosePrice.toString();
    else return "N/A";
  }

  getOpeningPrice(priceResult: Stock): string{
    if(priceResult != null && priceResult.historyList != null && priceResult.historyList.length >= 1)
      return priceResult.historyList[0].openPrice.toString();
    else return "N/A";
  }

  getDailyHigh(priceResult: Stock): string{
    if(priceResult != null && priceResult.historyList != null && priceResult.historyList.length >= 1)
      return priceResult.historyList[0].dailyHigh.toString();
    else return "N/A";
  }

  getDailyLow(priceResult: Stock): string{
    if(priceResult != null && priceResult.historyList != null && priceResult.historyList.length >= 1)
      return priceResult.historyList[0].dailyLow.toString();
    else return "N/A";
  }

  getVolume(priceResult: Stock): string{
    if(priceResult != null && priceResult.historyList != null && priceResult.historyList.length >= 1){
      return priceResult.historyList[0].volume.toString();
    }
    else return "N/A";
  }

  getIvSeries(result: IVSeries[], filter: string) : IVSeries{
    if(this.ivseriesResult != null){
      let ivseries = this.ivseriesResult.find(x => x.seriesName.includes("IV"));
      if(ivseries != null)
        return ivseries;
      else return null;
    }
    else
      return null;
  }

  getCurrent(targetSeries: IVSeries): string{
    if (targetSeries != null){
      let tp = targetSeries.timePointList.find(x => x.date.getTime() == this.selectedDate.getTime())
      if (tp != null)
        return sprintf("%.5f", tp.value);
      else
        return "N/A";
    }
    else return "N/A";
  }

  getStatsCount(targetSeries: IVSeries): string{
    if (targetSeries != null){
      return targetSeries.timePointList.length.toString();
    }
    else return "N/A";
  }

  getStatsMax(targetSeries: IVSeries): string{
    if (targetSeries != null){
      let result= Math.max(...targetSeries.timePointList.map(x=> x.value));
      return sprintf("%.5f", result);
    }
    else return "N/A";
  }

  getStatsMin(targetSeries: IVSeries): string{
    if (targetSeries != null){
      let result = Math.min(...targetSeries.timePointList.map(x=> x.value));
      return sprintf("%.5f", result);
    }
    else return "N/A";
  }

  getStatsAvg(targetSeries: IVSeries): string{
    if (targetSeries != null){
      let avg = targetSeries.timePointList.map(x=>x.value).reduce((prev, cur) => prev+cur) / targetSeries.timePointList.length;
      return sprintf("%.5f", avg);
    }
    else return "N/A";
  }

  getStatsStd(targetSeries: IVSeries): string{
    if (targetSeries != null){
      let avgInt = Number.parseFloat(this.getStatsAvg(targetSeries));
      let squareDiff = targetSeries.timePointList.map(x => (x.value-avgInt) * (x.value-avgInt))
      let avgSquareDiff = squareDiff.reduce((prev, cur) => prev+cur) / squareDiff.length;
      let result = Math.sqrt(avgSquareDiff);
      return sprintf("%.5f", result);
    }
    else return "N/A";
  }
  
}
