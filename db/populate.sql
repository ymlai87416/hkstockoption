-- populate data vendor
insert into data_vendor
(version, name, website_url, created_date, last_updated_date)
values
(1, 'Yahoo', 'https://finance.yahoo.com', now(), now());

insert into data_vendor
(version, name, website_url, created_date, last_updated_date)
values
(1, 'HKEx', 'https://www.hkex.com.hk', now(), now());

-- populate exchange
-- hkex
insert into exchange
(version, abbrev, name, city, country, currency, created_date, last_updated_date)
values
(1, 'HKEX', 'Hong Kong Exchange', 'Hong Kong', 'Hong Kong', 'HKD', now(), now());

-- NYSE
insert into exchange
(version, abbrev, name, city, country, currency, created_date, last_updated_date)
values
(1, 'NYSE', 'New York Stock Exchange', 'New York', 'USA', 'USD', now(), now());

-- NASDAQ
insert into exchange
(version, abbrev, name, city, country, currency, created_date, last_updated_date)
values
(1, 'NASDAQ', 'National Association of Securities Dealers Automated Quotations', 'New York', 'USA', 'USD', now(), now());

