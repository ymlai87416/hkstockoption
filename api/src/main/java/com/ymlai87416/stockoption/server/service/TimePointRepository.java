package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.TimePoint;
import com.ymlai87416.stockoption.server.domain.TimeSeries;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Date;
import java.util.List;

public interface TimePointRepository extends JpaRepository<TimePoint, Long> {
    List<TimePoint> findTimePointByTimeSeriesInAndTimePointDateBetween(List<TimeSeries> series, Date startDate, Date endDate);
}
