# Records docs/demo/http.gif from a real run: `vhs docs/demo/http.tape` from the repo root.
Output docs/demo/http.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 560
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate` Enter
Sleep 2s
Type `python -m ai_code_reviewer serve --port 18301 >/dev/null 2>&1 &` Enter
Sleep 2s
Sleep 8.0s
Type `clear` Enter
Sleep 1s
Show
Type `curl -s localhost:18301/review -d '{"diff": "+def load(path, cache={}):\n+    password = \"hunter2\"\n+    return cache"}' | jq` Enter
Sleep 3.5s
Type `curl -s localhost:18301/metrics | head -n 6` Enter
Sleep 3s
Hide
Type `kill %1` Enter
Sleep 1s
