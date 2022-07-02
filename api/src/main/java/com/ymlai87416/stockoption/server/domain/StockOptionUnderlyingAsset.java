package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;

@Entity
@Table(name = "stock_option_underlying_asset")
@Deprecated
public class StockOptionUnderlyingAsset {
    private Long id;
    private String ticker;
    private String shortForm;
    private String fullName;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    @Column(name = "ticker")
    public String getTicker() {
        return ticker;
    }

    public void setTicker(String ticker) {
        this.ticker = ticker;
    }

    @Column(name = "short_form")
    public String getShortForm() {
        return shortForm;
    }

    public void setShortForm(String shortForm) {
        this.shortForm = shortForm;
    }

    @Column(name = "full_name")
    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }
}
