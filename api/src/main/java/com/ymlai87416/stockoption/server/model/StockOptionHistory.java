package com.ymlai87416.stockoption.server.model;

import java.util.Date;

public class StockOptionHistory {

    private Long id;
    private Long stockOptionId;
    private Date priceDate;
    private Double openPrice;
    private Double dailyHigh;
    private Double dailyLow;
    private Double settlePrice;
    private Long openInterest;
    private Double iv;

    public StockOptionHistory(Long id, Long stockOptionId, Date priceDate, Double openPrice, Double dailyHigh, Double dailyLow, Double settlePrice, Long openInterest, Double iv){
		this.id = id;
		this.stockOptionId = stockOptionId;
		this.priceDate = priceDate;
		this.openPrice = openPrice;
		this.dailyHigh = dailyHigh;
		this.dailyLow = dailyLow;
		this.settlePrice = settlePrice;
		this.openInterest = openInterest;
		this.iv = iv;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getStockOptionId() {
        return stockOptionId;
    }

    public void setStockOptionId(Long stockOptionId) {
        this.stockOptionId = stockOptionId;
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

    public Double getSettlePrice() {
        return settlePrice;
    }

    public void setSettlePrice(Double settlePrice) {
        this.settlePrice = settlePrice;
    }

    public Long getOpenInterest() {
        return openInterest;
    }

    public void setOpenInterest(Long openInterest) {
        this.openInterest = openInterest;
    }

    public Double getIv() {
        return iv;
    }

    public void setIv(Double iv) {
        this.iv = iv;
    }

}
