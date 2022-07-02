--- configuration management ---

insert into job (name, description, created_date, last_updated_date)
values
('STOCK_002', 'populate stock price daily', now(), now());

SELECT id into @var1 from job where name = 'STOCK_002';

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'hkstock_tmp', 'T', 'add new stock series here', now(), now());
