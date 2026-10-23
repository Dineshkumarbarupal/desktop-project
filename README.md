# WindowPilot — Windows Desktop Window Controller

A local desktop utility built with **HTML/CSS/JavaScript + Python + Eel**. It uses the Windows **Win32 API** through Python's standard-library \`ctypes\` module to inspect and control top-level windows.

## Features
- Enumerate visible, titled top-level windows with HWND handles and bounds.
- Search and select windows.
- Focus, minimize, maximize, and restore a selected window.
- Move and resize a selected window with \`SetWindowPos\`.
- Send a normal \`WM_CLOSE\` request (does not force-kill the process).
- Local UI and API bridge; no cloud service or telemetry.

## Requirements
- Windows 10 or Windows 11
- Python 3.10+
- Eel

## Run
Open PowerShell or Command Prompt in this repository:

~~~powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python main.py
~~~

If PowerShell blocks activation:

~~~powershell
py -m pip install -r requirements.txt
py main.py
~~~

## Project structure
~~~text
desktop-project/
├── main.py
├── requirements.txt
├── README.md
└── web/
    ├── index.html
    ├── style.css
    └── app.js
~~~

## APIs used
- \`EnumWindows\` lists top-level windows.
- \`IsWindowVisible\` and \`GetWindowTextW\` filter visible windows with titles.
- \`ShowWindow\` changes window state.
- \`SetForegroundWindow\` requests focus.
- \`GetWindowRect\` reads bounds.
- \`SetWindowPos\` moves/resizes a selected window.
- \`PostMessageW(WM_CLOSE)\` asks the target app to close normally.

## Safety and limitations
Use this tool only on your own Windows desktop or systems you are authorized to administer. Windows may deny foreground activation or prevent moving certain protected/system windows. A close request can cause the target app to ask about unsaved work. This starter project does not inject code into other processes, bypass access controls, or force-terminate apps. The APIs require Windows; the UI will not operate on macOS or Linux.

## Troubleshooting
- **ModuleNotFoundError: eel** — run \`python -m pip install -r requirements.txt\`.
- **Window list is empty** — ensure visible desktop apps have a title bar and rerun the scan.
- **An action does not work** — Windows or the target application may restrict it.
