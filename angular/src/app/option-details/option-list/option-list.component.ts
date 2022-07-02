import { Component, OnInit, Input } from '@angular/core';
import { StockOption } from '../../option-result.model';
import * as moment from 'moment';

@Component({
  selector: 'app-option-list',
  templateUrl: './option-list.component.html',
  styleUrls: ['./option-list.component.css']
})
export class OptionListComponent implements OnInit {

  @Input() 
  set stockOptionList(stockOptionList: StockOption[]){
    if(stockOptionList != null){
      this._stockOptionList = stockOptionList;
      this.refreshTable(stockOptionList);
    }

    console.log(this.callData);
  }

  refreshTable(stockOptionList: StockOption[]){
    let callStockOptionList = stockOptionList.filter(x => x.optionType == 'C');
    let putStockOptionList = stockOptionList.filter(x => x.optionType == 'P');
    this.priceList = stockOptionList.map(x => x.strikePrice).filter((v, i, a) => a.indexOf(v) === i).sort((a, b) => a-b); 
    let callMonthDateList = callStockOptionList.map(x => x.dateTime.getTime()).filter((v, i, a) => a.indexOf(v) === i).sort().map(x => new Date(x)); 
    let putMonthDateList = putStockOptionList.map(x => x.dateTime.getTime()).filter((v, i, a) => a.indexOf(v) === i).sort().map(x => new Date(x));
    
    this.callMonthList = callMonthDateList.map(x => this.formatOptionDate(x));
    this.putMonthList = putMonthDateList.map(x => this.formatOptionDate(x));

    this.callData = [];
    this.putData = [];

    for(var i=0; i<this.priceList.length; ++i){
      this.callData[i] = [];
      this.putData[i] = [];
      for(var j=0; j<callMonthDateList.length; ++j){
        let strikePrice = this.priceList[i];
        let month = callMonthDateList[j];
        let callStockOption = callStockOptionList.find(x => x.strikePrice == strikePrice && x.dateTime.getTime() == month.getTime() )
        //console.log(callStockOption);
        this.callData[i][j] = this.getDisplayInfo(callStockOption);
      }

      for(var j=0; j<putMonthDateList.length; ++j){
        let strikePrice = this.priceList[i];
        let month = putMonthDateList[j];
        let putStockOption = putStockOptionList.find(x => x.strikePrice == strikePrice && x.dateTime.getTime() == month.getTime() )

        this.putData[i][j] = this.getDisplayInfo(putStockOption);
      }
    }
  }

  getDisplayInfo(option: StockOption): number{
    if(option != null && option.historyList != null && option.historyList.length >=1 ){
      if(this.displayMode == 'price') return option.historyList[0].settlePrice;
      else return option.historyList[0].openInterest;
    }
    else return null;
  }

  _stockOptionList: StockOption[];
  priceList: number[];
  callMonthList: string[];
  putMonthList: string[];
  callData: number[][];
  putData: number[][];
  displayMode: string;
  
  constructor() {
    this.displayMode = 'price';
  }

  ngOnInit() {
  }

  formatOptionDate(date: Date){
    return moment(date).format('MMMYY');
  }

  setDisplayMode(mode: string): void{
    this.displayMode = mode;
    this.refreshTable(this._stockOptionList);
  }

}
