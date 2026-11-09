-- =========================================================
-- 교내 음식점·카페 메뉴 통합 관리 시스템 : 테이블 생성
-- 실행하면 기존 campus_food DB를 지우고 새로 만듭니다.
-- =========================================================
DROP DATABASE IF EXISTS campus_food;
CREATE DATABASE campus_food DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE campus_food;

-- 건물
CREATE TABLE building (
  building_id   INT AUTO_INCREMENT PRIMARY KEY,
  building_name VARCHAR(50) NOT NULL UNIQUE
);

-- 관리자
CREATE TABLE admin (
  admin_id      INT AUTO_INCREMENT PRIMARY KEY,
  admin_name    VARCHAR(30)  NOT NULL,
  login_id      VARCHAR(30)  NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL
);

-- 음식 카테고리
CREATE TABLE category (
  category_id   INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(20) NOT NULL UNIQUE
);

-- 매장
CREATE TABLE store (
  store_id      INT AUTO_INCREMENT PRIMARY KEY,
  store_name    VARCHAR(50) NOT NULL,
  store_type    ENUM('학생식당','일반음식점','카페') NOT NULL,
  location_info VARCHAR(100),
  building_id   INT NOT NULL,
  admin_id      INT NULL,
  CONSTRAINT fk_store_building FOREIGN KEY (building_id)
    REFERENCES building(building_id) ON DELETE RESTRICT,
  CONSTRAINT fk_store_admin FOREIGN KEY (admin_id)
    REFERENCES admin(admin_id) ON DELETE SET NULL
);

-- 메뉴
CREATE TABLE menu (
  menu_id      INT AUTO_INCREMENT PRIMARY KEY,
  menu_name    VARCHAR(50)  NOT NULL,
  price        INT UNSIGNED NOT NULL,
  is_available BOOLEAN      NOT NULL DEFAULT TRUE,
  store_id     INT NOT NULL,
  category_id  INT NOT NULL,
  updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uq_menu_store_name UNIQUE (store_id, menu_name),
  CONSTRAINT fk_menu_store FOREIGN KEY (store_id)
    REFERENCES store(store_id) ON DELETE CASCADE,
  CONSTRAINT fk_menu_category FOREIGN KEY (category_id)
    REFERENCES category(category_id) ON DELETE RESTRICT,
  INDEX idx_menu_price (price)
);
