import { Component, OnInit, Input } from '@angular/core';
import { IVSeries, Stock } from '../../option-result.model';
import { sprintf } from 'sprintf-js';
import { toPublicName } from '@angular/compiler/src/i18n/serializers/xmb';

@Component({
  selector: 'app-stock-summary',
  templateUrl: './stock-summary.component.html',
  styleUrls: ['./stock-summary.component.css']
})
export class StockSummaryComponent implements OnInit {
  
  @Input() stock: Stock;
  @Input() ivSeries: IVSeries;
  @Input() selectedDate: Date;

  constructor() { }

  ngOnInit() {
  }

  getStockName(stock: Stock): string{
    if(stock != null)
      return stock.name;
    else return 'N/A';
  }

  getFormattedDate(selectedDate: Date): string{
    if(selectedDate != null)
      return selectedDate.toLocaleDateString();
    else return "N/A";
  }

  formatNumber(num: number): string{
    if(num == null) return 'N/A';
    else return  sprintf("%.5f", num);
  }

  getCurrentPrice(stock: Stock, selectedDate: Date): number{
    if(stock != null && stock.historyList != null){
      let stockhist = stock.historyList.find(x => x.priceDate.getTime() == selectedDate.getTime());
      if(stockhist != null) return stockhist.adjClosePrice;
      else return null;
    }
    else return null;
  }

  getOpeningPrice(stock: Stock, selectedDate: Date): number{
    if(stock != null && stock.historyList != null){
      let stockhist = stock.historyList.find(x => x.priceDate.getTime() == selectedDate.getTime());
      if(stockhist != null) return stockhist.openPrice;
      else return null;
    }
    else return null;
  }

  getDailyHigh(stock: Stock, selectedDate: Date): number{
    if(stock != null && stock.historyList != null){
      let stockhist = stock.historyList.find(x => x.priceDate.getTime() == selectedDate.getTime());
      if(stockhist != null) return stockhist.dailyHigh;
      else return null;
    }
    else return null;
  }

  getDailyLow(stock: Stock, selectedDate: Date): number{
    if(stock != null && stock.historyList != null){
      let stockhist = stock.historyList.find(x => x.priceDate.getTime() == selectedDate.getTime());
      if(stockhist != null) return stockhist.dailyLow;
      else return null;
    }
    else return null;
  }

  getVolume(stock: Stock, selectedDate: Date): number{
    if(stock != null && stock.historyList != null){
      let stockhist = stock.historyList.find(x => x.priceDate.getTime() == selectedDate.getTime());
      if(stockhist != null) return stockhist.volume;
      else return null;
    }
    else return null;
  }

  getCurrentIV(ivseries: IVSeries, selectedDate: Date): number{
    //console.log(ivseries);
    if(ivseries != null){
      let tp = ivseries.timePointList.find(x => x.date.getTime() == selectedDate.getTime());
      if(tp != null) return tp.value;
      else return null;
    }
    else return null;
  }

  getStatsCount(stock: Stock, selectedDate: Date, month: number): number{
    if(stock != null && stock.historyList != null){
      var sDate = new Date(selectedDate);
      sDate.setMonth(sDate.getMonth() - month)
      return stock.historyList.filter(x => x.priceDate.getTime() >= sDate.getTime()).length;
    }
    else return null;
  }

  getStatsMax(stock: Stock, selectedDate: Date, month: number): number{
    //console.log(stock);
    if(stock != null){
      var sDate = new Date(selectedDate);
      sDate.setMonth(sDate.getMonth() - month)
      let result= Math.max(...stock.historyList.filter(x => x.priceDate.getTime() >= sDate.getTime()).map(x=> x.adjClosePrice));
      return result;
    }
    else return null;
  }

  getStatsMin(stock: Stock, selectedDate: Date, month: number): number{
    if(stock != null){
      var sDate = new Date(selectedDate);
      sDate.setMonth(sDate.getMonth() - month)
      let result= Math.min(...stock.historyList.filter(x => x.priceDate.getTime() >= sDate.getTime()).map(x=> x.adjClosePrice));
      return result;
    }
    else return null;
  }

  getStatsAvg(stock: Stock, selectedDate: Date, month: number): number{
    if(stock != null){
      var sDate = new Date(selectedDate);
      sDate.setMonth(sDate.getMonth() - month);
      let filteredHistoryList = stock.historyList.filter(x => x.priceDate.getTime() >= sDate.getTime());

      let avg = filteredHistoryList.map(x=>x.adjClosePrice).reduce((prev, cur) => prev+cur) / filteredHistoryList.length;
      return avg;
    }
    else return null;
  }

  getStatsStd(stock: Stock, selectedDate: Date, month: number): number{
    if(stock != null){
      let avgInt = this.getStatsAvg(stock, selectedDate, month);
      var sDate = new Date(selectedDate);
      sDate.setMonth(sDate.getMonth() - month);
      let filteredHistoryList = stock.historyList.filter(x => x.priceDate.getTime() >= sDate.getTime());

      let squareDiff = filteredHistoryList.map(x => (x.adjClosePrice-avgInt) * (x.adjClosePrice-avgInt))
      let avgSquareDiff = squareDiff.reduce((prev, cur) => prev+cur) / squareDiff.length;
      let result = Math.sqrt(avgSquareDiff);

      return result;
    }
    else return null;
  }

}
