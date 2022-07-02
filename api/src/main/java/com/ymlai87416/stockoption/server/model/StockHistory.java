package com.ymlai87416.stockoption.server.model;

import java.util.Date;

public class StockHistory {
    private Long id;
    private Long stockId;
    private Date priceDate;
    private Double openPrice;
    private Double dailyHigh;
    private Double dailyLow;
    private Double closePrice;
    private Double adjClosePrice;
    private Long volume;

    public StockHistory(Long id, Long stockId, Date priceDate, Double openPrice, Double dailyHigh,
                        Double dailyLow, Double closePrice, Double adjClosePrice, Long volume){
        this.id = id;
        this.stockId = stockId;
        this.priceDate = priceDate;
        this.openPrice = openPrice;
        this.dailyHigh = dailyHigh;
        this.dailyLow = dailyLow;
        this.closePrice = closePrice;
        this.adjClosePrice = adjClosePrice;
        this.volume = volume;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getStockId() {
        return stockId;
    }

    public void setStockId(Long stockId) {
        this.stockId = stockId;
    }

    public Date getPriceDate() {
        return priceDate;
    }

    public void setPriceDate(Date priceDate) {
        this.priceDate = priceDate;
    }

    public Double getOpenPrice() {
        return openPrice;
    }

    public void setOpenPrice(Double openPrice) {
        this.openPrice = openPrice;
    }

    public Double getDailyHigh() {
        return dailyHigh;
    }

    public void setDailyHigh(Double dailyHigh) {
        this.dailyHigh = dailyHigh;
    }

    public Double getDailyLow() {
        return dailyLow;
    }

    public void setDailyLow(Double dailyLow) {
        this.dailyLow = dailyLow;
    }

    public Double getClosePrice() {
        return closePrice;
    }

    public void setClosePrice(Double closePrice) {
        this.closePrice = closePrice;
    }

    public Double getAdjClosePrice() {
        return adjClosePrice;
    }

    public void setAdjClosePrice(Double adjClosePrice) {
        this.adjClosePrice = adjClosePrice;
    }

    public Long getVolume() {
        return volume;
    }

    public void setVolume(Long volume) {
        this.volume = volume;
    }
}
