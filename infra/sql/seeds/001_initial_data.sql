-- Seed data for Financial Company
INSERT INTO financial_oltp.company (company_id, company_name, sector, exchange)
VALUES 
('AAPL', 'Apple Inc.', 'Technology', 'NASDAQ'),
('MSFT', 'Microsoft Corp.', 'Technology', 'NASDAQ'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'NASDAQ'),
('NVDA', 'NVIDIA Corp.', 'Technology', 'NASDAQ'),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'NASDAQ')
ON CONFLICT (company_id) DO NOTHING;

-- Seed data for Stocks
INSERT INTO market_data_oltp.stocks (company_id, stock_ticker, stock_name, exchange, delisted)
VALUES 
('AAPL', 'AAPL', 'Apple Inc.', 'NASDAQ', false),
('MSFT', 'MSFT', 'Microsoft Corp.', 'NASDAQ', false),
('GOOGL', 'GOOGL', 'Alphabet Inc.', 'NASDAQ', false),
('NVDA', 'NVDA', 'NVIDIA Corp.', 'NASDAQ', false),
('TSLA', 'TSLA', 'Tesla Inc.', 'NASDAQ', false)
ON CONFLICT (stock_ticker) DO NOTHING;
