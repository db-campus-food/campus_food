-- =========================================================
-- 테스트용 임시 데이터 (가상 데이터)
-- 실제 교내 매장·메뉴 조사가 끝나면 이 파일 내용을 교체하세요.
-- =========================================================
USE campus_food;

INSERT INTO building (building_name) VALUES
  ('학생회관'), ('도서관'), ('공학관');

-- 테스트 관리자 계정: 아이디 admin / 비밀번호 admin1234 (bcrypt 해시)
INSERT INTO admin (admin_name, login_id, password_hash) VALUES
  ('관리자', 'admin', '$2b$12$4FfZCMNYNmmdjUwfignd5u/BIOGn8tHMEcqjE8Sc47Arkj/833Iaq');

INSERT INTO category (category_name) VALUES
  ('한식'), ('중식'), ('일식'), ('양식'), ('분식'), ('음료'), ('디저트');

INSERT INTO store (store_name, store_type, location_info, building_id, admin_id) VALUES
  ('학생식당',     '학생식당',   '학생회관 1층',  1, 1),
  ('분식코너',     '일반음식점', '학생회관 2층',  1, 1),
  ('도서관 카페',  '카페',       '도서관 1층 로비', 2, 1),
  ('공학관 덮밥집', '일반음식점', '공학관 지하 1층', 3, 1);

-- category_id: 1 한식, 2 중식, 3 일식, 4 양식, 5 분식, 6 음료, 7 디저트
INSERT INTO menu (menu_name, price, store_id, category_id) VALUES
  ('제육덮밥',     5500, 1, 1),
  ('김치찌개',     6000, 1, 1),
  ('돈까스',       6500, 1, 4),
  ('짜장면',       5000, 1, 2),
  ('라면',         3500, 2, 5),
  ('떡볶이',       4000, 2, 5),
  ('김밥',         3000, 2, 5),
  ('아메리카노',   2500, 3, 6),
  ('카페라떼',     3200, 3, 6),
  ('치즈케이크',   4500, 3, 7),
  ('규동',         7000, 4, 3),
  ('연어덮밥',     8500, 4, 3),
  ('불고기덮밥',   7500, 4, 1);
