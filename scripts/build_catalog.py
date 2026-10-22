"""직접 작성한 학습 항목 메타데이터를 생성합니다. 공식 본문 수집과는 다릅니다."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = [
    ('app-signing', '앱 서명', '배포', '중급', '/studio/publish/app-signing', '업로드 키와 앱 서명 키, Play 배포 과정의 서명을 학습한다.', 'signing upload key certificate SHA release 배포 서명'),
    ('architecture', '앱 아키텍처', '아키텍처', '초급', '/topic/architecture', 'Android 앱의 계층과 책임 분리를 학습한다.', 'architecture UI data domain repository 아키텍처 구조 설계'),
    ('compose-state', 'Compose 상태 관리', 'Compose', '초급', '/develop/ui/compose/state', 'Compose UI와 상태의 관계, 상태 호이스팅을 학습한다.', 'Compose state remember mutableStateOf 상태 화면'),
    ('compose-architecture', 'Compose UI 아키텍처', 'Compose', '중급', '/develop/ui/compose/architecture', 'Compose의 단방향 데이터 흐름과 UI 설계를 학습한다.', 'Compose UDF state event 단방향 데이터 흐름'),
    ('viewmodel', 'ViewModel', '아키텍처', '초급', '/topic/libraries/architecture/viewmodel', '화면 상태를 관리하는 ViewModel의 역할을 학습한다.', 'ViewModel state lifecycle 화면 상태'),
    ('room', 'Room 데이터베이스', '저장소', '중급', '/training/data-storage/room', 'Room을 통한 로컬 데이터 저장을 학습한다.', 'Room SQL database DAO entity 로컬 데이터베이스'),
    ('datastore', 'DataStore', '저장소', '중급', '/topic/libraries/architecture/datastore', '설정 등의 데이터를 저장하는 DataStore를 학습한다.', 'DataStore preferences settings 설정 저장'),
    ('workmanager', 'WorkManager', '백그라운드', '중급', '/topic/libraries/architecture/workmanager', '지속적인 백그라운드 작업의 예약과 실행을 학습한다.', 'WorkManager worker background 백그라운드 작업'),
    ('camerax', 'CameraX', '카메라', '중급', '/media/camera/camerax', 'CameraX를 사용하는 카메라 앱 개발 개념을 학습한다.', 'CameraX camera preview image capture 카메라 사진 촬영'),
    ('navigation', 'Navigation', '화면 이동', '초급', '/guide/navigation', 'Android 앱의 화면 이동과 백 스택을 학습한다.', 'Navigation route destination back stack 화면 이동'),
    ('permissions', '런타임 권한', '권한', '초급', '/training/permissions/requesting', '런타임 권한 요청과 사용자 응답 처리 과정을 학습한다.', 'permission runtime request 권한 요청'),
    ('lifecycle', 'Activity 생명주기', '컴포넌트', '초급', '/guide/components/activities/activity-lifecycle', 'Activity 상태 변화와 생명주기를 학습한다.', 'Activity lifecycle onCreate onStart onResume 생명주기'),
]

# 항목 이름·기능 소개·분류는 프로젝트용으로 직접 작성한 메타데이터입니다.
# API의 버전별 세부 동작은 외부 공식 문서를 수집한 뒤 근거로 답합니다.
GROUPS = {
'컴포넌트': [
('android.app.Activity','화면을 구성하는 Activity'),
('android.app.Application','앱 프로세스의 Application'),
('android.app.Service','서비스 컴포넌트'),
('android.app.IntentService','기존 IntentService API'),
('android.content.Intent','컴포넌트 사이의 작업 요청'),
('android.content.Context','앱 실행 환경 접근'),
('android.content.BroadcastReceiver','브로드캐스트 수신'),
('android.content.ContentProvider','구조화된 데이터 제공'),
('android.content.ContentResolver','콘텐츠 제공자 접근'),
('android.content.ComponentName','컴포넌트 식별'),
('android.content.IntentFilter','인텐트 필터'),
('android.content.pm.PackageManager','패키지와 앱 정보'),
('android.app.PendingIntent','다른 주체가 실행할 인텐트'),
('android.app.AlarmManager','시간 기반 작업 예약'),
('android.app.job.JobScheduler','작업 예약 서비스'),
('android.app.job.JobInfo','예약 작업 조건'),
('android.app.job.JobService','예약 작업 실행 서비스'),
],
'화면 UI': [
('android.view.View','UI 뷰의 기본 동작'),
('android.view.ViewGroup','뷰 컨테이너'),
('android.view.LayoutInflater','레이아웃 리소스 인플레이션'),
('android.view.Window','화면 창 관리'),
('android.view.MotionEvent','터치 이벤트'),
('android.view.KeyEvent','키 입력 이벤트'),
('android.view.GestureDetector','터치 제스처 감지'),
('android.view.SurfaceView','별도 표면을 가진 뷰'),
('android.view.TextureView','표면 콘텐츠를 표시하는 뷰'),
('android.view.Menu','화면 메뉴'),
('android.view.MenuItem','메뉴 항목'),
('android.view.ViewConfiguration','UI 동작 설정'),
('android.widget.TextView','텍스트 표시'),
('android.widget.EditText','텍스트 입력'),
('android.widget.Button','버튼 입력'),
('android.widget.ImageView','이미지 표시'),
('android.widget.LinearLayout','선형 레이아웃'),
('android.widget.FrameLayout','프레임 레이아웃'),
('android.widget.ScrollView','세로 스크롤 컨테이너'),
('android.widget.ProgressBar','진행 상태 표시'),
('android.widget.Toast','짧은 알림 표시'),
('android.widget.CheckBox','체크 선택 입력'),
('android.widget.RadioButton','라디오 선택 입력'),
('android.widget.Spinner','목록 선택 입력'),
('android.widget.Switch','스위치 입력'),
],
'저장소': [
('android.content.SharedPreferences','키와 값 기반 설정 저장'),
('android.content.ContentValues','데이터베이스에 전달할 값'),
('android.database.Cursor','쿼리 결과 순회'),
('android.database.sqlite.SQLiteDatabase','SQLite 데이터베이스 접근'),
('android.database.sqlite.SQLiteOpenHelper','SQLite 생성과 스키마 관리'),
('android.os.Environment','기기 저장소 환경 정보'),
('android.os.ParcelFileDescriptor','파일 디스크립터 전달'),
('android.provider.MediaStore','미디어 저장소 접근'),
('android.provider.Settings','시스템 설정 접근'),
('android.content.res.Resources','앱 리소스 접근'),
('android.content.res.AssetManager','앱 에셋 접근'),
],
'스레드와 메시지': [
('android.os.Handler','메시지 큐에 작업 전달'),
('android.os.Looper','스레드의 메시지 루프'),
('android.os.Message','메시지 큐의 메시지'),
('android.os.HandlerThread','Looper를 가진 스레드'),
('android.os.Bundle','키와 값 데이터 묶음'),
('android.os.Parcelable','Android 객체 직렬화 인터페이스'),
('android.os.Parcel','IPC 데이터 컨테이너'),
('android.os.ResultReceiver','결과 콜백 전달'),
('android.os.CancellationSignal','취소 신호 전달'),
('android.os.SystemClock','시스템 시간 측정'),
('android.os.Build','기기와 빌드 정보'),
],
'미디어와 그래픽': [
('android.graphics.Bitmap','비트맵 이미지'),
('android.graphics.BitmapFactory','비트맵 디코딩'),
('android.graphics.Canvas','그래픽 그리기'),
('android.graphics.Paint','그리기 스타일'),
('android.graphics.Color','색상 값'),
('android.graphics.Rect','정수 사각형 영역'),
('android.graphics.Matrix','좌표 변환 행렬'),
('android.graphics.Path','도형 경로'),
('android.graphics.drawable.Drawable','그릴 수 있는 리소스'),
('android.media.MediaPlayer','미디어 재생'),
('android.media.MediaRecorder','미디어 녹음과 녹화'),
('android.media.AudioManager','오디오 상태 관리'),
('android.media.ExifInterface','기존 플랫폼 EXIF API'),
('android.hardware.camera2.CameraManager','Camera2 카메라 관리'),
('android.hardware.camera2.CameraDevice','Camera2 카메라 기기'),
('android.hardware.camera2.CaptureRequest','Camera2 캡처 요청'),
],
'기기와 네트워크': [
('android.net.Uri','URI 값'),
('android.net.ConnectivityManager','네트워크 연결 상태'),
('android.net.Network','네트워크 식별과 접근'),
('android.net.NetworkCapabilities','네트워크 기능 정보'),
('android.net.NetworkRequest','네트워크 요청 조건'),
('android.net.wifi.WifiManager','Wi-Fi 관리 API'),
('android.location.Location','위치 데이터'),
('android.location.LocationManager','위치 서비스 접근'),
('android.location.Geocoder','주소와 좌표 변환'),
('android.hardware.Sensor','센서 정보'),
('android.hardware.SensorManager','센서 관리'),
('android.hardware.SensorEvent','센서 이벤트'),
('android.os.Vibrator','진동 기능'),
('android.os.PowerManager','전원 관련 기능'),
('android.app.Notification','알림 데이터'),
('android.app.NotificationManager','알림 게시와 관리'),
('android.app.NotificationChannel','알림 채널'),
('android.util.Log','로그 출력'),
('android.util.SparseArray','정수 키 기반 컨테이너'),
('android.util.LruCache','LRU 캐시'),
],
}


def build():
    items=[]
    for identifier,name,category,level,path,description,keywords in GUIDES:
        items.append({'id':identifier,'name':name,'category':category,'level':level,
                      'description':description,'keywords':keywords,
                      'url':'https://developer.android.com'+path+'?hl=ko'})
    for category, rows in GROUPS.items():
        for qualified, purpose in rows:
            items.append({'id':qualified,'name':qualified.rsplit('.',1)[-1],
                          'category':category,'level':'중급','description':purpose+'을 학습한다.',
                          'keywords':qualified+' '+purpose+' '+category,
                          'url':'https://developer.android.com/reference/'+qualified.replace('.','/')+'?hl=ko'})
    for item in items:
        item.update(author='프로젝트 작성 메타데이터',license='직접 작성한 학습 항목 소개',
                    license_url='https://developer.android.com/license',
                    provenance='메타데이터 직접 작성, 원문 URL은 수집 대상으로 구성. 공식 본문 수집 완료 여부는 별도 집계.')
    assert len(items)>=100
    assert len({row['id'] for row in items})==len(items)
    path=ROOT/'data'/'items.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf-8')
    print(f'Created {len(items)} authored metadata items. External documents are not collected by this command.')

if __name__=='__main__':
    build()
