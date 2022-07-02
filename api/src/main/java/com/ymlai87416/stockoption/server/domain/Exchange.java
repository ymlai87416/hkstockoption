package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;
import java.sql.Date;
import java.sql.Time;

/**
 * Created by Tom on 6/10/2016.
 */
@Entity
@Table(name = "exchange")
public class Exchange {
    private Long id;
    private long version;
    private String abbrev;
    private String name;
    private String city;
    private String country;
    private String currency;
    private Time timezoneOffset;
    private Date createdDate;
    private Date lastUpdatedDate;

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

    @Column(name = "abbrev")
    public String getAbbrev() {
        return abbrev;
    }

    public void setAbbrev(String abbrev) {
        this.abbrev = abbrev;
    }

    @Column(name = "name")
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Column(name = "city")
    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    @Column(name = "country")
    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    @Column(name = "currency")
    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    @Column(name = "timezone_offset")
    public Time getTimezoneOffset() {
        return timezoneOffset;
    }

    public void setTimezoneOffset(Time timezoneOffset) {
        this.timezoneOffset = timezoneOffset;
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
}
