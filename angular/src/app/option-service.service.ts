import { Injectable, Inject } from '@angular/core';
import {
  HttpClient,
  HttpRequest,
  HttpHeaders
} from '@angular/common/http';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map'

import {
  Stock, StockHistory, StockOption, StockOptionHistory,
  StockOptionUnderlyingAsset,
  IVSeries, IVSeriesTimePoint, HKOption,
} from './option-result.model';
import { sprintf } from 'sprintf-js';

//export const WEBSERVICE_ROOT = 'http://trade.ymlai87416.com/hkstockoption/api'
export const WEBSERVICE_ROOT = 'http://localhost:8080'
export const SEARCH_STOCK_BY_SEHK_CODE_URL = WEBSERVICE_ROOT + '/stock/%s';
export const SEARCH_STOCK_BY_SEHK_CODE_WITH_PARAM_URL = WEBSERVICE_ROOT + '/stock/%s?startDate=%s&endDate=%s';
export const SEARCH_STOCK_OPTION_BY_SEHK_CODE_URL = WEBSERVICE_ROOT + '/stockOption/sehk/%s';
export const SEARCH_STOCK_OPTION_BY_HKATS_CODE_URL = WEBSERVICE_ROOT + '/stockOption/hkats/%s';
export const SEARCH_STOCK_OPTION_BY_SEHK_CODE_WITH_PARAM_URL = WEBSERVICE_ROOT + '/stockOption/sehk/%s?startDate=%s&endDate=%s';
export const SEARCH_STOCK_OPTION_BY_HKATS_CODE_WITH_PARAM_URL = WEBSERVICE_ROOT + '/stockOption/hkats/%s?startDate=%s&endDate=%s';
export const SEARCH_STOCK_OPTION_BY_TICKER_URL = WEBSERVICE_ROOT + '/stockOption/code/%s';
export const SEARCH_STOCK_OPTION_BY_TICKER_WITH_PARAM_URL = WEBSERVICE_ROOT + '/stockOption/code/%s?startDate=%s&endDate=%s';
export const GET_UNDERLYING_ASSET_LIST_URL = WEBSERVICE_ROOT + '/stockOption/underlyingAsset';
export const SEARCH_IV_SERIES_BY_SEHK_CODE_URL = WEBSERVICE_ROOT + '/ivseries/%s';
export const SEARCH_IV_SERIES_BY_SEHK_CODE_WITH_PARAM_URL = WEBSERVICE_ROOT + '/ivseries/%s?startDate=%s&endDate=%s';

@Injectable({
  providedIn: 'root'
})
export class OptionService {

  constructor(
    private http: HttpClient,
    @Inject(SEARCH_STOCK_BY_SEHK_CODE_URL) private searchStockBySehkCodeUrl: string,
    @Inject(SEARCH_STOCK_BY_SEHK_CODE_WITH_PARAM_URL) private searchStockBySehkCodeWithParamUrl: string,
    @Inject(SEARCH_STOCK_OPTION_BY_SEHK_CODE_URL) private searchStockOptionBySehkCodeUrl: string,
    @Inject(SEARCH_STOCK_OPTION_BY_HKATS_CODE_URL) private searchStockOptionByHKATSCodeUrl: string,
    @Inject(SEARCH_STOCK_OPTION_BY_SEHK_CODE_WITH_PARAM_URL) private searchStockOptionBySehkCodeWithParamUrl: string,
    @Inject(SEARCH_STOCK_OPTION_BY_HKATS_CODE_WITH_PARAM_URL) private searchStockOptionByHKATSCodeWithParamUrl: string,
    @Inject(SEARCH_STOCK_OPTION_BY_TICKER_URL) private searchStockOptionByTickerUrl: string,
    @Inject(SEARCH_STOCK_OPTION_BY_TICKER_WITH_PARAM_URL) private searchStockOptionByTickerWithParamUrl: string,
    @Inject(GET_UNDERLYING_ASSET_LIST_URL) private getUnderlyingAssetListUrl: string,
    @Inject(SEARCH_IV_SERIES_BY_SEHK_CODE_URL) private searchIvSeriesBySehkCodeUrl: string,
    @Inject(SEARCH_IV_SERIES_BY_SEHK_CODE_WITH_PARAM_URL) private searchIvSeriesBySehkCodeWithParamUrl: string,
  ) {
    console.log("Option service created.");
  }

  dateToYMD(date: Date): string {
    var d = date.getDate();
    var m = date.getMonth() + 1; //Month from 0 to 11
    var y = date.getFullYear();
    return '' + y + (m<=9 ? '0' + m : m) + (d <= 9 ? '0' + d : d);
}

