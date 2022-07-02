package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;

@Entity
@Table(name = "stock_option_underlying_asset")
public class HKOption {
    private String hkatsCode;
    private String ticker;
    private String name;
    @Id
    @Column(name = "hkats_code")
    public String getHKATSCode() {
        return hkatsCode;
    }

    public void setHKATSCode(String ticker) {
        this.hkatsCode = ticker;
    }

    @Column(name = "ticker")
    public String getTicker() {
        return ticker;
    }

    public void setTicker(String shortForm) {
        this.ticker = shortForm;
    }

    @Column(name = "name")
    public String getName() {
        return name;
    }

    public void setName(String fullName) {
        this.name = fullName;
    }

}
