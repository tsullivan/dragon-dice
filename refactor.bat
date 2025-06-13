
setlocal

echo Starting transition from PyGame to PySide6 implementation...

REM Define paths (assuming script is run from project root)
set PYGAME_SRC_DIR=src
set PYGAME_ASSETS_DIR=assets
set PYGAME_ROOT_REQS=requirements.txt
set PYSIDE6_SOURCE_DIR=py_side_6

REM Safety check: Ensure py_side_6 directory exists
if not exist "%PYSIDE6_SOURCE_DIR%" (
    echo ERROR: The %PYSIDE6_SOURCE_DIR% directory was not found.
    echo Please ensure it exists in the project root.
    goto :eof
)

echo.
echo Removing PyGame specific files and directories...

REM Remove the PyGame src directory
if exist "%PYGAME_SRC_DIR%" (
    echo Removing %PYGAME_SRC_DIR% directory...
    rmdir /S /Q "%PYGAME_SRC_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to remove %PYGAME_SRC_DIR%.
    ) else (
        echo %PYGAME_SRC_DIR% removed.
    )
) else (
    echo %PYGAME_SRC_DIR% directory not found.
)

REM Remove the assets directory
if exist "%PYGAME_ASSETS_DIR%" (
    echo Removing %PYGAME_ASSETS_DIR% directory...
    rmdir /S /Q "%PYGAME_ASSETS_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to remove %PYGAME_ASSETS_DIR%.
    ) else (
        echo %PYGAME_ASSETS_DIR% removed.
    )
) else (
    echo %PYGAME_ASSETS_DIR% directory not found.
)

REM Remove the root PyGame requirements.txt
if exist "%PYGAME_ROOT_REQS%" (
    echo Removing root %PYGAME_ROOT_REQS%...
    del /Q "%PYGAME_ROOT_REQS%"
    if errorlevel 1 (
        echo ERROR: Failed to remove root %PYGAME_ROOT_REQS%.
    ) else (
        echo Root %PYGAME_ROOT_REQS% removed.
    )
) else (
    echo Root %PYGAME_ROOT_REQS% not found.
)

echo.
echo Moving PySide6 files to project root...

REM Move contents from py_side_6 to the current directory (project root)
REM Using robocopy for robustness. /E copies subdirectories, including empty ones. /MOVE moves files and directories, and deletes them from the source.
robocopy "%PYSIDE6_SOURCE_DIR%" "%CD%" /E /MOVE /NFL /NDL /NJH /NJS /NP
if errorlevel 8 (
    echo WARNING: Robocopy completed with some errors ^(e.g. files in use^).
) else if errorlevel 4 (
    echo WARNING: Robocopy completed with some mismatched files/directories.
) else if errorlevel 2 (
    echo WARNING: Robocopy completed with some extra files/directories.
) else if errorlevel 1 (
    echo PySide6 files moved to root successfully.
) else if errorlevel 0 (
    echo No files needed to be moved from %PYSIDE6_SOURCE_DIR% or an issue occurred ^(Robocopy exit code 0^).
) else (
    echo ERROR: Robocopy failed to move files from %PYSIDE6_SOURCE_DIR%.
)


REM The py_side_6 directory should be empty or non-existent after robocopy /MOVE
REM If it still exists and is empty, rmdir will remove it. If it has content, robocopy /MOVE might have failed.
if exist "%PYSIDE6_SOURCE_DIR%" (
    echo Attempting to remove the (now hopefully empty) %PYSIDE6_SOURCE_DIR% directory...
    rmdir "%PYSIDE6_SOURCE_DIR%"
    if not errorlevel 1 (
        echo %PYSIDE6_SOURCE_DIR% directory removed.
    ) else (
        echo INFO: %PYSIDE6_SOURCE_DIR% could not be removed. It might not be empty or an error occurred.
        echo Please check the directory manually.
    )
)

echo.
echo Transition complete.
echo Please review the console output for details of the move operation.
echo You may need to update your README.md and other project documentation.

endlocal
