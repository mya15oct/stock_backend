-- 1. Create View: Income Statement Recent
CREATE OR REPLACE VIEW financial_oltp.vw_income_statement_recent AS
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
FROM financial_oltp.financial_statement fs
JOIN financial_oltp.company c ON fs.company_id = c.company_id
JOIN financial_oltp.statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_oltp.financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'IS'
  AND (fs.fiscal_year, fs.fiscal_quarter) IN (
      SELECT fiscal_year, fiscal_quarter
      FROM financial_oltp.financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
      ORDER BY fs2.fiscal_year DESC, fs2.fiscal_quarter DESC
      LIMIT 10
  )
ORDER BY c.company_id, fs.fiscal_year DESC, fs.fiscal_quarter DESC, li.display_order;

-- 2. Create View: Balance Sheet Recent
CREATE OR REPLACE VIEW financial_oltp.vw_balance_sheet_recent AS
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
FROM financial_oltp.financial_statement fs
JOIN financial_oltp.company c ON fs.company_id = c.company_id
JOIN financial_oltp.statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_oltp.financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'BS'
  AND (fs.fiscal_year, fs.fiscal_quarter) IN (
      SELECT fiscal_year, fiscal_quarter
      FROM financial_oltp.financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
      ORDER BY fs2.fiscal_year DESC, fs2.fiscal_quarter DESC
      LIMIT 10
  )
ORDER BY c.company_id, fs.fiscal_year DESC, fs.fiscal_quarter DESC, li.display_order;

-- 3. Create View: Cash Flow Statement Recent
CREATE OR REPLACE VIEW financial_oltp.vw_cashflow_statement_recent AS
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
FROM financial_oltp.financial_statement fs
JOIN financial_oltp.company c ON fs.company_id = c.company_id
JOIN financial_oltp.statement_type st ON fs.statement_type_id = st.statement_type_id
JOIN financial_oltp.financial_line_item li ON fs.statement_id = li.statement_id
WHERE st.statement_code = 'CF'
  AND (fs.fiscal_year, fs.fiscal_quarter) IN (
      SELECT fiscal_year, fiscal_quarter
      FROM financial_oltp.financial_statement fs2
      WHERE fs2.company_id = fs.company_id
        AND fs2.statement_type_id = fs.statement_type_id
      ORDER BY fs2.fiscal_year DESC, fs2.fiscal_quarter DESC
      LIMIT 10
  )
ORDER BY c.company_id, fs.fiscal_year DESC, fs.fiscal_quarter DESC, li.display_order;
