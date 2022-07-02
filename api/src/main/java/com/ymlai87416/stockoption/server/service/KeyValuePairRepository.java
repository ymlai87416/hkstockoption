package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.KeyValuePair;
import org.springframework.data.jpa.repository.JpaRepository;

public interface KeyValuePairRepository  extends JpaRepository<KeyValuePair, Long> {
}
