import os
import subprocess
import shutil
import sys
import io

# 인코딩 설정
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

textFilePath = "/home/alpha/texts"
vimrcPath = os.path.expanduser("~/.vimrc")
backupVimrcPath = os.path.expanduser("~/.alphawriter")

def changeVimrcName(newName):
    if os.path.exists(backupVimrcPath):
        os.rename(backupVimrcPath, newName)

def restoreVimrcName(originalName):
    if os.path.exists(originalName):
        os.rename(originalName, backupVimrcPath)

def listFiles():
    try:
        print("제목 | 생성 날짜 | 수정 날짜")
        files = os.listdir(textFilePath)
        for file in files:
            if file.endswith('.txt'):
                filePath = os.path.join(textFilePath, file)
                created = os.path.getctime(filePath)
                modified = os.path.getmtime(filePath)
                print(f"{file} | {created} | {modified}")
        
        usbBasePath = "/media/alpha"
        devices = [d for d in os.listdir(usbBasePath) if os.path.ismount(os.path.join(usbBasePath, d))]

        if devices:
            print("\n[외부장치]")
            for deviceName in devices:
                devicePath = os.path.join(usbBasePath, deviceName)
                if os.path.isdir(devicePath):
                    externalFiles = os.listdir(devicePath)
                    for extFile in externalFiles:
                        if extFile.endswith('.txt'):
                            extFilePath = os.path.join(devicePath, extFile)
                            extCreated = os.path.getctime(extFilePath)
                            extModified = os.path.getmtime(extFilePath)
                            print(f"{extFile} | {extCreated} | {extModified}")
        else:
            print("\n[*] 외부 저장장치가 없습니다.")
    except Exception as e:
        print(f"[!] 파일 목록을 불러오는 중 오류 발생: {e}")

def createFile(title):
    if not title.strip():
        print("[!] 제목을 입력해야 합니다.")
        return
    filePath = os.path.join(textFilePath, f"{title}.txt")
    if os.path.exists(filePath):
        print("[!] 이미 존재하는 제목입니다.")
    else:
        try:
            changeVimrcName(vimrcPath)
            subprocess.run(['vim', filePath])
            restoreVimrcName(vimrcPath)
            print(f"[*] '{title}'을(를) 작성했습니다.")
        except Exception as e:
            restoreVimrcName(vimrcPath)
            print(f"[!] 파일을 여는 중 오류 발생: {e}")

def editFile(title):
    if not title.strip():
        print("[!] 제목을 입력해야 합니다.")
        return
    filePath = os.path.join(textFilePath, f"{title}.txt")
    if not os.path.exists(filePath):
        print("[!] 존재하지 않는 글입니다.")
    else:
        try:
            changeVimrcName(vimrcPath)
            subprocess.run(['vim', filePath])
            restoreVimrcName(vimrcPath)
            print(f"[*] '{title}'을(를) 수정했습니다.")
        except Exception as e:
            restoreVimrcName(vimrcPath)
            print(f"[!] 파일을 여는 중 오류 발생: {e}")

def deleteFile(title):
    if not title.strip():
        print("[!] 제목을 입력해야 합니다.")
        return
    filePath = os.path.join(textFilePath, f"{title}.txt")
    if os.path.exists(filePath):
        confirmation = input(f"[*] 정말 {title}을 삭제하시겠습니까? (y/n) > ")
        if confirmation.lower() == 'y':
            os.remove(filePath)
            print(f"[*] {title}이 삭제되었습니다.")
        else:
            print("[*] 삭제가 취소되었습니다.")
    else:
        print("[!] 존재하지 않는 글입니다.")

def checkUsb():
    if any(os.path.ismount(os.path.join("/media/alpha", d)) for d in os.listdir("/media/alpha")):
        print("[*] 외부 저장장치가 삽입되어 있습니다.")
    else:
        print("[*] 외부 저장장치가 없습니다.")

