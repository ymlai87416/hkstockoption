import { Component, OnInit } from '@angular/core';
import { 
  StockOption, 
  Stock, IVSeries
} from '../../option-result.model';

@Component({
  selector: 'app-option-details-screen',
  templateUrl: './option-details-screen.component.html',
  styleUrls: ['./option-details-screen.component.css']
})
export class OptionDetailsScreenComponent implements OnInit {
  stock: Stock;
  ivSeries: IVSeries;
  stockOptionList: StockOption[];
  selectedDate: Date;
  error: boolean;
  loading: boolean;

  constructor() {
    this.error = false;
    this.loading = false;
    this.ivSeries = null;
    this.stock = null;
    this.stockOptionList = null;
    this.selectedDate = null;
  }

  ngOnInit() {
  }

  isInCorrectState(): boolean{
    let result =  this.stock != null && this.selectedDate != null
      && this.stockOptionList != null;
   
    //check valid
    return result;
  }
}
