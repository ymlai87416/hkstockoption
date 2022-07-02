package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.TimeSeries;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Date;
import java.util.List;

public interface TimeSeriesRepository extends JpaRepository<TimeSeries, Long> {
    List<TimeSeries> findBySeriesNameLike(String seriesName);
    List<TimeSeries> findBySeriesNameLikeAndTimePointListTimePointDateBetween(String seriesName, Date startDate, Date endDate);
}
