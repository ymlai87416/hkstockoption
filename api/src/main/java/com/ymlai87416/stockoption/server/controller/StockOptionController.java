package com.ymlai87416.stockoption.server.controller;

import com.ymlai87416.stockoption.server.domain.HKOption;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.ymlai87416.stockoption.server.domain.DailyPrice;
import com.ymlai87416.stockoption.server.domain.StockOptionUnderlyingAsset;
import com.ymlai87416.stockoption.server.domain.Symbol;
import com.ymlai87416.stockoption.server.model.StockOption;
import com.ymlai87416.stockoption.server.model.StockOptionHistory;
import com.ymlai87416.stockoption.server.service.*;
import com.ymlai87416.stockoption.server.utilities.Utilities;
import org.hibernate.dialect.Sybase11Dialect;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Example;
import org.springframework.data.domain.ExampleMatcher;
import org.springframework.web.bind.annotation.*;

//import javax.rmi.CORBA.Util;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("hkstockoption/api")
public class StockOptionController {

    /**
     * findBySEHKCode                       : /stockOption/sehk/{id}
     * findBySEHKCodeWithHistory            : /stockOption/sehk/{id}?history=1
     * findByOptionCodeWithHistory          : /stockOption/code/{id}?history=1
     * findAvailableDateBySEHKCode          : /stockOption/sehk/{id}/listDate
     * findLatestAvailableDateBySEHKCode    : /stockOption/sehk/{id}/listDate?latest=1
     * (obsoleted) getAllStockOption        : /stockOption
     * getAllStockOptionUnderlyingAsset     : /stockOption/underlyingAsset
     */

    private SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
    private SymbolRepository symbolRepository;
    private DailyPriceRepository dailyPriceRepository;
    private HKOptionRespository hkOptionRespository;
    List<HKOption> hkOptionList;
    private Logger logger = LoggerFactory.getLogger(this.getClass());

    final String HK_STOCK_OPTION = "HK STOCK OPTION";

    @Autowired
    private StockOptionController(SymbolRepository symbolRepository,
                                  DailyPriceRepository dailyPriceRepository,
                                  HKOptionRespository hkOptionRespository
    ){
        this.symbolRepository = symbolRepository;
        this.dailyPriceRepository = dailyPriceRepository;
        //this.stockOptionUnderlyingAssetRepository = stockOptionUnderlyingAssetRepository;
        //underlyingAssetsList = this.stockOptionUnderlyingAssetRepository.findAll();
        this.hkOptionRespository = hkOptionRespository;
        hkOptionList = hkOptionRespository.findAll();
    }

    private boolean tickerMatch(String tickerStr, int tickerNum){
        try{
            int parseInt = Integer.parseInt(tickerStr.replace(".HK", ""));
            return parseInt == tickerNum;
        }
        catch(Exception ex){
            return false;
        }
    }

    @RequestMapping("/stockOption/sehk/{id}")
    @CrossOrigin(origins={"http://localhost:4200", "https://trade.ymlai87416.com"})
    public List<StockOption> findStockOptionBySEHKCode(@PathVariable String id,
                                                       @RequestParam(value="startDate", required=false) String startDate,
                                                       @RequestParam(value="endDate", required=false) String endDate) throws Exception {
        try {
            //int tickerNum = Integer.parseInt(id);
            Optional<HKOption> asset = hkOptionList.stream().filter(x -> x.getTicker()
                    .compareToIgnoreCase(id) == 0 ).findFirst();

            if (asset.isPresent()) {

                List<Symbol> searchResult = null;
                List<DailyPrice> childSearchResult = null;
                String tickerPattern = asset.get().getHKATSCode() + "%";

                Date[] startEndDate = Utilities.parseStartDateAndEndDate(startDate, endDate);

                boolean initChild = false;
                if(startEndDate != null && startEndDate.length == 2
                        && startEndDate[0] != null && startEndDate[1] != null){
                    logger.debug("Before query 1");

                    
                    searchResult = symbolRepository.findByInstrumentEqualsAndTickerLikeAndDailyPriceListPriceDateBetween
                            (HK_STOCK_OPTION, tickerPattern, startEndDate[0], startEndDate[1]);

                    logger.debug("After query 1");

                    childSearchResult = dailyPriceRepository.findBySymbolInstrumentEqualsAndSymbolTickerLikeAndPriceDateBetween
                            (HK_STOCK_OPTION, tickerPattern,
                                startEndDate[0], startEndDate[1]);

                    logger.debug("After query 2");

                    for(Symbol symbol : searchResult){
                        List<DailyPrice> dailyPriceList =
                                childSearchResult.stream().filter(x -> x.getSymbol().getId() == symbol.getId())
                                        .collect(Collectors.toList());
                        symbol.setDailyPriceList(dailyPriceList);
                    }

                    logger.debug("After consolidate");

                    initChild = true;
                }
                else{
                    searchResult = symbolRepository
                            .findByInstrumentAndTickerLike(HK_STOCK_OPTION, tickerPattern);
                }

                if (searchResult != null)
                    return convertToStockOptionList(searchResult, !initChild);
                else
                    return Collections.emptyList();
            } else
                return Collections.emptyList();
        } catch (Exception ex) {
            logger.error("Exception occurred", ex);
            throw new Exception("Invalid SEHK code.");
        }
    }

