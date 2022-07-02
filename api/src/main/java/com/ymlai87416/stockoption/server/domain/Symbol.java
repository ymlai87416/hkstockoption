package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;
import java.sql.Date;
import java.util.List;

/**
 * Created by Tom on 6/10/2016.
 */
@Entity
@Table(name = "symbol")
public class Symbol {
    private Long id;
    private long version;
    private Exchange exchange;
    private String ticker;
    private String instrument;
    private String name;
    private String sector;
    private Integer lot;
    private String currency;
    private Date createdDate;
    private Date lastUpdatedDate;
    private List<DailyPrice> dailyPriceList;

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
    @JoinColumn(name="exchange_id")
    public Exchange getExchange() {
        return exchange;
    }

    public void setExchange(Exchange exchange) {
        this.exchange = exchange;
    }

    @Column(name = "ticker")
    public String getTicker() {
        return ticker;
    }

    public void setTicker(String ticker) {
        this.ticker = ticker;
    }

    @Column(name = "instrument")
    public String getInstrument() {
        return instrument;
    }

    public void setInstrument(String instrument) {
        this.instrument = instrument;
    }

    @Column(name = "name")
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Column(name = "sector")
    public String getSector() {
        return sector;
    }

    public void setSector(String sector) {
        this.sector = sector;
    }

    @Column(name = "lot")
    public Integer getLot() {
        return lot;
    }

    public void setLot(Integer lot) {
        this.lot = lot;
    }

    @Column(name = "currency")
    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
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

    @OneToMany(mappedBy="symbol", cascade=CascadeType.ALL, fetch = FetchType.LAZY)
    public List<DailyPrice> getDailyPriceList() {
        return dailyPriceList;
    }

    public void setDailyPriceList(List<DailyPrice> dailyPriceList) {
        this.dailyPriceList = dailyPriceList;
    }
}
