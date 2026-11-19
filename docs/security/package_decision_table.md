\# Day 17 – Slopsquatting / Package Verification Drill



\## Objective



Check whether AI-recommended Python package names are legitimate before installing them.



The package names were selected because they are relevant to the Day 17 FastAPI security project.



\*\*Verification source:\*\* Official Python Package Index (PyPI), https://pypi.org/



No packages were installed as part of this exercise.



\## Package Verification Table



| Package | Exists on PyPI? | Author / maintainer information | Earliest release | Decision |

|---|---|---|---|---|

| fastapi | Yes | Sebastián Ramírez / tiangolo | Not confirmed | Accept |

| uvicorn | Yes | Tom Christie / Kludex | Not confirmed | Accept |

| Jinja2 | Yes | Pallets Projects | 17 Jul 2008 | Accept |

| python-multipart | Yes | Andrew Dunham / Kludex | 26 Mar 2013 | Accept |

| itsdangerous | Yes | Pallets Projects | 24 Jun 2011 | Accept |

| python-dotenv | Yes | Saurabh Kumar; maintained by project contributors | 8 Sep 2014 | Accept |

| pytest | Yes | Multiple contributors | Not confirmed | Accept |

| httpx | Yes | Tom Christie | Not confirmed | Accept |

| pwdlib | Yes | pwdlib / fvoron | 13 Feb 2024 | Accept |

| argon2-cffi | Yes | Hynek Schlawack / hynek | 18 Dec 2015 | Accept |



\## Verification Decisions



All ten package names exist on the official PyPI website and are relevant to the project's application, testing, or password-security requirements.



The packages were accepted as candidates based on their relevance and available PyPI information.



A package's existence does not prove that it is safe. Before installing any new package:



1\. Check the exact package name on PyPI.

2\. Verify the project description and intended purpose.

3\. Review author, maintainer, and project ownership information.

4\. Inspect release history and recent maintenance activity.

5\. Check source repository and documentation where available.

6\. Review dependencies and security advisories.

7\. Confirm that the package is genuinely needed.



\## Slopsquatting Warning



Slopsquatting occurs when an attacker publishes a malicious package using a name that an AI tool has invented or recommended incorrectly.



An attacker may exploit a developer who installs a suggested package without checking whether the name is genuine.



\*\*Team rule:\*\* Never install an unchecked AI-recommended package name. Verify the exact package on PyPI first.



\## Verification Limitations



Some original release dates and current ownership details were not confirmed during this exercise. Author and maintainer fields are not necessarily the same as PyPI project owners.



These details should be checked directly on the package's PyPI page before making a production dependency decision.



\*\*Conclusion:\*\* All ten selected package names were verified as existing on PyPI. No package was installed during this drill.
