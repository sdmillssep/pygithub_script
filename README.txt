GetIssues.py
################
(1) Installation:
	-Use pip to install PyGitHub, pandas, and openpyxl
	-create an access token for your GitHub account (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
		-pass in your created token to the Github object's constructor (see line 11 of GetIssues.py)
	-run command: "python GetIssues.py"

(2) repo_names.txt (important file)
	-located in script_data folder
	-tab delimited
	-Place desired repos/queries here (one entry per line)
	-Example (using https://github.com/StephenCleary/AsyncEx/issues):
		-insert the following line to query for all issues after April 4th, 2019:
			"StephenCleary/AsyncEx	is:issue created:>2019-04-14"
	-additional example in script_data/repo_names.txt

(3) Running in terminal:
	-The script reads the queries from repo_names.txt one-at-a-time. The script calls the GitHub API and returns an in-memory copy of the filtered issues.
	 -For each returned issue the following prompts are displayed sequentially:
		-Option to open issue in web browser
		-Enter in assessment description of issue
		-Enter assessment (issue tag) for issue (see section 2.0 of the Splat template doc for more info on this)
		-Option to continue to next issue or save current progress
		
	-Once all the issues of a query have been assessed, the assessment results are saved to a unique-per-repo excel file (script_data/results/excel_result_tables) and a .txt file.
	 The saved table in excel can be copy-pasted to a word document (be sure to use source formatting when pasting to word).

	-After assessing/completing all the issues for a query, you may continue with the next query in repo_names.txt (if any left) or save and exit.
	-Feel free to hack around/modify as needed
			
