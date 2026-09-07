@echo off
chcp 65001 >nul
echo ==========================================
echo    桌面宠物打包工具
echo ==========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 安装依赖
echo [1/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: 安装 PyInstaller
echo [2/4] 安装 PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败
    pause
    exit /b 1
)

:: 打包 EXE
echo [3/4] 开始打包...
pyinstaller --noconfirm --onefile --windowed ^
    --name "DesktopPet" ^
    --add-data "pet_char.png;." ^
    --icon "NONE" ^
    --clean ^
    desktop_pet.py

if errorlevel 1 (
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

:: 复制资源到 dist
echo [4/4] 整理文件...
copy pet_char.png dist\ /Y >nul 2>&1

echo.
echo ==========================================
echo    打包完成！
echo    可执行文件: dist\DesktopPet.exe
echo ==========================================
pause
