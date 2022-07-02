package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;
import java.sql.Date;

/**
 * Created by Tom on 12/10/2016.
 */
@Entity
@Table(name = "time_point")
public class TimePoint {
    private Long id;
    private long version;
    private TimeSeries timeSeries;
    private java.sql.Date timePointDate;
    private Double value;
    private java.sql.Date createdDate;
    private java.sql.Date lastUpdatedDate;

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
    @JoinColumn(name="series_id")
    public TimeSeries getTimeSeries() {
        return timeSeries;
    }

    public void setTimeSeries(TimeSeries timeSeries) {
        this.timeSeries = timeSeries;
    }

    @Column(name = "time_point_date")
    public Date getTimePointDate() {
        return timePointDate;
    }

    public void setTimePointDate(Date timePointDate) {
        this.timePointDate = timePointDate;
    }

    @Column(name = "value")
    public Double getValue() {
        return value;
    }

    public void setValue(Double value) {
        this.value = value;
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

    public void setLastUpdatedDate(Date updatedDate) {
        this.lastUpdatedDate = updatedDate;
    }
}