  searchStockBySehkCode(sehkCode: string, startDate?: Date, endDate?: Date): Observable<Stock[]> {
    let queryUrl: string;

    if (startDate != null){
      let startDateStr = this.dateToYMD(startDate);
      let endDateStr = this.dateToYMD(endDate);
      queryUrl = sprintf(this.searchStockBySehkCodeWithParamUrl, sehkCode, startDateStr, endDateStr);
    }
    else
      queryUrl = sprintf(this.searchStockBySehkCodeUrl, sehkCode);

    return this.http.get(queryUrl).map(response => {
      let responseArr = response as Stock[];
      return responseArr.map(item => {
        // console.log("raw item", item); // uncomment if you want to debug
        if (item.historyList)
          item.historyList = item.historyList.map(history => new StockHistory(history));
        return new Stock(item);
      });
    });
  }

  searchStockOptionBySehkCode(sehkCode: string, startDate?: Date, endDate?: Date): Observable<StockOption[]> {
    let queryUrl: string;

    if (startDate != null){
      let startDateStr = this.dateToYMD(startDate);
      let endDateStr = this.dateToYMD(endDate);
      queryUrl = sprintf(this.searchStockOptionBySehkCodeWithParamUrl, sehkCode, startDateStr, endDateStr);
    }
    else
      queryUrl = sprintf(this.searchStockOptionBySehkCodeUrl, sehkCode);

    return this.http.get(queryUrl).map(response => {
      let responseArr = response as StockOption[];
      return responseArr.map(item => {
        // console.log("raw item", item); // uncomment if you want to debug
        
        if (item.historyList){
          let newHistoryList = item.historyList.map(history => new StockOptionHistory(history));
          //console.log(item.historyList);
          //console.log(newHistoryList);
          item.historyList = newHistoryList;
        }
        let result= new StockOption(item);
        return result;
      });
    });
  }

  searchStockOptionByHKATSCode(hkatsCode: string, startDate?: Date, endDate?: Date): Observable<StockOption[]> {
    let queryUrl: string;

    if (startDate != null){
      let startDateStr = this.dateToYMD(startDate);
      let endDateStr = this.dateToYMD(endDate);
      queryUrl = sprintf(this.searchStockOptionByHKATSCodeWithParamUrl, hkatsCode, startDateStr, endDateStr);
    }
    else
      queryUrl = sprintf(this.searchStockOptionByHKATSCodeUrl, hkatsCode);

    return this.http.get(queryUrl).map(response => {
      let responseArr = response as StockOption[];
      return responseArr.map(item => {
        // console.log("raw item", item); // uncomment if you want to debug
        
        if (item.historyList){
          let newHistoryList = item.historyList.map(history => new StockOptionHistory(history));
          //console.log(item.historyList);
          //console.log(newHistoryList);
          item.historyList = newHistoryList;
        }
        let result= new StockOption(item);
        return result;
      });
    });
  }

  searchStockOptionByTicker(ticker: string, startDate?: Date, endDate?: Date): Observable<StockOption[]> {
    let queryUrl: string;

    if (startDate != null){
      let startDateStr = this.dateToYMD(startDate);
      let endDateStr = this.dateToYMD(endDate);
      queryUrl = sprintf(this.searchStockOptionByTickerWithParamUrl, ticker, startDateStr, endDateStr);
    }
    else
      queryUrl = sprintf(this.searchStockOptionByTickerUrl, ticker);

    return this.http.get(queryUrl).map(response => {
      let responseArr = response as StockOption[];
      return responseArr.map(item => {
        // console.log("raw item", item); // uncomment if you want to debug
        if (item.historyList)
          item.historyList = item.historyList.map(history => new StockOptionHistory(history));
        return new StockOption(item);
      });
    });
  }

  getUnderlyingAssetList(): Observable<HKOption[]> {
    return this.http.get(this.getUnderlyingAssetListUrl).map(response => {
      let responseArr = response as HKOption[];
      return responseArr.map(item => {
        return new HKOption(item);
      });
    });
  }

  searchIvSeriesBySehkCode(sehkCode: string, startDate?: Date, endDate?: Date): Observable<IVSeries[]> {
    let queryUrl: string;

    if (startDate != null){
      let startDateStr = this.dateToYMD(startDate);
      let endDateStr = this.dateToYMD(endDate);
      queryUrl = sprintf(this.searchIvSeriesBySehkCodeWithParamUrl, sehkCode, startDateStr, endDateStr);
    }
    else
      queryUrl = sprintf(this.searchIvSeriesBySehkCodeUrl, sehkCode);

    return this.http.get(queryUrl).map(response => {
      let responseArr = response as IVSeries[];
      return responseArr.map(item => {
        // console.log("raw item", item); // uncomment if you want to debug
        if (item.timePointList)
          item.timePointList = item.timePointList.map(history => new IVSeriesTimePoint(history));
        let result = new IVSeries(item); 
        return result;
      });
    });
  }
}