    @RequestMapping("/stockOption/hkats/{id}")
    @CrossOrigin(origins={"http://localhost:4200", "https://trade.ymlai87416.com"})
    public List<StockOption> findStockOptionByHKATSCode(@PathVariable String id,
                                                       @RequestParam(value="startDate", required=false) String startDate,
                                                       @RequestParam(value="endDate", required=false) String endDate) throws Exception {
        try {
            //int tickerNum = Integer.parseInt(id);
            Optional<HKOption> asset = hkOptionList.stream().filter(x -> x.getHKATSCode()
                    .compareToIgnoreCase(id) == 0 ).findFirst();

            if (asset.isPresent()) {

                List<Symbol> searchResult = null;
                List<DailyPrice> childSearchResult = null;
                String tickerPattern = asset.get().getHKATSCode() + "%";

                Date[] startEndDate = Utilities.parseStartDateAndEndDate(startDate, endDate);

                boolean initChild = false;
                if(startEndDate != null && startEndDate.length == 2
                        && startEndDate[0] != null && startEndDate[1] != null){
                    logger.debug("Before query 1");


                    searchResult = symbolRepository.findByInstrumentEqualsAndTickerLikeAndDailyPriceListPriceDateBetween
                            (HK_STOCK_OPTION, tickerPattern, startEndDate[0], startEndDate[1]);

                    logger.debug("After query 1");

                    childSearchResult = dailyPriceRepository.findBySymbolInstrumentEqualsAndSymbolTickerLikeAndPriceDateBetween
                            (HK_STOCK_OPTION, tickerPattern,
                                    startEndDate[0], startEndDate[1]);

                    logger.debug("After query 2");

                    for(Symbol symbol : searchResult){
                        List<DailyPrice> dailyPriceList =
                                childSearchResult.stream().filter(x -> x.getSymbol().getId() == symbol.getId())
                                        .collect(Collectors.toList());
                        symbol.setDailyPriceList(dailyPriceList);
                    }

                    logger.debug("After consolidate");

                    initChild = true;
                }
                else{
                    searchResult = symbolRepository
                            .findByInstrumentAndTickerLike(HK_STOCK_OPTION, tickerPattern);
                }

                if (searchResult != null)
                    return convertToStockOptionList(searchResult, !initChild);
                else
                    return Collections.emptyList();
            } else
                return Collections.emptyList();
        } catch (Exception ex) {
            logger.error("Exception occurred", ex);
            throw new Exception("Invalid HKATS code.");
        }
    }

    @RequestMapping("/stockOption/code/{id}")
    @CrossOrigin(origins={"http://localhost:4200", "https://trade.ymlai87416.com"})
    public List<StockOption> findStockOptionByOptionCode(@PathVariable String id,
                                                         @RequestParam(value="startDate", required=false) String startDate,
                                                         @RequestParam(value="endDate", required=false) String endDate)
    {

        List<Symbol> searchResult;
        List<DailyPrice> childSearchResult = null;

        Date[] startEndDate = Utilities.parseStartDateAndEndDate(startDate, endDate);

        boolean initChild = false;
        if(startEndDate != null && startEndDate.length == 2
                && startEndDate[0] != null && startEndDate[1] != null){
            searchResult = symbolRepository.findByInstrumentEqualsAndTickerAndDailyPriceListPriceDateBetween
                    (HK_STOCK_OPTION, id, startEndDate[0], startEndDate[1]);
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
        else{
            searchResult = symbolRepository.findByInstrumentAndTicker(HK_STOCK_OPTION, id);
        }

        if(searchResult != null)
            return convertToStockOptionList(searchResult, !initChild);
        else
            return Collections.emptyList();
    }

    @RequestMapping("/stockOption/underlyingAsset")
    @CrossOrigin(origins={"http://localhost:4200", "https://trade.ymlai87416.com"})
    public List<HKOption> getAllStockOptionUnderlyingAsset()
    {
        return hkOptionList;
    }

    private List<StockOption> convertToStockOptionList(List<Symbol> symbolList, boolean skipChild){
        return symbolList.stream().map(x -> convertToStockOption(x, skipChild)).collect(Collectors.toList());
    }

    private StockOption convertToStockOption(Symbol symbol, boolean skipChild){
        StockOption result =  new StockOption(symbol.getId(), symbol.getTicker(), symbol.getName());
        if(!skipChild) {
            List<StockOptionHistory> children = convertToStockOptionHistoryList(symbol.getDailyPriceList());
            result.setHistoryList(children);
        }
        return result;
    }

    private List<StockOptionHistory> convertToStockOptionHistoryList(List<DailyPrice> dailyPriceList){
        return dailyPriceList.stream().map(x -> convertToStockOptionHistory(x)).collect(Collectors.toList());
    }

    private StockOptionHistory convertToStockOptionHistory(DailyPrice dailyPrice){
        return new StockOptionHistory(dailyPrice.getId(), dailyPrice.getSymbol().getId(),
                dailyPrice.getPriceDate(), dailyPrice.getOpenPrice(), dailyPrice.getHighPrice(), dailyPrice.getLowPrice(),
                dailyPrice.getClosePrice(), dailyPrice.getOpenInterest(), dailyPrice.getIv());
    }

}
