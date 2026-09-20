-- ===========================================================================
--  Smart Parking Slot System - demo data
--
--  Import this AFTER schema.sql.
--  Then run:  python setup_db.py
--  (that script replaces the placeholder password hashes below with real
--   Werkzeug PBKDF2 hashes for the demo password  Password@123 )
-- ===========================================================================

USE smart_parking;

-- ---------------------------------------------------------------------------
-- The parking lot
-- ---------------------------------------------------------------------------
INSERT INTO lots (id, name, address, city) VALUES
(1, 'Prestige Aurora Parking', '24, Lavelle Road, Ashok Nagar', 'Bengaluru');

-- ---------------------------------------------------------------------------
-- Two levels
-- ---------------------------------------------------------------------------
INSERT INTO levels (id, lot_id, code, name, floor_order) VALUES
(1, 1, 'G',  'Ground Floor', 0),
(2, 1, 'B1', 'Basement 1',   1);

-- ---------------------------------------------------------------------------
-- 48 slots: 3 EV + 3 Women's Safety per level.
-- Women's Safety bays sit in row 1 next to the entrance and security cabin.
-- Rows 1-3 are car bays, row 4 is two-wheeler bays.
-- pos_x / pos_y are the coordinates used by the SVG floor plan.
-- ---------------------------------------------------------------------------
INSERT INTO slots (id, level_id, code, slot_type, vehicle_type, pos_x, pos_y, status, note) VALUES
-- ---------------------------- Ground Floor --------------------------------
(1,  1, 'G-01',  'women',    'car',     200, 130, 'available', 'Women''s Safety zone - beside security cabin'),
(2,  1, 'G-02',  'women',    'car',     330, 130, 'available', 'Women''s Safety zone - beside security cabin'),
(3,  1, 'G-03',  'women',    'car',     460, 130, 'available', 'Women''s Safety zone - beside security cabin'),
(4,  1, 'G-04',  'standard', 'car',     590, 130, 'available', NULL),
(5,  1, 'G-05',  'standard', 'car',     720, 130, 'occupied',  NULL),
(6,  1, 'G-06',  'standard', 'car',     850, 130, 'available', NULL),
(7,  1, 'G-07',  'ev',       'ev_car',  200, 240, 'available', 'EV charger - AC or DC'),
(8,  1, 'G-08',  'ev',       'ev_car',  330, 240, 'available', 'EV charger - AC or DC'),
(9,  1, 'G-09',  'ev',       'ev_car',  460, 240, 'available', 'EV charger - AC or DC'),
(10, 1, 'G-10',  'standard', 'car',     590, 240, 'available', NULL),
(11, 1, 'G-11',  'standard', 'car',     720, 240, 'reserved',  NULL),
(12, 1, 'G-12',  'standard', 'car',     850, 240, 'available', NULL),
(13, 1, 'G-13',  'standard', 'car',     200, 350, 'available', NULL),
(14, 1, 'G-14',  'standard', 'car',     330, 350, 'available', NULL),
(15, 1, 'G-15',  'standard', 'car',     460, 350, 'available', NULL),
(16, 1, 'G-16',  'standard', 'car',     590, 350, 'available', NULL),
(17, 1, 'G-17',  'standard', 'car',     720, 350, 'available', NULL),
(18, 1, 'G-18',  'standard', 'car',     850, 350, 'available', NULL),
(19, 1, 'G-19',  'standard', 'bike',    200, 460, 'available', 'Two-wheeler bay'),
(20, 1, 'G-20',  'standard', 'bike',    330, 460, 'available', 'Two-wheeler bay'),
(21, 1, 'G-21',  'standard', 'bike',    460, 460, 'available', 'Two-wheeler bay'),
(22, 1, 'G-22',  'standard', 'bike',    590, 460, 'available', 'Two-wheeler bay'),
(23, 1, 'G-23',  'standard', 'bike',    720, 460, 'available', 'Two-wheeler bay'),
(24, 1, 'G-24',  'standard', 'bike',    850, 460, 'available', 'Two-wheeler bay'),
-- ---------------------------- Basement 1 ----------------------------------
(25, 2, 'B1-01', 'women',    'car',     200, 130, 'available', 'Women''s Safety zone - beside security cabin'),
(26, 2, 'B1-02', 'women',    'car',     330, 130, 'available', 'Women''s Safety zone - beside security cabin'),
(27, 2, 'B1-03', 'women',    'car',     460, 130, 'available', 'Women''s Safety zone - beside security cabin'),
(28, 2, 'B1-04', 'standard', 'car',     590, 130, 'occupied',  NULL),
(29, 2, 'B1-05', 'standard', 'car',     720, 130, 'available', NULL),
(30, 2, 'B1-06', 'standard', 'car',     850, 130, 'available', NULL),
(31, 2, 'B1-07', 'ev',       'ev_car',  200, 240, 'available', 'EV charger - AC or DC'),
(32, 2, 'B1-08', 'ev',       'ev_car',  330, 240, 'available', 'EV charger - AC or DC'),
(33, 2, 'B1-09', 'ev',       'ev_car',  460, 240, 'available', 'EV charger - AC or DC'),
(34, 2, 'B1-10', 'standard', 'car',     590, 240, 'available', NULL),
(35, 2, 'B1-11', 'standard', 'car',     720, 240, 'available', NULL),
(36, 2, 'B1-12', 'standard', 'car',     850, 240, 'available', NULL),
(37, 2, 'B1-13', 'standard', 'car',     200, 350, 'reserved',  NULL),
(38, 2, 'B1-14', 'standard', 'car',     330, 350, 'available', NULL),
(39, 2, 'B1-15', 'standard', 'car',     460, 350, 'available', NULL),
(40, 2, 'B1-16', 'standard', 'car',     590, 350, 'available', NULL),
(41, 2, 'B1-17', 'standard', 'car',     720, 350, 'available', NULL),
(42, 2, 'B1-18', 'standard', 'car',     850, 350, 'available', NULL),
(43, 2, 'B1-19', 'standard', 'bike',    200, 460, 'available', 'Two-wheeler bay'),
(44, 2, 'B1-20', 'standard', 'bike',    330, 460, 'available', 'Two-wheeler bay'),
(45, 2, 'B1-21', 'standard', 'bike',    460, 460, 'available', 'Two-wheeler bay'),
(46, 2, 'B1-22', 'standard', 'bike',    590, 460, 'available', 'Two-wheeler bay'),
(47, 2, 'B1-23', 'standard', 'bike',    720, 460, 'available', 'Two-wheeler bay'),
(48, 2, 'B1-24', 'standard', 'bike',    850, 460, 'occupied',  'Two-wheeler bay');

