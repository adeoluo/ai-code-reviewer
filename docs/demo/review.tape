# Records docs/demo/review.gif from a real run: `vhs docs/demo/review.tape` from the repo root.
Output docs/demo/review.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 420
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `python -m ai_code_reviewer review --case 0` Enter
Sleep 2s
Type `python -m ai_code_reviewer review --case 4` Enter
Sleep 2.5s
