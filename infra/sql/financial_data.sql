DROP SCHEMA financial_oltp CASCADE;


CREATE SCHEMA IF NOT EXISTS financial_oltp;
SET search_path TO financial_oltp;

CREATE TABLE company (
    company_id VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    exchange VARCHAR(50),
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE company IS 'Bảng lưu thông tin cơ bản về công ty niêm yết';
COMMENT ON COLUMN company.company_id IS 'Mã định danh công ty (Ticker hoặc ID từ API)';
COMMENT ON COLUMN company.exchange IS 'Sàn giao dịch chứng khoán (NASDAQ, NYSE, HOSE,...)';
COMMENT ON COLUMN company.currency IS 'Đơn vị tiền tệ mặc định (USD, VND,...)';

CREATE TABLE statement_type (
    statement_type_id SERIAL PRIMARY KEY,
    statement_code VARCHAR(10) UNIQUE NOT NULL,
    statement_name VARCHAR(100) NOT NULL
);

INSERT INTO statement_type (statement_code, statement_name)
VALUES 
    ('IS', 'Income Statement'),
    ('BS', 'Balance Sheet'),
    ('CF', 'Cash Flow Statement')
ON CONFLICT DO NOTHING;

COMMENT ON TABLE statement_type IS 'Danh mục loại báo cáo tài chính (IS, BS, CF)';

CREATE TABLE financial_statement (
    statement_id BIGSERIAL PRIMARY KEY,
    company_id VARCHAR(20) NOT NULL REFERENCES company(company_id) ON DELETE CASCADE,
    statement_type_id INT NOT NULL REFERENCES statement_type(statement_type_id),
    fiscal_year INT NOT NULL,
    fiscal_quarter VARCHAR(5) NOT NULL CHECK (fiscal_quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    fiscal_period VARCHAR(10) GENERATED ALWAYS AS (fiscal_year || '-' || fiscal_quarter) STORED,
    report_date DATE,
    source VARCHAR(100) DEFAULT 'API_USGAAP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_financial_statement UNIQUE (company_id, statement_type_id, fiscal_year, fiscal_quarter)
);

COMMENT ON TABLE financial_statement IS 'Báo cáo tài chính của công ty theo năm và quý';
COMMENT ON COLUMN financial_statement.fiscal_period IS 'Chuỗi kỳ tài chính (VD: 2024-Q2)';

-- Index tối ưu truy vấn theo công ty, loại báo cáo, kỳ
CREATE INDEX idx_statement_lookup 
ON financial_statement (company_id, statement_type_id, fiscal_year, fiscal_quarter);


CREATE TABLE line_item_dictionary (
    item_code VARCHAR(50) PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    default_unit VARCHAR(20) DEFAULT 'USD',
    display_group VARCHAR(100),
    description TEXT
);

COMMENT ON TABLE line_item_dictionary IS 'Từ điển các chỉ tiêu tài chính (Revenue, Net Income,...)';
COMMENT ON COLUMN line_item_dictionary.item_code IS 'Mã chỉ tiêu duy nhất, chuẩn hóa cho API hoặc hệ thống BI';
COMMENT ON COLUMN line_item_dictionary.display_group IS 'Nhóm hiển thị chỉ tiêu (Revenue, Expense, Assets, Liabilities,...)';

-- =========================================
-- 6️⃣ BẢNG FINANCIAL_LINE_ITEM
-- =========================================
CREATE TABLE financial_line_item (
    line_item_id BIGSERIAL PRIMARY KEY,
    statement_id BIGINT NOT NULL REFERENCES financial_statement(statement_id) ON DELETE CASCADE,
    item_code VARCHAR(50) REFERENCES line_item_dictionary(item_code),
    item_name VARCHAR(255) NOT NULL,
    item_value NUMERIC(20,2) DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'USD',
    display_order INT
);

COMMENT ON TABLE financial_line_item IS 'Chi tiết các chỉ tiêu trong báo cáo tài chính';
COMMENT ON COLUMN financial_line_item.item_name IS 'Tên chỉ tiêu hiển thị (Revenue, Total Assets, Net Income,...)';
COMMENT ON COLUMN financial_line_item.item_value IS 'Giá trị chỉ tiêu (theo đơn vị tiền tệ tương ứng)';

-- Index hỗ trợ tìm kiếm nhanh theo báo cáo
CREATE INDEX idx_lineitem_statement_order ON financial_line_item (statement_id, display_order);
CREATE INDEX idx_lineitem_code ON financial_line_item (item_code);


SET search_path TO financial_oltp;

-- =========================================
-- VIEW: Income Statement – 10 kỳ gần nhất
-- =========================================
CREATE OR REPLACE VIEW vw_income_statement_recent AS
SELECT
    fs.statement_id,
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    fs.fiscal_quarter,
    (fs.fiscal_year || '-' || fs.fiscal_quarter) AS fiscal_period,
    li.item_name,
    li.item_value,
    li.unit,
    li.display_order,
    fs.report_date
FROM financial_statement fs
JOIN company c ON fs.company_id = c.company_id
JOIN statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'IS'
  AND (fs.fiscal_year, fs.fiscal_quarter) IN (
      SELECT fiscal_year, fiscal_quarter
      FROM financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
      ORDER BY fs2.fiscal_year DESC, fs2.fiscal_quarter DESC
      LIMIT 10
  )
ORDER BY c.company_id, fs.fiscal_year DESC, fs.fiscal_quarter DESC, li.display_order;

COMMENT ON VIEW vw_income_statement_recent IS 'Báo cáo kết quả kinh doanh 10 kỳ gần nhất của mỗi công ty.';

-- =========================================
-- VIEW: Balance Sheet – 10 kỳ gần nhất
-- =========================================
CREATE OR REPLACE VIEW vw_balance_sheet_recent AS
SELECT
    fs.statement_id,
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    fs.fiscal_quarter,
    (fs.fiscal_year || '-' || fs.fiscal_quarter) AS fiscal_period,
    li.item_name,
    li.item_value,
    li.unit,
    li.display_order,
    fs.report_date
FROM financial_statement fs
JOIN company c ON fs.company_id = c.company_id
JOIN statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'BS'
  AND (fs.fiscal_year, fs.fiscal_quarter) IN (
      SELECT fiscal_year, fiscal_quarter
      FROM financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
      ORDER BY fs2.fiscal_year DESC, fs2.fiscal_quarter DESC
      LIMIT 10
  )
ORDER BY c.company_id, fs.fiscal_year DESC, fs.fiscal_quarter DESC, li.display_order;

COMMENT ON VIEW vw_balance_sheet_recent IS 'Bảng cân đối kế toán 10 kỳ gần nhất của mỗi công ty.';


-- =========================================
-- VIEW: Cash Flow Statement – 10 kỳ gần nhất
-- =========================================
CREATE OR REPLACE VIEW vw_cashflow_statement_recent AS
SELECT
    fs.statement_id,
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    fs.fiscal_quarter,
    (fs.fiscal_year || '-' || fs.fiscal_quarter) AS fiscal_period,
    li.item_name,
    li.item_value,
    li.unit,
    li.display_order,
    fs.report_date
FROM financial_statement fs
JOIN company c ON fs.company_id = c.company_id
JOIN statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'CF'
  AND (fs.fiscal_year, fs.fiscal_quarter) IN (
      SELECT fiscal_year, fiscal_quarter
      FROM financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
      ORDER BY fs2.fiscal_year DESC, fs2.fiscal_quarter DESC
      LIMIT 10
  )
ORDER BY c.company_id, fs.fiscal_year DESC, fs.fiscal_quarter DESC, li.display_order;

COMMENT ON VIEW vw_cashflow_statement_recent IS 'Báo cáo lưu chuyển tiền tệ 10 kỳ gần nhất của mỗi công ty.';


SELECT * 
FROM financial_oltp.vw_income_statement_recent
WHERE company_id = 'IBM';

CREATE OR REPLACE VIEW financial_oltp. vw_income_statement_annual AS
SELECT
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    li.item_name,
    SUM(li.item_value) AS total_value,
    li.unit,
    li.display_order,
    MAX(fs.report_date) AS latest_report_date
FROM financial_oltp.financial_statement fs
JOIN financial_oltp.company c ON fs.company_id = c.company_id
JOIN financial_oltp.statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_oltp.financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'IS'
GROUP BY 
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    li.item_name,
    li.unit,
    li.display_order
ORDER BY 
    c.company_id,
    fs.fiscal_year DESC,
    li.display_order;

COMMENT ON VIEW financial_oltp.vw_income_statement_annual IS 
'Báo cáo kết quả kinh doanh tổng hợp theo từng năm (gộp 4 quý).';

CREATE OR REPLACE VIEW financial_oltp.vw_balance_sheet_annual AS
SELECT
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    li.item_name,
    li.item_value,
    li.unit,
    li.display_order,
    fs.report_date
FROM financial_oltp.financial_statement fs
JOIN financial_oltp.company c ON fs.company_id = c.company_id
JOIN financial_oltp.statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_oltp.financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'BS'
  AND fs.report_date = (
      SELECT MAX(fs2.report_date)
      FROM financial_oltp.financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
        AND fs2.fiscal_year = fs.fiscal_year
  )
ORDER BY 
    c.company_id,
    fs.fiscal_year DESC,
    li.display_order;

COMMENT ON VIEW financial_oltp.vw_balance_sheet_annual IS 
'Bảng cân đối kế toán cuối năm của mỗi công ty.';

CREATE OR REPLACE VIEW financial_oltp.vw_cashflow_statement_annual AS
SELECT
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    li.item_name,
    SUM(li.item_value) AS total_value,
    li.unit,
    li.display_order,
    MAX(fs.report_date) AS latest_report_date
FROM financial_oltp.financial_statement fs
JOIN financial_oltp.company c ON fs.company_id = c.company_id
JOIN financial_oltp.statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_oltp.financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'CF'
GROUP BY 
    c.company_id,
    c.company_name,
    fs.fiscal_year,
    li.item_name,
    li.unit,
    li.display_order
ORDER BY 
    c.company_id,
    fs.fiscal_year DESC,
    li.display_order;

COMMENT ON VIEW financial_oltp.vw_cashflow_statement_annual IS 
'Báo cáo lưu chuyển tiền tệ tổng hợp theo từng năm (gộp 4 quý).';

SELECT * 
FROM financial_oltp. vw_income_statement_annual
WHERE company_id = 'IBM' and item_name = 'Total Revenue';

SELECT * 
FROM financial_oltp. vw_balance_sheet_annual
WHERE company_id = 'IBM' and item_name = 'Total Assets';

SELECT * 
FROM financial_oltp.vw_cashflow_statement_annual
WHERE company_id = 'IBM' and item_name = 'Capital Expenditures';



