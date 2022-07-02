--- configuration management ---

insert into job (name, description, created_date, last_updated_date)
values
('STOCK_003_HK', 'populate hk stock option price daily', now(), now());

SELECT id into @var1 from job where name = 'STOCK_003_HK';

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'hk_stock_option_tmp', 'T', 'temp table', now(), now());

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'hk_option_list', 'T', 'hk option list', now(), now());


CREATE TABLE hk_option_list (
	hkats_code varchar(10) not null,
    ticker varchar(10) not null,
    name varchar(255) NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=UTF8MB4;

