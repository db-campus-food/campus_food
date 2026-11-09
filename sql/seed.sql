-- =========================================================
-- 개발용 가상 샘플 데이터 (is_sample = TRUE)
-- 실제 교내 매장·메뉴 조사가 끝나면 실제 데이터로 교체하세요.
-- =========================================================
USE campus_food;

INSERT INTO building (building_name) VALUES
  ('학생회관'),   -- 1
  ('도서관'),     -- 2
  ('공학관');     -- 3

-- 테스트 관리자 계정: 아이디 admin / 비밀번호 admin1234 (bcrypt 해시)
INSERT INTO admin (admin_name, login_id, password_hash) VALUES
  ('관리자', 'admin', '$2b$12$4FfZCMNYNmmdjUwfignd5u/BIOGn8tHMEcqjE8Sc47Arkj/833Iaq');

INSERT INTO category (category_name) VALUES
  ('한식'), ('중식'), ('일식'), ('양식'), ('분식'), ('음료'), ('디저트');
-- category_id: 1 한식, 2 중식, 3 일식, 4 양식, 5 분식, 6 음료, 7 디저트

INSERT INTO store (store_name, store_type, location_info, is_sample, building_id, admin_id) VALUES
  ('샘플 학생식당',   '학생식당',    '1층',       TRUE, 1, 1),  -- 1
  ('샘플 분식코너',   '일반 음식점', '2층',       TRUE, 1, 1),  -- 2
  ('샘플 북카페',     '카페',        '1층 로비',  TRUE, 2, 1),  -- 3
  ('샘플 덮밥집',     '일반 음식점', '지하 1층',  TRUE, 3, 1),  -- 4
  ('샘플 중식당',     '일반 음식점', '지하 1층',  TRUE, 3, 1),  -- 5
  ('샘플 커피스탠드', '카페',        '3층',       TRUE, 1, 1);  -- 6

INSERT INTO menu (menu_name, price, is_available, is_sample, store_id, category_id) VALUES
  -- 1 샘플 학생식당
  ('제육덮밥',     5500, TRUE,  TRUE, 1, 1),
  ('김치찌개',     6000, TRUE,  TRUE, 1, 1),
  ('된장찌개',     5500, TRUE,  TRUE, 1, 1),
  ('돈까스',       6500, TRUE,  TRUE, 1, 4),
  ('카레라이스',   5000, TRUE,  TRUE, 1, 3),
  -- 2 샘플 분식코너
  ('라면',         3500, TRUE,  TRUE, 2, 5),
  ('떡볶이',       4000, TRUE,  TRUE, 2, 5),
  ('김밥',         3000, TRUE,  TRUE, 2, 5),
  ('참치김밥',     4000, TRUE,  TRUE, 2, 5),
  ('순대',         4500, FALSE, TRUE, 2, 5),   -- 판매 중지 예시 (검색에 안 나옴)
  -- 3 샘플 북카페
  ('아메리카노',   2500, TRUE,  TRUE, 3, 6),
  ('카페라떼',     3200, TRUE,  TRUE, 3, 6),
  ('바닐라라떼',   3700, TRUE,  TRUE, 3, 6),
  ('치즈케이크',   4500, TRUE,  TRUE, 3, 7),
  ('크로플',       3800, TRUE,  TRUE, 3, 7),
  -- 4 샘플 덮밥집
  ('규동',         7000, TRUE,  TRUE, 4, 3),
  ('연어덮밥',     8500, TRUE,  TRUE, 4, 3),
  ('불고기덮밥',   7500, TRUE,  TRUE, 4, 1),
  ('치킨마요덮밥', 6000, TRUE,  TRUE, 4, 1),
  -- 5 샘플 중식당
  ('짜장면',       5500, TRUE,  TRUE, 5, 2),
  ('짬뽕',         6500, TRUE,  TRUE, 5, 2),
  ('탕수육',       9000, TRUE,  TRUE, 5, 2),
  ('볶음밥',       6000, TRUE,  TRUE, 5, 2),
  -- 6 샘플 커피스탠드
  ('아메리카노',   2000, TRUE,  TRUE, 6, 6),
  ('아이스티',     2500, TRUE,  TRUE, 6, 6),
  ('토스트',       3500, TRUE,  TRUE, 6, 4),
  ('마카롱',       2000, TRUE,  TRUE, 6, 7);
