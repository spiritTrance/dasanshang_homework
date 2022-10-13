set /p var=Please Enter the commit message:
git add .
git commit -m "%var%"
git push