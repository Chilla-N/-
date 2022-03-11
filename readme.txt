hyper-V를 자동으로 생성, 정지, 삭제할 수 있는 기능을 가진 웹서비스 입니다.
초기 admin db를 구현할 필요가 있습니다.
MongoDB기반의 DB를 사용합니다.
bat파일의 절대경로를 수정하여 사용해야 합니다
ps1파일의 이미지경로를 수정하여 사용해야 합니다.


derectory:
    python 코드설명: flask 코드에 설명이 추가된 파일(중요)
    _pycache_:플라스크 실행시 자동생성파일
    CSsharpDriver: 파워쉘에서 mongoDB제어 드라이버
    static: 웹사이트 이미지 및 js, Css
    templates:웹사이트 html
file:
    app.py: 플라스크 핵심코드
    creat_Vm.ps1: 파워쉘을 통한 hyper-v VM 생성제어 스크립트
    stop_Vm.ps1: 파워쉘을 통한 hyper-v VM 정지제어 스크립트
    create.bat: 파워쉘 스크립트 관리자실행을 위한 cmd 스크립트 (절대경로 수정필요)
    stop.bat: 파워쉘 스크립트 관리자실행을 위한 cmd 스크립트 (절대경로 수정필요)