-- ---------------------------------------------------------------------------
-- Users.  password_hash is a placeholder - setup_db.py replaces it with a
-- real Werkzeug hash for the demo password  Password@123
-- ---------------------------------------------------------------------------
INSERT INTO users (id, name, email, phone, password_hash, role, wants_women_slots, created_at) VALUES
(1, 'Ananya Rao (Admin)', 'admin@smartpark.in',  '+91 80 4123 9900', 'RESET_ME', 'admin', 0, NOW() - INTERVAL 120 DAY),
(2, 'Aarthi Nair',        'aarthi@example.com',  '+91 98450 11223', 'RESET_ME', 'user',  0, NOW() - INTERVAL 90 DAY),
(3, 'Rohan Deshpande',    'rohan@example.com',   '+91 99001 44556', 'RESET_ME', 'user',  0, NOW() - INTERVAL 60 DAY),
(4, 'Meera Iyer',         'meera@example.com',   '+91 97400 77889', 'RESET_ME', 'user',  1, NOW() - INTERVAL 45 DAY),
(5, 'Karthik Reddy',      'karthik@example.com', '+91 90080 33445', 'RESET_ME', 'user',  0, NOW() - INTERVAL 30 DAY),
(6, 'Sneha Kulkarni',     'sneha@example.com',   '+91 88840 99112', 'RESET_ME', 'user',  1, NOW() - INTERVAL 12 DAY);

-- ---------------------------------------------------------------------------
-- Saved vehicles (Indian number plates)
-- ---------------------------------------------------------------------------
INSERT INTO vehicles (id, user_id, plate, vehicle_type, is_default) VALUES
(1, 2, 'KA-01-AB-1234', 'car',     1),
(2, 2, 'KA-01-BK-5566', 'bike',    0),
(3, 3, 'KA-05-MJ-7788', 'car',     1),
(4, 4, 'KA-03-HX-4521', 'scooter', 1),
(5, 5, 'KA-02-QR-9012', 'car',     1),
(6, 6, 'KA-04-EV-3311', 'ev_car',  1);

-- ---------------------------------------------------------------------------
-- Tariff table (admin editable from the dashboard)
-- ---------------------------------------------------------------------------
INSERT INTO pricing (vehicle_type, hourly_rate, charging_rate) VALUES
('bike',    10.00,  0.00),
('scooter', 10.00,  0.00),
('car',     30.00,  0.00),
('ev_car',  30.00, 12.00);

-- ---------------------------------------------------------------------------
-- Bookings - a realistic mix of past, active and upcoming
-- ---------------------------------------------------------------------------
INSERT INTO bookings
  (id, reference, user_id, slot_id, vehicle_plate, vehicle_type,
   start_ts, end_ts, status, charger_type, charging_addon, amount_estimate, created_at) VALUES
-- completed earlier today on G-05
(1, 'SPK-100001', 2, 5,  'KA-01-AB-1234', 'car',
   DATE_ADD(CURDATE(), INTERVAL 9 HOUR), DATE_ADD(CURDATE(), INTERVAL 12 HOUR),
   'completed', 'none', 0, 90.00, NOW() - INTERVAL 6 HOUR),
-- EV charging right now on G-07
(2, 'SPK-100002', 6, 7,  'KA-04-EV-3311', 'ev_car',
   DATE_SUB(NOW(), INTERVAL 60 MINUTE), DATE_ADD(NOW(), INTERVAL 120 MINUTE),
   'active', 'dc', 1, 126.00, NOW() - INTERVAL 90 MINUTE),
