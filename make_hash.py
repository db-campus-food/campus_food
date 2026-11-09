"""관리자 비밀번호 해시 만들기.

사용법:  python make_hash.py 내비밀번호
출력된 값(맨 앞이 $2b$ 로 시작)을 admin 테이블의 password_hash 에 넣는다.
비밀번호 원문은 DB나 GitHub에 저장하지 않는다.
"""
import sys

import bcrypt

if len(sys.argv) != 2:
    print("사용법: python make_hash.py 내비밀번호")
    sys.exit(1)

print(bcrypt.hashpw(sys.argv[1].encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))
