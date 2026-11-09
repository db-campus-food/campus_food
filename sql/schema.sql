-- =========================================================
-- 교내 음식점·카페 메뉴 통합 관리 시스템 : 테이블 생성
-- 팀 ERD(교내 메뉴 추천 시스템 ERD)와 동일한 구조 · MySQL 8.0.16 이상
-- 실행하면 기존 campus_food DB를 지우고 새로 만듭니다.
-- =========================================================
DROP DATABASE IF EXISTS campus_food;
CREATE DATABASE campus_food DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE campus_food;

-- 건물
CREATE TABLE building (
  building_id   INT AUTO_INCREMENT PRIMARY KEY,
  building_name VARCHAR(100) NOT NULL UNIQUE
);

-- 관리자 (계정은 INSERT로 미리 만들어 둠)
CREATE TABLE admin (
  admin_id      INT AUTO_INCREMENT PRIMARY KEY,
  admin_name    VARCHAR(50)  NOT NULL,
  login_id      VARCHAR(50)  NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL
);

-- 음식 카테고리
CREATE TABLE category (
  category_id   INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(50) NOT NULL UNIQUE
);

-- 매장 (담당 관리자 한 명이 꼭 있음)
CREATE TABLE store (
  store_id      INT AUTO_INCREMENT PRIMARY KEY,
  store_name    VARCHAR(100) NOT NULL,
  store_type    VARCHAR(30)  NOT NULL,
  location_info VARCHAR(100) NULL,              -- 세부 위치만 (건물명 제외)
  is_sample     BOOLEAN      NOT NULL DEFAULT FALSE,
  building_id   INT NOT NULL,
  admin_id      INT NOT NULL,
  CONSTRAINT ck_store_type CHECK (store_type IN ('학생식당', '일반 음식점', '카페')),
  CONSTRAINT fk_store_building FOREIGN KEY (building_id)
    REFERENCES building(building_id) ON DELETE RESTRICT,
  CONSTRAINT fk_store_admin FOREIGN KEY (admin_id)
    REFERENCES admin(admin_id) ON DELETE RESTRICT
);

-- 메뉴
CREATE TABLE menu (
  menu_id      INT AUTO_INCREMENT PRIMARY KEY,
  menu_name    VARCHAR(100) NOT NULL,
  price        INT          NOT NULL,
  is_available BOOLEAN      NOT NULL DEFAULT TRUE,
  is_sample    BOOLEAN      NOT NULL DEFAULT FALSE,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  store_id     INT NOT NULL,
  category_id  INT NOT NULL,
  CONSTRAINT ck_menu_price CHECK (price >= 0),
  CONSTRAINT uq_menu_store_name UNIQUE (store_id, menu_name),
  CONSTRAINT fk_menu_store FOREIGN KEY (store_id)
    REFERENCES store(store_id) ON DELETE CASCADE,
  CONSTRAINT fk_menu_category FOREIGN KEY (category_id)
    REFERENCES category(category_id) ON DELETE RESTRICT
);