-- car parked right now on B1-04
(3, 'SPK-100003', 5, 28, 'KA-02-QR-9012', 'car',
   DATE_SUB(NOW(), INTERVAL 30 MINUTE), DATE_ADD(NOW(), INTERVAL 150 MINUTE),
   'active', 'none', 0, 90.00, NOW() - INTERVAL 45 MINUTE),
-- upcoming tomorrow on G-11
(4, 'SPK-100004', 3, 11, 'KA-05-MJ-7788', 'car',
   DATE_ADD(DATE_ADD(CURDATE(), INTERVAL 1 DAY), INTERVAL 9 HOUR),
   DATE_ADD(DATE_ADD(CURDATE(), INTERVAL 1 DAY), INTERVAL 18 HOUR),
   'booked', 'none', 0, 270.00, NOW() - INTERVAL 20 MINUTE),
-- upcoming tomorrow on B1-13 (payment still pending)
(5, 'SPK-100005', 4, 37, 'KA-03-HX-4521', 'scooter',
   DATE_ADD(DATE_ADD(CURDATE(), INTERVAL 1 DAY), INTERVAL 14 HOUR),
   DATE_ADD(DATE_ADD(CURDATE(), INTERVAL 1 DAY), INTERVAL 17 HOUR),
   'booked', 'none', 0, 30.00, NOW() - INTERVAL 5 MINUTE),
-- yesterday's two-wheeler trip on G-14
(6, 'SPK-100006', 2, 14, 'KA-01-BK-5566', 'bike',
   DATE_ADD(DATE_SUB(CURDATE(), INTERVAL 1 DAY), INTERVAL 8 HOUR),
   DATE_ADD(DATE_SUB(CURDATE(), INTERVAL 1 DAY), INTERVAL 10 HOUR),
   'completed', 'none', 0, 20.00, NOW() - INTERVAL 30 HOUR);

-- ---------------------------------------------------------------------------
-- Payments
-- ---------------------------------------------------------------------------
INSERT INTO payments (id, booking_id, amount, method, status, txn_ref, created_at) VALUES
(1, 1,  90.00, 'upi',  'paid',    'TXN-8F41C2A7', NOW() - INTERVAL 6 HOUR),
(2, 2, 126.00, 'card', 'paid',    'TXN-2B90D551', NOW() - INTERVAL 90 MINUTE),
(3, 3,  90.00, 'exit', 'pending', 'TXN-PAY-AT-EXIT', NOW() - INTERVAL 45 MINUTE),
(4, 4, 270.00, 'upi',  'paid',    'TXN-71AE33C8', NOW() - INTERVAL 20 MINUTE),
(5, 5,  30.00, 'upi',  'pending', 'TXN-0C55A914', NOW() - INTERVAL 5 MINUTE),
(6, 6,  20.00, 'upi',  'paid',    'TXN-55D0E7B2', NOW() - INTERVAL 30 HOUR);

-- ---------------------------------------------------------------------------
-- Parking sessions (entry / exit desk)
-- ---------------------------------------------------------------------------
INSERT INTO parking_sessions
  (id, booking_id, slot_id, vehicle_plate, entry_ts, exit_ts, billed_hours, amount, status) VALUES
(1, 1, 5,  'KA-01-AB-1234',
   DATE_ADD(CURDATE(), INTERVAL 9 HOUR) + INTERVAL 5 MINUTE,
   DATE_ADD(CURDATE(), INTERVAL 11 HOUR) + INTERVAL 40 MINUTE,
   3, 90.00, 'exited'),
(2, 2, 7,  'KA-04-EV-3311',
   DATE_SUB(NOW(), INTERVAL 55 MINUTE), NULL, NULL, NULL, 'inside'),
(3, 3, 28, 'KA-02-QR-9012',
   DATE_SUB(NOW(), INTERVAL 25 MINUTE), NULL, NULL, NULL, 'inside'),
(4, 6, 14, 'KA-01-BK-5566',
   DATE_ADD(DATE_SUB(CURDATE(), INTERVAL 1 DAY), INTERVAL 8 HOUR) + INTERVAL 5 MINUTE,
   DATE_ADD(DATE_SUB(CURDATE(), INTERVAL 1 DAY), INTERVAL 10 HOUR) + INTERVAL 5 MINUTE,
   2, 20.00, 'exited');

-- ---------------------------------------------------------------------------
-- EV charging session in progress on G-07
-- ---------------------------------------------------------------------------
INSERT INTO ev_charging_sessions
  (id, booking_id, slot_id, charger_type, start_ts, end_ts, kwh, amount) VALUES
(1, 2, 7, 'dc', DATE_SUB(NOW(), INTERVAL 50 MINUTE), NULL, 0.00, 0.00);

-- ---------------------------------------------------------------------------
-- One historical SOS alert, already resolved
-- ---------------------------------------------------------------------------
INSERT INTO sos_alerts
  (id, user_id, slot_id, booking_id, message, status, created_at, resolved_at, resolved_by) VALUES
(1, 4, 37, 5,
 'Someone was loitering near the Basement 1 lift lobby and followed me to the bay.',
 'resolved', NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 6 MINUTE, 1);