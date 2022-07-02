package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.Symbol;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Date;
import java.util.List;

public interface SymbolRepository extends JpaRepository<Symbol, Long> {
    List<Symbol> findByInstrumentEqualsAndTickerLikeAndDailyPriceListPriceDateBetween(
            String instrument, String ticker,
            Date startDate, Date endDate);
    List<Symbol> findByInstrumentEqualsAndTickerAndDailyPriceListPriceDateBetween(
            String instrument, String ticker,
            Date startDate, Date endDate);
    List<Symbol> findByInstrumentAndTickerLike(String instrument, String ticker);
    List<Symbol> findByInstrumentAndTicker(String instrument, String ticker);

    List<Symbol> findByInstrument(String instrument);
}
