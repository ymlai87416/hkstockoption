import * as moment from 'moment';

function _convertStringToDate(input: string): Date {
    let result = moment(input).toDate();
    return result;
}

function _fieldValue(obj: any, field: string){
    if(obj[field] != undefined)
        return obj[field];
    else return null;
}

export class StockOption {
    id: number;
    ticker: string;
    name: string;
    historyList: StockOptionHistory[];
    optionType: string;
    strikePrice: number;
    dateTime: Date;

    constructor(obj? : any){
        if(obj != null){
            this.id = _fieldValue(obj, "id"); 
            this.ticker = _fieldValue(obj, "ticker");
            this.name = _fieldValue(obj, "name");
            this.historyList = _fieldValue(obj, "historyList");
            this.optionType = _fieldValue(obj, "optionType");
            this.strikePrice = _fieldValue(obj, "strikePrice");
            this.dateTime = _convertStringToDate(_fieldValue(obj, "dateTime"));
        }
    }
}

//TODO: this class init method screw 0 value
export class StockOptionHistory {
    id: number;
    stockOptionId: number;
    priceDate: Date;
    openPrice: number;
    dailyHigh: number;
    dailyLow: number;
    settlePrice: number;
    openInterest: number;
    iv: number;

    constructor(obj?: any){
        if(obj != null){
            this.id = _fieldValue(obj, "id");
            this.stockOptionId = _fieldValue(obj, "stockOptionId");
            this.priceDate = _convertStringToDate(_fieldValue(obj, "priceDate"));
            this.openPrice = _fieldValue(obj, "openPrice");
            this.dailyHigh = _fieldValue(obj, "dailyHigh");
            this.dailyLow = _fieldValue(obj, "dailyLow");
            this.settlePrice = _fieldValue(obj, "settlePrice");
            this.openInterest = _fieldValue(obj, "openInterest");
            this.iv = _fieldValue(obj, "iv");
        }
    }
}

export class Stock {
    id: number;
    ticker: string;
    name: string;
    historyList: StockHistory[];
    sehkCode: number;

    constructor(obj? : any){
        this.id = obj && obj.id || null;
        this.ticker = obj && obj.ticker || null;
        this.name = obj && obj.name || null;
        this.sehkCode = obj && obj.sehkCode || null;
        this.historyList = obj && obj.historyList || null;
    }
}

export class StockHistory{
    id: number;
    stockId: number;
    priceDate: Date;
    openPrice: number;
    dailyHigh: number;
    dailyLow: number;
    closePrice: number;
    adjClosePrice: number;
    volume: number;

    constructor(obj?: any){
        this.id = obj && obj.id || null;
        this.stockId = obj && obj.stockId || null;
        this.priceDate = obj && _convertStringToDate(obj.priceDate) || null;
        this.openPrice = obj && obj.openPrice || null;
        this.dailyHigh = obj && obj.dailyHigh || null;
        this.dailyLow = obj && obj.dailyLow || null;
        this.closePrice = obj && obj.closePrice || null;
        this.adjClosePrice = obj && obj.adjClosePrice || null;
        this.volume = obj && obj.volume || null;
    }
}

export class StockStatistics{
    stockId: number;
    startDate: Date;
    endDate: Date;
    minPrice: number;
    maxPrice: number;
    meanPrice: number;
    stdPrice: number;

    constructor(obj?: any){
        this.stockId = obj && obj.stockId || null;
        this.startDate = obj && _convertStringToDate(obj.startDate) || null; 
        this.endDate = obj && _convertStringToDate(obj.endDate) || null;
        this.minPrice = obj && obj.minPrice || null;
        this.maxPrice = obj && obj.maxPrice || null;
        this.meanPrice = obj && obj.meanPrice || null;
        this.stdPrice = obj && obj.stdPrice || null;
    }
}

export class IVSeries{
    id: number;
    seriesName: string;
    timePointList: IVSeriesTimePoint[];

    constructor(obj?: any){
        this.id = obj && obj.id || null; 
        this.seriesName = obj && obj.seriesName || null;
        this.timePointList = obj && obj.timePointList || null;
    }
}

export class IVSeriesTimePoint{
    id: number;
    date: Date;
    value: number;

    constructor(obj?: any){
        this.id = obj && obj.id || null;
        this.date = obj && _convertStringToDate(obj.date) || null;
        this.value = obj && obj.value || null;
    }
}

export class StockOptionUnderlyingAsset{
    id: number;
    ticker: string;
    shortForm: string;
    fullName: string;

    constructor(obj?: any){
        this.id = obj && obj.id || null;
        this.ticker = obj && obj.ticker ||  null;
        this.shortForm = obj && obj.shortForm || null;
        this.fullName = obj && obj.fullName || null;
    }
}

export class HKOption{
    ticker: string;
    hkatsCode: string;
    name: string;

    constructor(obj?: any){
        this.ticker = obj && obj.ticker ||  null;
        this.hkatsCode = obj && obj.hkatscode || null;
        this.name = obj && obj.name || null;
    }
}