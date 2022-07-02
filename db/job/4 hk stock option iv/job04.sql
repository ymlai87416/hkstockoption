--- configuration management ---

insert into job (name, description, created_date, last_updated_date)
values
('STOCK_004_HK', 'populate hk stock option iv daily', now(), now());


SELECT id into @var1 from job where name = 'STOCK_004_HK';

insert into job_table(job_id, table_name, `type`, description, created_date, last_updated_date) 
values
(@var1, 'iv_timepoint_tmp', 'T', 'temp table', now(), now());
