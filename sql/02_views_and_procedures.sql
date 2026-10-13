-- Total stock per product across all bins
CREATE OR REPLACE VIEW v_stock_levels AS
SELECT p.product_id, p.name, p.category,
       COALESCE(SUM(i.quantity), 0) AS total_stock
FROM products p
LEFT JOIN inventory i ON i.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category;

-- Delivered orders that arrived after the promised date
CREATE OR REPLACE VIEW v_late_shipments AS
SELECT o.order_id, c.name AS customer, s.carrier,
       o.promised_date, s.delivered_date,
       s.delivered_date - o.promised_date AS days_late
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN shipments s ON s.order_id = o.order_id
WHERE s.delivered_date > o.promised_date;

-- Move a picked order to SHIPPED and record the shipment
CREATE OR REPLACE PROCEDURE sp_ship_order(p_order_id INT, p_carrier TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_status TEXT;
BEGIN
    SELECT status INTO v_status
    FROM orders WHERE order_id = p_order_id
    FOR UPDATE;

    IF v_status IS NULL THEN
        RAISE EXCEPTION 'Order % does not exist', p_order_id;
    ELSIF v_status <> 'PICKED' THEN
        RAISE EXCEPTION 'Order % has status %, expected PICKED', p_order_id, v_status;
    END IF;

    UPDATE orders SET status = 'SHIPPED' WHERE order_id = p_order_id;

    INSERT INTO shipments (order_id, carrier, shipped_date)
    VALUES (p_order_id, p_carrier, CURRENT_DATE);
END;
$$;