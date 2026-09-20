-- ===========================================================================
--  Smart Parking Slot System - database schema
--  MySQL 8 / MariaDB 10.4+   |   Engine: InnoDB (needed for transactions)
-- ===========================================================================

DROP DATABASE IF EXISTS smart_parking;
CREATE DATABASE smart_parking
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE smart_parking;

-- ---------------------------------------------------------------------------
-- 1. lots - the physical parking lot (we seed exactly one)
-- ---------------------------------------------------------------------------
CREATE TABLE lots (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(120) NOT NULL,
  address     VARCHAR(255) NOT NULL,
  city        VARCHAR(80)  NOT NULL DEFAULT 'Bengaluru',
  created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 2. levels - Ground, Basement 1, ...
-- ---------------------------------------------------------------------------
CREATE TABLE levels (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  lot_id      INT NOT NULL,
  code        VARCHAR(10)  NOT NULL,          -- 'G', 'B1'
  name        VARCHAR(60)  NOT NULL,          -- 'Ground Floor'
  floor_order INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_levels_lot FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE CASCADE,
  UNIQUE KEY uq_level_code (lot_id, code)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 3. users - drivers and admins
-- ---------------------------------------------------------------------------
CREATE TABLE users (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  name              VARCHAR(120) NOT NULL,
  email             VARCHAR(160) NOT NULL,
  phone             VARCHAR(20)  DEFAULT NULL,
  password_hash     VARCHAR(255) NOT NULL,
  role              ENUM('user','admin') NOT NULL DEFAULT 'user',
  wants_women_slots TINYINT(1)   NOT NULL DEFAULT 0,   -- self-declared opt-in
  is_active         TINYINT(1)   NOT NULL DEFAULT 1,
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_users_email (email),
  KEY idx_users_role (role)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 4. vehicles - saved number plates (Indian format, e.g. KA-01-AB-1234)
-- ---------------------------------------------------------------------------
CREATE TABLE vehicles (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  plate        VARCHAR(16) NOT NULL,
  vehicle_type ENUM('car','bike','scooter','ev_car') NOT NULL DEFAULT 'car',
  is_default   TINYINT(1) NOT NULL DEFAULT 0,
  created_at   TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_vehicles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY uq_vehicle_plate (plate),
  KEY idx_vehicles_user (user_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 5. slots - one row per parking bay, with its position on the SVG map
-- ---------------------------------------------------------------------------
CREATE TABLE slots (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  level_id     INT NOT NULL,
  code         VARCHAR(16) NOT NULL,                                   -- 'G-07'
  slot_type    ENUM('standard','ev','women')       NOT NULL DEFAULT 'standard',
  vehicle_type ENUM('car','bike','ev_car')         NOT NULL DEFAULT 'car',
  pos_x        INT NOT NULL DEFAULT 0,                                 -- SVG coords
  pos_y        INT NOT NULL DEFAULT 0,
  status       ENUM('available','occupied','reserved','disabled') NOT NULL DEFAULT 'available',
  is_active    TINYINT(1) NOT NULL DEFAULT 1,
  note         VARCHAR(160) DEFAULT NULL,
  CONSTRAINT fk_slots_level FOREIGN KEY (level_id) REFERENCES levels(id) ON DELETE CASCADE,
  UNIQUE KEY uq_slot_code (level_id, code),
  KEY idx_slots_status (status),
  KEY idx_slots_type (slot_type),
  KEY idx_slots_level (level_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 6. pricing - admin-editable tariff table
-- ---------------------------------------------------------------------------
CREATE TABLE pricing (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_type  ENUM('car','bike','scooter','ev_car') NOT NULL,
  hourly_rate   DECIMAL(8,2) NOT NULL,
  charging_rate DECIMAL(8,2) NOT NULL DEFAULT 0.00,   -- per hour, EV only
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_pricing_vehicle (vehicle_type)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 7. bookings - a reservation for a time window
-- ---------------------------------------------------------------------------
CREATE TABLE bookings (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  reference       VARCHAR(20) NOT NULL,                  -- 'SPK-100001'
  user_id         INT NOT NULL,
  slot_id         INT NOT NULL,
  vehicle_plate   VARCHAR(16) NOT NULL,
  vehicle_type    ENUM('car','bike','scooter','ev_car') NOT NULL,
  start_ts        DATETIME NOT NULL,
  end_ts          DATETIME NOT NULL,
  status          ENUM('booked','active','completed','cancelled') NOT NULL DEFAULT 'booked',
  charger_type    ENUM('none','ac','dc') NOT NULL DEFAULT 'none',
  charging_addon  TINYINT(1) NOT NULL DEFAULT 0,
  amount_estimate DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_bookings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_bookings_slot FOREIGN KEY (slot_id) REFERENCES slots(id) ON DELETE CASCADE,
  UNIQUE KEY uq_booking_reference (reference),
  KEY idx_bookings_slot_time (slot_id, start_ts, end_ts),
  KEY idx_bookings_user (user_id, status),
  KEY idx_bookings_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 8. payments - one row per payment attempt (simulated in this demo)
-- ---------------------------------------------------------------------------
CREATE TABLE payments (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT NOT NULL,
  amount     DECIMAL(10,2) NOT NULL,
  method     ENUM('upi','card','exit') NOT NULL,
  status     ENUM('pending','paid','failed','refunded') NOT NULL DEFAULT 'pending',
  txn_ref    VARCHAR(40) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
  KEY idx_payments_status (status),
  KEY idx_payments_created (created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 9. parking_sessions - what actually happened at the boom barrier
-- ---------------------------------------------------------------------------
CREATE TABLE parking_sessions (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  booking_id    INT DEFAULT NULL,
  slot_id       INT NOT NULL,
  vehicle_plate VARCHAR(16) NOT NULL,
  entry_ts      DATETIME NOT NULL,
  exit_ts       DATETIME DEFAULT NULL,
  billed_hours  INT DEFAULT NULL,
  amount        DECIMAL(10,2) DEFAULT NULL,
  status        ENUM('inside','exited') NOT NULL DEFAULT 'inside',
  CONSTRAINT fk_sessions_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
  CONSTRAINT fk_sessions_slot FOREIGN KEY (slot_id) REFERENCES slots(id) ON DELETE CASCADE,
  KEY idx_sessions_status (status),
  KEY idx_sessions_entry (entry_ts),
  KEY idx_sessions_plate (vehicle_plate)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 10. ev_charging_sessions - energy delivered to an EV bay
-- ---------------------------------------------------------------------------
CREATE TABLE ev_charging_sessions (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  booking_id   INT DEFAULT NULL,
  slot_id      INT NOT NULL,
  charger_type ENUM('ac','dc') NOT NULL DEFAULT 'ac',
  start_ts     DATETIME NOT NULL,
  end_ts       DATETIME DEFAULT NULL,
  kwh          DECIMAL(6,2) NOT NULL DEFAULT 0.00,
  amount       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  CONSTRAINT fk_ev_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
  CONSTRAINT fk_ev_slot FOREIGN KEY (slot_id) REFERENCES slots(id) ON DELETE CASCADE,
  KEY idx_ev_slot (slot_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 11. sos_alerts - raised from a Women's Safety slot or an active ticket
-- ---------------------------------------------------------------------------
CREATE TABLE sos_alerts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  slot_id     INT DEFAULT NULL,
  booking_id  INT DEFAULT NULL,
  message     VARCHAR(255) DEFAULT NULL,
  status      ENUM('open','resolved') NOT NULL DEFAULT 'open',
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at DATETIME DEFAULT NULL,
  resolved_by INT DEFAULT NULL,
  CONSTRAINT fk_sos_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_sos_slot FOREIGN KEY (slot_id) REFERENCES slots(id) ON DELETE SET NULL,
  CONSTRAINT fk_sos_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
  CONSTRAINT fk_sos_admin FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
  KEY idx_sos_status (status, created_at)
) ENGINE=InnoDB;