\# Day 17 – Security Triage Report



\## 1. Scope



Security scanning was performed on the Day 17 FastAPI application, its Python dependencies, and the project files.



Tools used:

\- pip-audit – dependency vulnerability scanning

\- Bandit – Python security issue scanning

\- Semgrep Community Edition – static code analysis

\- Gitleaks – secret detection



\## 2. pip-audit – Dependency Vulnerabilities



\*\*Initial result:\*\* The first scan identified a vulnerability in the installed pip version (25.0.1).



\*\*Action taken:\*\* Upgraded pip to version 26.3 and reran the scan.



\*\*Final result:\*\* No known vulnerabilities found.



\*\*Evidence:\*\* `pip\_audit.txt`



\## 3. Bandit – Python Security Scan



\*\*Scope:\*\* `src/`



\*\*Command:\*\* `python -m bandit -r src`



\*\*Result:\*\*

\- 1,141 lines of code scanned

\- 0 high-severity issues

\- 0 medium-severity issues

\- 0 low-severity issues



\*\*Decision:\*\* No Bandit findings required remediation.



\*\*Evidence:\*\* `bandit\_report.txt`



\## 4. Semgrep – Static Analysis



\*\*Tool version:\*\* Semgrep 1.186.0



\*\*Rules:\*\* 151 Python security rules



\*\*Scope:\*\* 19 Python source files.



\*\*Result:\*\*

\- 0 findings

\- 0 blocking findings

\- Approximately 100% of source lines parsed



\*\*Decision:\*\* No Semgrep findings required remediation.



\*\*Evidence:\*\* `semgrep\_report.txt`



\## 5. Gitleaks – Secret Detection



\*\*Tool version:\*\* Gitleaks 8.30.1



\### Source scan



\- Scanned application source files in `src/`.

\- Result: No leaks found.



\### Test scan



\- Scanned files in `tests/`.

\- Result: No leaks found.



\### Full project scan



The broad scan reported 209 matches for the `generic-api-key` rule.



Review showed that the matches were located in:

\- Third-party package data and code inside `.venv/`.

\- The project's `.env` file, which contains the application session secret.



The `.env` file is excluded from Git through `.gitignore`. Its secret value was not included in this report.



\*\*Decision:\*\*

\- No secret findings were detected in application source or test files.

\- Keep `.env` private and excluded from Git.

\- Exclude virtual environments from routine repository secret scans where appropriate.

\- Review future findings instead of blindly suppressing them.



\*\*Evidence:\*\*

\- `gitleaks\_src\_only.json`

\- `gitleaks\_tests\_report.json`

\- `gitleaks\_files\_report.json`



\## 6. Overall Triage Decisions



| Tool | Final result | Decision |

|---|---|---|

| pip-audit | No known vulnerabilities | Clean after pip upgrade |

| Bandit | 0 findings | No remediation required |

| Semgrep | 0 findings | No remediation required |

| Gitleaks source scan | No leaks | Clean |

| Gitleaks test scan | No leaks | Clean |

| Gitleaks full scan | 209 matches | Reviewed; package-data matches and private `.env` require appropriate handling |



\## 7. Limitations and Follow-up



\- Static analysis tools cannot guarantee that an application is completely secure.

\- Dependency vulnerabilities can appear when new versions or advisories are published.

\- Secret scans can produce false positives and require human review.

\- Repeat these scans regularly and include them in the CI pipeline.



\*\*Conclusion:\*\* The application source and test files passed the recorded security scans. The initial pip vulnerability was addressed, and the broad Gitleaks matches were reviewed.
