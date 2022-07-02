package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;
import java.sql.Date;

/**
 * Created by Tom on 6/10/2016.
 */
@Entity
@Table(name = "daily_price")
public class DailyPrice {
    private Long id;
    private long version;
    private DataVendor dataVendor;
    private Symbol symbol;
    private Date priceDate;
    private Date createdDate;
    private Date lastUpdatedDate;
    private Double openPrice;
    private Double highPrice;
    private Double lowPrice;
    private Double closePrice;
    private Double adjClosePrice;
    private Long volume;
    private Double iv;
    private Long openInterest;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    @Version
    @Column(name = "version")
    public long getVersion() {
        return version;
    }

    public void setVersion(long version) {
        this.version = version;
    }

    @ManyToOne(fetch= FetchType.LAZY)
    @JoinColumn(name="data_vendor_id")
    public DataVendor getDataVendor() {
        return dataVendor;
    }

    public void setDataVendor(DataVendor dataVendor) {
        this.dataVendor = dataVendor;
    }

    @ManyToOne(fetch= FetchType.LAZY)
    @JoinColumn(name="symbol_id")
    public Symbol getSymbol() {
        return symbol;
    }

    public void setSymbol(Symbol symbol) {
        this.symbol = symbol;
    }

    @Column(name = "price_date")
    public Date getPriceDate() {
        return priceDate;
    }

    public void setPriceDate(Date priceDate) {
        this.priceDate = priceDate;
    }

    @Column(name = "created_date")
    public Date getCreatedDate() {
        return createdDate;
    }

    public void setCreatedDate(Date createdDate) {
        this.createdDate = createdDate;
    }

    @Column(name = "last_updated_date")
    public Date getLastUpdatedDate() {
        return lastUpdatedDate;
    }

    public void setLastUpdatedDate(Date lastUpdatedDate) {
        this.lastUpdatedDate = lastUpdatedDate;
    }

    @Column(name = "open_price")
    public Double getOpenPrice() {
        return openPrice;
    }

    public void setOpenPrice(Double openPrice) {
        this.openPrice = openPrice;
    }

    @Column(name = "high_price")
    public Double getHighPrice() {
        return highPrice;
    }

    public void setHighPrice(Double highPrice) {
        this.highPrice = highPrice;
    }

    @Column(name = "low_price")
    public Double getLowPrice() {
        return lowPrice;
    }

    public void setLowPrice(Double lowPrice) {
        this.lowPrice = lowPrice;
    }

    @Column(name = "close_price")
    public Double getClosePrice() {
        return closePrice;
    }

    public void setClosePrice(Double closePrice) {
        this.closePrice = closePrice;
    }

    @Column(name = "adj_close_price")
    public Double getAdjClosePrice() {
        return adjClosePrice;
    }

    public void setAdjClosePrice(Double adjClosePrice) {
        this.adjClosePrice = adjClosePrice;
    }

    @Column(name = "volume")
    public Long getVolume() {
        return volume;
    }

    public void setVolume(Long volume) {
        this.volume = volume;
    }

    @Column(name = "iv")
    public Double getIv() {
        return iv;
    }

    public void setIv(Double volume) {
        this.iv = volume;
    }

    @Column(name = "open_interest")
    public Long getOpenInterest() {
        return openInterest;
    }

    public void setOpenInterest(Long openInterest) {
        this.openInterest = openInterest;
    }
}
