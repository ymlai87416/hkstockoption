package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.Exchange;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ExchangeRepository extends JpaRepository<Exchange, Long> {
}
