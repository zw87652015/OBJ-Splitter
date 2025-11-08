#!/usr/bin/env python3
"""
Build script for creating OBJ Model Processor executable
Uses PyInstaller to create a standalone Windows executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean spec file if exists
    spec_file = "OBJ_Model_Processor.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"🧹 Cleaning {spec_file}...")

def create_spec_file():
    """Create PyInstaller spec file with custom configuration"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('PyQt6MD3Guide', 'PyQt6MD3Guide'),
    ],
    hiddenimports=[
        'PyQt6.QtOpenGLWidgets',
        'PyQt6.QtOpenGL',
        'OpenGL',
        'OpenGL.GL',
        'OpenGL.GLU',
        'OpenGL.GLUT',
        'numpy',
        'numpy.core._multiarray_umath',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OBJ Model Processor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''
    
    with open("OBJ_Model_Processor.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    print("✅ Created PyInstaller spec file")

def create_version_info():
    """Create version info file for Windows executable"""
    version_info = '''
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(2,0,0,0),
prodvers=(2,0,0,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'zw87652015'),
    StringStruct(u'FileDescription', u'OBJ Model Processor - 3D Model Analysis Tool'),
    StringStruct(u'FileVersion', u'2.0.0.0'),
    StringStruct(u'InternalName', u'OBJ_Model_Processor'),
    StringStruct(u'LegalCopyright', u'© 2025 zw87652015'),
    StringStruct(u'OriginalFilename', u'OBJ Model Processor.exe'),
    StringStruct(u'ProductName', u'OBJ Model Processor'),
    StringStruct(u'ProductVersion', u'2.0.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    print("✅ Created version info file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Use the spec file for building
        cmd = [sys.executable, "-m", "PyInstaller", "OBJ_Model_Processor.spec", "--clean"]
        
        print(f"🚀 Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            print("\n📦 Build output:")
            print(result.stdout)
            return True
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build failed with exception: {e}")
        return False

def create_installer_script():
    """Create a simple installer script using NSIS (optional)"""
    nsis_script = '''
; NSIS installer script for OBJ Model Processor
; Requires NSIS to be installed to create installer

!define APPNAME "OBJ Model Processor"
!define VERSION "2.0.0"
!define PUBLISHER "zw87652015"
!define DESCRIPTION "3D Model Analysis and Processing Tool"

; Modern UI
!include "MUI2"

; General
Name "${APPNAME}"
OutFile "${APPNAME}_Setup_${VERSION}.exe"
InstallDir "$PROGRAMFILES\\${APPNAME}"
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\\OBJ Model Processor\\*"
    
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\OBJ Model Processor.exe"
    CreateShortCut "$STARTMENU\\Programs\\${APPNAME}.lnk" "$INSTDIR\\OBJ Model Processor.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
    Delete "$INSTDIR\\uninstall.exe"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    Delete "$STARTMENU\\Programs\\${APPNAME}.lnk"
    RMDir /r "$INSTDIR"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
SectionEnd
'''
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)
    print("✅ Created NSIS installer script (optional)")

def main():
    """Main build process"""
    print("🏗️  OBJ Model Processor - EXE Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this script from the project directory.")
        return False
    
    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Create configuration files
    create_spec_file()
    create_version_info()
    create_installer_script()
    
    # Step 4: Build executable
    if not build_executable():
        return False
    
    # Step 5: Show results
    print("\n" + "=" * 50)
    print("🎉 Build completed successfully!")
    print("\n📁 Output location:")
    print(f"   dist/OBJ Model Processor.exe")
    print("\n📋 What was created:")
    print("   ✅ Standalone executable (no Python required)")
    print("   ✅ Includes all dependencies")
    print("   ✅ Material Design 3 guide included")
    print("   ✅ Version info embedded")
    print("   ✅ Windows executable with icon support")
    
    # Check if executable exists
    exe_path = Path("dist/OBJ Model Processor.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n📊 Executable size: {size_mb:.1f} MB")
        print(f"📂 Full path: {exe_path.absolute()}")
    
    print("\n🚀 To run the executable:")
    print("   Double-click: dist/OBJ Model Processor.exe")
    print("   Or run from command line: dist\\'OBJ Model Processor.exe'")
    
    print("\n📦 Optional: Create installer")
    print("   If you have NSIS installed, run: makensis installer.nsi")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Build process completed successfully!")
    else:
        print("\n❌ Build process failed!")
        sys.exit(1)
