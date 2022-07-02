package com.ymlai87416.stockoption.server.service;

import com.ymlai87416.stockoption.server.domain.DataVendor;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DataVendorRepository extends JpaRepository<DataVendor, Long> {
}
