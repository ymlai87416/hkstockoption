package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;

public interface HKOptionRespository extends JpaRepository<HKOption, String> {
}
