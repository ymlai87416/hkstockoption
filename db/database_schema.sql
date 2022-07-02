CREATE DATABASE securities_master;
-- UTF8MB4?

USE securities_master;

CREATE TABLE exchange (
	id bigint NOT NULL AUTO_INCREMENT,
	version bigint NOT NULL,
	abbrev varchar(32) NOT NULL,
	name varchar(255) NOT NULL,
	city varchar(255) NULL,
	country varchar(255) NULL,
	currency varchar(64) NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

CREATE TABLE data_vendor (
	id bigint NOT NULL AUTO_INCREMENT,
	version bigint NOT NULL,
	name varchar(64) NOT NULL,
	website_url varchar(255) NULL,
	support_email varchar(255) NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;


CREATE TABLE symbol (
	id bigint NOT NULL AUTO_INCREMENT,
	version bigint NOT NULL,
	exchange_id bigint NULL,
	ticker varchar(32) NOT NULL,
	instrument varchar(64) NOT NULL,
	underlying_asset_ticker varchar(32) NOT NULL,
	name varchar(255) NULL,
	sector varchar(255) NULL,
	lot	int NULL,
	currency varchar(32) NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (exchange_id) REFERENCES exchange(id),
	CONSTRAINT exchange_ticker UNIQUE(exchange_id, ticker)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

CREATE TABLE daily_price (
	id bigint NOT NULL AUTO_INCREMENT,
	version bigint NOT NULL,
	data_vendor_id bigint NOT NULL,
	symbol_id bigint NOT NULL,
	price_date datetime NOT NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	open_price decimal(19,4) NULL,
	high_price decimal(19,4) NULL,
	low_price decimal(19,4) NULL,
	close_price decimal(19,4) NULL,
	adj_close_price decimal(19,4) NULL,
	volume bigint NULL,
	iv decimal(19,4) NULL,
	open_interest bigint NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (data_vendor_id) REFERENCES data_vendor(id),
	FOREIGN KEY (symbol_id) REFERENCES symbol(id),
	CONSTRAINT symbol_date UNIQUE (symbol_id,price_date)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;




CREATE TABLE time_series(
	id bigint NOT NULL AUTO_INCREMENT,
	version bigint NOT NULL,
	series_name varchar(255) NOT NULL,
	category varchar(255) NOT NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

CREATE INDEX idx_time_series_name ON time_series (series_name);

CREATE TABLE time_point(
	id bigint NOT NULL AUTO_INCREMENT,
	version bigint NOT NULL,
	series_id bigint NOT NULL,
	time_point_date datetime NOT NULL,
	`value` decimal(19,4) NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT series_timepoint UNIQUE(series_id, time_point_date),
	FOREIGN KEY (series_id) REFERENCES time_series(id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

CREATE TABLE key_value_collection(
	id bigint NOT NULL AUTO_INCREMENT,
	`key` varchar(255) NOT NULL,
	`value` varchar(255) NOT NULL,
	version bigint NOT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

CREATE INDEX index_key ON key_value_collection (`key`);

create table log_message(
	id bigint NOT NULL AUTO_INCREMENT,
	category varchar(100) NOT NULL,
	message varchar(255) NOT NULL,
	created_date datetime NOT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;


--- job tables --- 
create table job(
	id bigint NOT NULL AUTO_INCREMENT, 
	name varchar(64) NOT NULL,
	description varchar(255) NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

create table job_table(
	id bigint NOT NULL AUTO_INCREMENT,
	job_id bigint NOT NULL,
	table_name varchar(255) NOT NULL,
	type varchar(1) NOT NULL,
	description varchar(255) NULL,
	created_date datetime NOT NULL,
	last_updated_date datetime NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (job_id) REFERENCES job(id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

