\# Day 17 – Leaked Secret Detection and Recovery Drill



\## 1. Objective



Practise detecting a committed secret, simulating credential rotation, and removing the exposed file from Git history.



The exercise was performed in a separate throwaway Git repository so the actual Day 17 application repository was not affected.



A fake demonstration token was used. No real credential was exposed.



\## 2. Drill Environment



\- Repository: `day17-gitleaks-drill`

\- Branch: `day17-gitleaks-drill`

\- Secret detection tool: Gitleaks 8.30.1

\- History cleanup tool: git-filter-repo



\## 3. Exercise Steps and Results



\### Step 1: Prepare a throwaway repository



Created a separate Git repository and committed an initial README file.



\*\*Result:\*\* Initial repository setup completed.



\### Step 2: Create a fake leaked secret



Created a demonstration file containing a fake token and committed it to the throwaway branch.



Some initial dummy token formats were not detected by Gitleaks. A high-entropy demonstration token was subsequently detected.



\*\*Result:\*\* Gitleaks detected one finding in the Git history.



\### Step 3: Simulate credential rotation



Replaced the demonstration token in the current file with a rotated placeholder value and committed the change.



\*\*Result:\*\* Gitleaks still detected the old secret in Git history.



\*\*Learning:\*\* Replacing a secret in the latest version of a file does not remove it from earlier Git commits.



\### Step 4: Rewrite Git history



Used git-filter-repo to remove the demonstration secret file from all commits:



```bash

git filter-repo --path leaked\_secret\_demo.txt --invert-paths --force

```



\*\*Explanation:\*\*

\- `git filter-repo` rewrites repository history.

\- `--path` selects the file to remove.

\- `--invert-paths` keeps everything except the selected file.

\- `--force` allows the operation to proceed in this isolated drill repository.



The tool processed five commits and removed the demonstration file from the rewritten history. The repository was left with the initial README commit.



The origin remote was also removed by git-filter-repo as a safety measure.



\### Step 5: Run Gitleaks again



Executed:



```bash

gitleaks git --redact=100 .

```



\*\*Final result:\*\* One commit scanned; no leaks found.



\## 4. Results Summary



| Stage | Result |

|---|---|

| Initial repository setup | Successful |

| Fake secret committed | Successful |

| Gitleaks detection | One finding detected |

| Simulated rotation | Completed |

| Old history still contained secret | Confirmed |

| History rewritten | Successful |

| Final Gitleaks scan | No leaks found |



\## 5. Important Security Lessons



1\. Never commit real secrets to Git.

2\. If a real credential is exposed, revoke or rotate it immediately.

3\. Removing a secret from the latest file does not remove it from Git history.

4\. History rewriting may be necessary to remove exposed content from repository history.

5\. History rewriting does not invalidate or revoke a leaked credential.

6\. Coordinate history rewriting with the team because commit IDs change.

7\. Check forks, CI logs, build artifacts, and other copies for exposure.



\## 6. Recommended Team Incident Procedure



When a real secret is accidentally committed:



1\. \*\*Rotate first:\*\* Revoke the exposed credential and generate a replacement.

2\. \*\*Assess exposure:\*\* Identify the affected repository, branches, commits, and systems.

3\. \*\*Remove from history if needed:\*\* Use an approved history-rewriting procedure, coordinate any force push, and verify the rewritten repository.

4\. \*\*Notify the team:\*\* Explain the rewrite and ask everyone to re-clone the repository rather than continuing with stale history.

5\. \*\*Verify:\*\* Run Gitleaks again and check other places where the old credential may have been copied.

6\. \*\*Prevent recurrence:\*\* Keep secrets in environment variables or a secrets manager, maintain `.gitignore`, and run secret scanning in CI.



\## 7. Conclusion



The leaked-secret drill successfully demonstrated detection of a committed fake token, simulated rotation, removal of the affected file from Git history, and a clean final Gitleaks scan.



The exercise confirmed that credential rotation and Git history cleanup are separate steps, and that rotation must happen first when a real credential is exposed.
