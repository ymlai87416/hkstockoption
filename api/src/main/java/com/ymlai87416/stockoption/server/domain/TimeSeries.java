package com.ymlai87416.stockoption.server.domain;
import javax.persistence.*;
import java.sql.Date;
import java.util.List;

/**
 * Created by Tom on 12/10/2016.
 */
@Entity
@Table(name = "time_series")
public class TimeSeries {
    private Long id;
    private long version;
    private String seriesName;
    private String category;
    private java.sql.Date createdDate;
    private java.sql.Date lastUpdatedDate;
    private List<TimePoint> timePointList;

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

    @Column(name = "series_name")
    public String getSeriesName() {
        return seriesName;
    }

    public void setSeriesName(String seriesName) {
        this.seriesName = seriesName;
    }

    @Column(name = "category")
    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
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

    @OneToMany(mappedBy="timeSeries", cascade=CascadeType.ALL)
    public List<TimePoint> getTimePointList(){
        return this.timePointList;
    }

    public void setTimePointList(List<TimePoint> timePointList){
        this.timePointList = timePointList;
    }

}
