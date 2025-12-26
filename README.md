# Developer_AI
- Developer: Trần Nguyên Hiền And Trí Hoàng
- Email MrHien: trannguyenhien29085@gmail.com
- Email MrHoang: hoangdeptrai181@gmail.com
-----------------------------------------------------

-------------------------------------------------- Installation instructions ----------------------------------------------------
```
git clone https://github.com/NguyenHien-8/Developer_AI.git
```
### 1.Windows
**The command automatically creates directories for all branches**
- On PowerShell
```
git branch -r | % { $n = $_.Trim() -replace 'origin/'; if($n -notmatch 'HEAD'){ git worktree add $n $n } }
```
- On CMD
```
for /f "tokens=1,* delims=/" %a in ('git branch -r ^| findstr /v "HEAD"') do git worktree add "%b" "origin/%b"
```

### 2.Linux
**The command automatically creates directories for all branches.**
- On Bash
```
git branch -r | grep -v 'HEAD' | cut -d/ -f2- | xargs -I{} git worktree add {} origin/{}
```

### 3.MacOS
**The command automatically creates directories for all branches.**
- On Zsh/Bash
```
git branch -r | grep -v 'HEAD' | cut -d/ -f2- | xargs -I{} git worktree add {} origin/{}
```