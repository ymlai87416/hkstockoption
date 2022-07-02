import { 
  Component,
  OnInit,
  Output,
  EventEmitter,
  ElementRef,
  Inject,
  ViewChild
} from '@angular/core';
import { DatepickerMode} from 'ng2-semantic-ui';

import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/do';
import 'rxjs/add/operator/switch';
import { Observable } from 'rxjs/Rx';

import { IVSeries, StockOptionUnderlyingAsset, Stock, StockStatistics, HKOption } from '../../option-result.model';
import { OptionService } from '../../option-service.service';

@Component({
  selector: 'app-option-iv-query-form',
  templateUrl: './option-iv-query-form.component.html',
  styleUrls: ['./option-iv-query-form.component.css']
})
export class OptionIvQueryFormComponent implements OnInit {
  @Output() loading: EventEmitter<boolean> = new EventEmitter<boolean>();
  @Output() ivseriesResult: EventEmitter<IVSeries[]> = new EventEmitter<IVSeries[]>();
  @Output() priceResult: EventEmitter<Stock> = new EventEmitter<Stock>();
  @Output() selectedDate: EventEmitter<Date> = new EventEmitter<Date>();
  @Output() error: EventEmitter<boolean> = new EventEmitter<boolean>();
 
  mode: DatepickerMode;
  date: Date;
  underlyingAssetList: HKOption[];
  selectedAsset: HKOption;
  timeRange: number;

  @ViewChild('search') button;

  constructor(
    private optionService: OptionService,) {
    this.mode = DatepickerMode.Date;
    this.underlyingAssetList = null;
    this.selectedAsset = null;
    this.timeRange = 3;
  }

  ngOnInit() {
    console.log(this.button);

    this.optionService.getUnderlyingAssetList().subscribe(
      (results: HKOption[]) => { // on sucesss
        this.loading.emit(false);
        this.underlyingAssetList = results;
        this.selectedAsset = this.underlyingAssetList[0];
      },
      (err: any) => { // on error
        console.log(err);
        this.loading.emit(false);
      },
      () => { // on completion
        this.loading.emit(false);
      }
      
    )

    Observable.fromEvent(this.button.nativeElement, 'click')
      .map((e: any) => { let obj = {asset: this.selectedAsset, date: this.date, timeRange: this.timeRange}; return obj;}) // extract the value of the input
      .filter(query => query["asset"] != null && query["date"] != null ) // filter out if empty
      .debounceTime(250)                         // only once every 250ms
      .do(() => this.loading.emit(true))         // enable loading
      // search, discarding old events if new input comes in
      .map((query) => {
        console.log("Button clicked!");
        let asset = query["asset"] as HKOption;
        let date = query["date"] as Date;
        let timeRange = query["timeRange"] as number;
        var sDate = new Date(date);
        sDate.setMonth(sDate.getMonth()-timeRange)
        let ivResultOb = this.optionService.searchIvSeriesBySehkCode(asset.ticker, sDate, date);
        let stockResultOb = this.optionService.searchStockBySehkCode(asset.ticker, date, date);
        let dateOb = Observable.of(date);
        let result = Observable.zip(ivResultOb, stockResultOb, dateOb,
          (a, b, c) => {
            let combine = {ivResult: a, stockResult: b, queryDate: c};
            return combine;
          }
        );

        return result;
      })
      .switch()
      // act on the return of the search
      .subscribe(
        (results) => { // on sucesss
          this.loading.emit(false);

          let ivResult = results["ivResult"] as IVSeries[];
          let stockResult = results["stockResult"] as Stock[];
          let queryDate = results["queryDate"] as Date;

          if(this.validate(ivResult, stockResult, queryDate)){
            this.ivseriesResult.emit(ivResult);
            this.priceResult.emit(stockResult[0]);
            this.selectedDate.emit(queryDate);
            this.error.emit(false);
          }
          else{
            this.ivseriesResult.emit(null);
            this.priceResult.emit(null);
            this.selectedDate.emit(null);
            this.error.emit(true);
          }

          console.log(results);
        },
        (err: any) => { // on error
          console.log(err);
          this.loading.emit(false);
        },
        () => { // on completion
          this.loading.emit(false);
        }
      );
  }

  isActive(month: number): boolean{
    return month == this.timeRange;
  }

  setTimeRange(month: number): void{
    console.log(month);
    this.timeRange= month;
  }

  validate(ivResultList: IVSeries[], stockResult: Stock[], queryDate: Date): boolean{
    if(ivResultList != null && stockResult != null){
      if(stockResult.length > 0){
        let hasPrice = stockResult[0].historyList != null && stockResult[0].historyList.find(x => x.priceDate.getTime() == queryDate.getTime()) != null;
        let ivResult = ivResultList.find(x => x.seriesName.includes("IV"));
        let ivHasPrice;
        if(ivResult != null)
          ivHasPrice  = ivResult.timePointList.find(x => x.date.getTime() == queryDate.getTime()) != null;
        else
          ivHasPrice = null;

        return hasPrice && ivHasPrice;
      }
      else return false;
    }
    else return false;
  }
}
