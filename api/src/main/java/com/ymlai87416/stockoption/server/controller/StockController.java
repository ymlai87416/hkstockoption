package com.ymlai87416.stockoption.server.controller;

import com.ymlai87416.stockoption.server.domain.DailyPrice;
import com.ymlai87416.stockoption.server.domain.Symbol;
import com.ymlai87416.stockoption.server.model.*;
import com.ymlai87416.stockoption.server.service.*;
import com.ymlai87416.stockoption.server.utilities.Utilities;
import org.apache.commons.math3.stat.descriptive.moment.StandardDeviation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

//import javax.rmi.CORBA.Util;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("hkstockoption/api")
public class StockController {

    /**
     * findBySEHKCode                       : /stock/{id}
     * findBySEHKCodeWithHistory            : /stock/{id}?history=1
     * getStockStatistic                    : /stock/{id}/stats?toDate=yyyymmdd
     */

    private SymbolRepository symbolRepository;
    private DailyPriceRepository dailyPriceRepository;

    @Autowired
    private StockController(SymbolRepository symbolRepository,
                            DailyPriceRepository dailyPriceRepository

    ){
        this.symbolRepository = symbolRepository;
        this.dailyPriceRepository = dailyPriceRepository;
    }

    final String HK_STOCK = "HK STOCK";

    @RequestMapping("/stock/{id}")
    @CrossOrigin(origins={"http://localhost:4200", "https://trade.ymlai87416.com"})
    public List<Stock> findStockBySEHKCode(@PathVariable String id,
                                           @RequestParam(value="startDate", required=false) String startDate,
                                           @RequestParam(value="endDate", required=false) String endDate)
    {
        List<Symbol> searchResult = symbolRepository.findByInstrumentAndTicker(HK_STOCK, id);
        List<DailyPrice> childSearchResult = null;

        Date[] startEndDate = Utilities.parseStartDateAndEndDate(startDate, endDate);

        boolean initChild = false;
        if(startEndDate != null && startEndDate.length == 2
                && startEndDate[0] != null && startEndDate[1] != null){

            childSearchResult = dailyPriceRepository.findBySymbolInAndPriceDateBetween(searchResult,
                    startEndDate[0], startEndDate[1]);

            for(Symbol symbol : searchResult){
                List<DailyPrice> dailyPriceList =
                        childSearchResult.stream()
                                .filter(x -> x.getSymbol().getId() == symbol.getId())
                                .collect(Collectors.toList());
                symbol.setDailyPriceList(dailyPriceList);
            }

            initChild = true;
        }

        if(searchResult != null)
            return convertToStockList(searchResult, !initChild);
        else
            return Collections.emptyList();
    }

    @RequestMapping("/stock/{id}/stats")
    @CrossOrigin(origins={"http://localhost:4200", "https://trade.ymlai87416.com"})
    public StockStatistic getStockStatistic(@PathVariable String id,
                                            @RequestParam(value="startDate", required=false) String startDate,
                                            @RequestParam(value="endDate", required=false) String endDate)
    {
        List<Symbol> searchResult = symbolRepository.findByInstrumentAndTicker(HK_STOCK, id);


        if(searchResult != null && searchResult.size() > 0 ){
            Symbol resultSymbol = searchResult.get(0);

            List<DailyPrice> childSearchResult = null;

            Date[] startEndDate = Utilities.parseStartDateAndEndDate(startDate, endDate);

            if(startEndDate != null && startEndDate.length == 2
                    && startEndDate[0] != null && startEndDate[1] != null){

                childSearchResult = dailyPriceRepository
                        .findBySymbolInAndPriceDateBetween(Collections.singletonList(resultSymbol),
                        startEndDate[0], startEndDate[1]);

                long stockId = resultSymbol.getId();
                List<Date> dateList = childSearchResult.stream()
                        .map(x -> x.getPriceDate()).collect(Collectors.toList());
                Optional<Date> statStartDate = dateList.stream().min(Date::compareTo);
                Optional<Date> statEndDate = dateList.stream().max(Date::compareTo);
                List<Double> priceList = childSearchResult.stream()
                        .map(x -> x.getAdjClosePrice()).collect(Collectors.toList());
                OptionalDouble statMinPrice = priceList.stream().mapToDouble(w -> w).min();
                OptionalDouble statMaxPrice = priceList.stream().mapToDouble(w -> w).max();
                OptionalDouble statAvgPrice = priceList.stream().mapToDouble(w -> w).average();
                StandardDeviation std = new StandardDeviation();
                double[] priceValues = new double[priceList.size()];
                for(int i=0; i<priceList.size(); ++i) priceValues[i] = priceList.get(i);

                double statStdPrice = std.evaluate(priceValues);

                if(statStartDate.isPresent() && statEndDate.isPresent()
                        && statMaxPrice.isPresent() && statMinPrice.isPresent()
                        && statAvgPrice.isPresent())
                    return new StockStatistic(stockId, statStartDate.get(), statEndDate.get(),
                            (float)statMinPrice.orElse(-1), (float)statMaxPrice.orElse(-1),
                            (float)statAvgPrice.orElse(-1), (float)statStdPrice);
                else
                    return null;
            }
            else
                return null;
        }
        else
            return null;
    }

    private List<Stock> convertToStockList(List<Symbol> symbolList, boolean skipChild){
        return symbolList.stream().map(x -> convertToStock(x, skipChild))
                .collect(Collectors.toList());
    }

    private Stock convertToStock(Symbol symbol, boolean skipChild){
        Stock result =  new Stock(symbol.getId(), symbol.getTicker(), symbol.getName());

        if(!skipChild) {
            List<StockHistory> children = convertToStockHistoryList(symbol.getDailyPriceList());
            result.setHistoryList(children);
        }
        return result;
    }

    private List<StockHistory> convertToStockHistoryList(List<DailyPrice> dailyPriceList){
        return dailyPriceList.stream().map(x -> convertToStockHistory(x)).collect(Collectors.toList());
    }

    private StockHistory convertToStockHistory(DailyPrice dailyPrice){
        return new StockHistory(dailyPrice.getId(), dailyPrice.getSymbol().getId(), dailyPrice.getPriceDate(),
                dailyPrice.getOpenPrice(), dailyPrice.getHighPrice(), dailyPrice.getLowPrice(),
                dailyPrice.getClosePrice(), dailyPrice.getAdjClosePrice(), dailyPrice.getVolume());
    }
}
