# GitLab 업로드 방법 — Windows / VS Code

대상: 처음 Git 저장소에 올리는 사용자. 아래는 **커밋이 없는 빈 GitLab 저장소**에 올리는 절차다. 수업에서 지정한 GitLab 서버·그룹·저장소가 있으면 그것을 우선 사용한다. GitLab.com 계정을 별도로 만들 필요가 있는지는 수업 안내를 따른다.

## 1. 준비

1. 현재 작동하는 프로젝트를 다른 폴더에 백업한다.
2. 이 ZIP을 별도 위치에 풀어 내용부터 확인한다. 원본 starter를 사용 중이라면 docs, README.md, .gitignore, .env.example을 반영한다. .env는 기존 파일을 유지한다. 실제 소스를 수정했다면 덮어쓰지 말고 문서를 실제 코드에 맞춘다.
3. VS Code에서 app.py가 바로 있는 android-rag-mentor 폴더를 연다.
4. Terminal → New Terminal에서 PowerShell을 선택한다. Git 업로드는 가상환경 활성화가 필요 없다.

```powershell
cd C:\Users\SSAFY\android-rag-mentor
git --version
```

Git 명령을 찾지 못하면 https://git-scm.com/downloads/win 에서 Git을 설치하고 VS Code를 다시 연다.

## 2. GitLab 저장소 준비

수업에서 저장소를 지정했다면 해당 프로젝트를 사용한다. 새 저장소를 직접 만들 때는 GitLab 로그인 → New project/repository → Create blank project로 이동한다.

- Project name: android-rag-mentor
- Namespace: 제출할 본인 또는 수업 그룹
- Visibility: 수업 지침에 맞춤. 공개 지시가 없으면 Private로 시작 가능.
- Initialize repository with a README: **체크 해제**. 로컬 README가 있기 때문.
- Create project를 선택한다.

Code 또는 Clone 메뉴에서 **Clone with HTTPS** 주소를 복사한다. 주소는 사이트에 따라 https://서버/그룹/프로젝트.git 형태다. 브라우저의 /-/tree/... 주소를 사용하지 않는다.

## 3. 로컬 Git 시작

이름·이메일은 본인 것으로 바꾼다. GitLab 비밀번호나 GMS 키를 입력하는 곳이 아니다.

```powershell
git init
git config user.name "본인 이름"
git config user.email "본인 이메일"
git remote -v
git status --short
```

이미 origin이 있으면 주소를 확인한다. 제출할 GitLab 주소와 같으면 아래 remote add 명령을 생략한다. 다른 주소라면 기존 연결을 임의로 바꾸지 말고 제출 대상과 기존 저장소의 관계부터 확인한다.

## 4. 업로드 파일 점검과 커밋

```powershell
git add .
git diff --cached --name-only
```

목록에 app.py, mentor, scripts, tests, data, docs, README.md, requirements.txt, settings.toml, .gitignore, .env.example 등이 보이면 된다. **.env, .venv, storage, 실제 키가 적힌 파일은 보이면 안 된다.** .env.example은 빈 키 예제이므로 포함해도 된다.

새로 추가한 .env가 보이면 다음 명령으로 추적 대상에서만 빼고 .gitignore를 확인한다. 로컬 .env 파일은 삭제되지 않는다. 과거 커밋에 이미 실제 키를 올렸다면 추적 해제만으로 과거 기록은 없어지지 않으므로 해당 키 폐기·재발급 및 기록 정리가 필요하다.

```powershell
git rm --cached -- .env
```

.env가 목록에 없으면 위 명령은 실행하지 않아도 된다. 점검이 끝나면 커밋한다.

```powershell
git commit -m "Add Android RAG mentor and project documents"
git branch -M main
```

## 5. 연결과 push

아래 주소는 예시다. GitLab에서 복사한 **실제 Clone with HTTPS 주소**로 바꾼다. origin이 이미 같은 주소로 연결됐다면 첫 줄은 생략한다.

```powershell
git remote add origin https://gitlab.example.com/your-group/android-rag-mentor.git
git push -u origin main
```

로그인 창이 나오면 GitLab 계정으로 인증한다. HTTPS에서 비밀번호 대신 토큰이 필요한 환경이면 본인 GitLab 서버의 Personal access token을 만든 뒤 비밀번호 입력란에 넣는다. Git push용 기존 방식 토큰은 write_repository 권한이 필요하며, 기관 정책을 따른다. 토큰을 코드·README·remote 주소·채팅에 넣지 않는다.

오류별 처리:

| 오류 | 확인할 것 |
|---|---|
| remote origin already exists | git remote -v로 기존 주소 확인, 같으면 add 생략 |
| src refspec main does not match any | 커밋 생성 여부와 현재 브랜치 확인 |
| HTTP Basic Access denied / 401 | 서버·계정·인증 방식·토큰 만료 확인 |
| 403 / protected branch | 해당 그룹의 push 권한 및 보호 브랜치 정책 확인, 필요하면 허용된 작업 브랜치와 MR 사용 |
| rejected / fetch first / non-fast-forward | 원격에 이미 커밋 있음. 강제 push하지 말고 아래 기존 저장소 절차 사용 |

## 이미 README나 다른 커밋이 있는 GitLab 저장소라면

위 빈 저장소 push 절차 대신 별도 폴더에 저장소를 clone한 뒤 프로젝트 파일을 그 안에 복사하는 방법을 사용한다. 원격 파일을 먼저 보존하며 .git, .env, .venv, storage는 복사 대상에서 제외한다. 폴더가 중첩되지 않게 clone한 폴더 바로 아래에 app.py를 둔다.

```powershell
cd C:\Users\SSAFY
git clone https://gitlab.example.com/your-group/android-rag-mentor.git android-rag-mentor-gitlab
cd android-rag-mentor-gitlab
```

파일 복사 후 git status → git add . → 추적 목록 점검 → git commit → git push 순서로 실행한다. 강제 push로 원격 작업을 덮어쓰지 않는다.

## 6. 업로드 완료 확인

GitLab 페이지를 새로고침해 README와 docs, app.py가 보이는지 확인한다. Markdown 문서는 GitLab 화면에서 읽을 수 있다. ZIP만 올린 상태는 소스 제출 구조와 다르다.

- [ ] main 또는 제출 지정 브랜치에 파일 존재
- [ ] 여섯 제출물이 README 링크에서 열림
- [ ] .env, .venv, storage와 실제 키 없음
- [ ] 작성자 정보와 실제 검증 결과 반영
- [ ] 강사에게 공유할 프로젝트 주소 확인 및 열람 권한 설정

이후 수정할 때는 git add . → 추적 목록 점검 → git commit -m "Update project documents" → git push 순서다.

## 공식 참고 문서

- https://docs.gitlab.com/user/project/
- https://docs.gitlab.com/topics/git/project/
- https://docs.gitlab.com/user/profile/personal_access_tokens/

확인일: 2026-10-22. 수업용 GitLab은 버전에 따라 메뉴 명칭이 다를 수 있다.
