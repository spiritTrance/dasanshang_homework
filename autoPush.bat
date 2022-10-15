set /p var=Please enter the commit message to github:
git add .
git commit -m "%var%"
git push
pause