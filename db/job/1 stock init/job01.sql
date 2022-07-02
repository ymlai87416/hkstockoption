--- configuration management ---

insert into job (name, description, created_date, last_updated_date)
values
('STOCK_001', 'initialize new stock price series', now(), now());

SELECT @var1=id from job where name = 'STOCK_001';

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'STOCK_001_input', 'I', 'add new stock series here', now(), now());

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'symbol_tmp', 'T', 'add new stock series here', now(), now());

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'daily_price_tmp', 'T', 'add new stock series here', now(), now());



--- job tables --- 

CREATE TABLE STOCK_001_input (
	exchange varchar(32) NOT NULL,
	ticker varchar(32) NOT NULL,
	instrument varchar(64) NOT NULL,
	reason varchar(255) NULL,
    start_date datetime NOT NULL,
	created_date datetime NOT NULL,
    processed_time datetime NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;
