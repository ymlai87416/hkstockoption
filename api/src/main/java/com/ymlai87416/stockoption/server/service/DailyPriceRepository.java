package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.DailyPrice;
import com.ymlai87416.stockoption.server.domain.Symbol;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.*;

public interface DailyPriceRepository  extends JpaRepository<DailyPrice, Long> {
    List<DailyPrice> findBySymbolInAndPriceDateBetween(Collection<Symbol> symbolList, Date startDate, Date endDate);
    List<DailyPrice> findBySymbolInstrumentEqualsAndSymbolTickerLikeAndPriceDateBetween(String instrument, String ticker, Date startDate, Date endDate);
}