def exportFile(title=None):
    usbBasePath = "/media/alpha"
    devices = [d for d in os.listdir(usbBasePath) if os.path.ismount(os.path.join(usbBasePath, d))]
    
    if not devices:
        print("[!] 외부 저장장치가 없습니다.")
        return

    deviceName = devices[0]
    devicePath = os.path.join(usbBasePath, deviceName)
    
    if not os.path.isdir(devicePath):
        print(f"[!] {deviceName}은 유효한 저장장치 경로가 아닙니다.")
        return

    if title:
        filePath = os.path.join(textFilePath, f"{title}.txt")
        if not os.path.exists(filePath):
            print(f"[!] '{title}' 파일이 존재하지 않습니다.")
            return
        shutil.copy(filePath, devicePath)
        print(f"[*] '{title}' 파일을 '{deviceName}' 장치로 내보냈습니다.")
    else:
        for file in os.listdir(textFilePath):
            if file.endswith('.txt'):
                shutil.copy(os.path.join(textFilePath, file), devicePath)
        print(f"[*] 모든 .txt 파일을 '{deviceName}' 장치로 내보냈습니다.")

def importFile(title):
    if not title.strip():
        print("[!] 제목을 입력해야 합니다.")
        return

    usbBasePath = "/media/alpha"
    devices = [d for d in os.listdir(usbBasePath) if os.path.ismount(os.path.join(usbBasePath, d))]
    if not devices:
        print("[!] 외부 저장장치가 없습니다.")
        return

    deviceName = devices[0]
    devicePath = os.path.join(usbBasePath, deviceName)

    if not os.path.isdir(devicePath):
        print(f"[!] {deviceName}은 유효한 저장장치 경로가 아닙니다.")
        return
    
    filePath = os.path.join(devicePath, f"{title}.txt")
    targetPath = os.path.join(textFilePath, f"{title}.txt")
    
    if os.path.exists(targetPath):
        print("[!] 이미 해당 제목의 글이 장치 내에 존재합니다.")
        return
    
    if os.path.exists(filePath):
        shutil.copy(filePath, targetPath)
        print(f"[*] '{title}' 파일을 성공적으로 불러왔습니다.")
    else:
        print(f"[!] '{title}' 파일이 외부 저장장치에 존재하지 않습니다.")

def printHelp():
    print("""[기본 명령어]
help : 도움말을 출력합니다.
list : 글 목록을 불러옵니다.
create <글제목> : <글제목>으로 새로운 글을 작성합니다.
edit <글제목> : <글제목> 글의 내용을 수정합니다.
del <글제목> : <글제목> 글을 삭제합니다.
scan : 외부 저장장치가 삽입되어 있는지 확인합니다.
export [<글제목>] : 모든 .txt 파일 또는 <글제목> 글을 외부 저장장치로 내보냅니다.
import <글제목> : 외부 저장장치에서 <글제목> 글을 불러옵니다.
""")

def parseCommand(command):
    parts = command.split()
    return parts[0], parts[1:] if len(parts) > 1 else []

def main():
    if not os.path.exists(textFilePath):
        os.makedirs(textFilePath)

    printHelp()

    while True:
        command = input("> ").strip()
        cmd, args = parseCommand(command)

        if cmd == "list":
            listFiles()
        elif cmd == "create" and args:
            createFile(args[0])
        elif cmd == "edit" and args:
            editFile(args[0])
        elif cmd == "del" and args:
            deleteFile(args[0])
        elif cmd == "scan":
            checkUsb()
        elif cmd == "export":
            exportFile(args[0] if args else None)
        elif cmd == "import" and args:
            importFile(args[0])
        elif cmd == "help":
            printHelp()
        elif cmd in ["exit", "quit"]:
            print("[*] 프로그램을 종료합니다.")
            break
        else:
            print("[!] 잘못된 명령어입니다.")

if __name__ == "__main__":
    main()