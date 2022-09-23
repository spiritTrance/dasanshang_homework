setlocal enableextensions disabledelayedexpansion
for %%I in (mktexpk.exe) do set "mktexpk=%%~$PATH:I"
if not defined mktexpk exit 1
for /f "usebackq skip=17 tokens=1,2,3* delims=|" %%I in (%0) do (
  set dpi=%%I
  set bdpi=%%J
  set mag=%%K
  set font=%%L
  goto :sanitize
)
:sanitize
if defined dpi  set "dpi=%dpi:"=%"
if defined bdpi set "bdpi=%bdpi:"=%"
if defined mag  set "mag=%mag:"=%"
if defined font set "font=%font:"=%"
"%mktexpk%" --mfmode / --dpi "%dpi%" --bdpi "%bdpi%" --mag "%mag%" "%font%"
del %0 & exit %errorlevel%
632|600|1+32/600|unisong5e
