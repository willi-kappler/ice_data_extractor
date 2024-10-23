$pythonProgramPath = cmd /c "where python" '2>&1'
$pythonScriptPath = "src\main.py"
$pythonOutput = & $pythonProgramPath $pythonScriptPath
$pythonOutput

