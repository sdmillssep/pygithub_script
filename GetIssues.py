# Script for pulling issues from public repo
# Use pip to install PyGitHub, Pandas, openpyxl
from github import Github
import os
import webbrowser
import pandas
import pdb

def main():

    g = Github(login_or_token='YOUR_AUTH_TOKEN_HERE') # Will need to use own access token. See https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
    checkFolders()
    repoNames = getAllRepoNames()

    # Iternate each repo in 'repo_names.txt'
    for i in range(3, len(repoNames)):
        line = repoNames[i]
        # check for ignored lines
        if line[:3] == '%%%':
            continue
            
        lineData = processLine(line.rstrip()) 
        
        # Query for issues
        issues = g.search_issues('repo:{0} {1}'.format(lineData['repo_name'], lineData['query']), sort = 'created', order = 'asc')
                        
        # Iternate issues + give Assessment Summary
        startSession(lineData['repo_name'], issues)
        
        # Only called if a query session has finished
        # Rewrite repo_names.txt to reflect current progress
        rewrittenLine = '%%%' + line
        repoNames[i] = rewrittenLine
        updateRepoNames(repoNames)
        
        # Next/exit logic
        nextQuery = input('Finished issues returned from \'{0}\'...\nMove to next query? (y = yes, any other key = no)\n'.format(lineData['query']))
        exportToExcel(lineData['repo_name'])
        
        if nextQuery.lower() != 'y':
            exit()
            
    print('Completed assessment of all entries in repo_names.txt...')


def getAllRepoNames():
    with open('.\\script_data\\repo_names.txt', 'r', encoding = 'utf-8') as repoNamesFile:
        return repoNamesFile.readlines()


def processLine(line):
    # Create dictionary of line data
    keys = ['repo_name', 'query']
    lineDataList = line.split('\t')
    lineDataList[1] = lineDataList[1].lower()
    
    return dict(zip(keys, lineDataList))
            

def listIssueData(curRepo, issue, issuesRemaining):
    os.system('cls')
    print('Currently viewing: {0}\tIssues remaining: {1}'.format(curRepo, issuesRemaining))
    print('{4}\nIssue #{0}: {1}\nBODY:\n{2}\nEND BODY\nCreated at: {3}\n{4}\n'.format(issue.number, issue.title, issue.body, issue.created_at, '##############' * 3))
    
    
def startSession(repoName, issues):
    if issues.totalCount == 0:
        print ('Query returned 0 issues...')
             
    else:
        # Start a 'review session' of remaining filtered issues
        # Read last line of results.txt file + find that issue # in issues list + start at index immediately after that issue (if not out-of-bounds)
        lastViewedIssue = getLastViewedIssue(repoName, issues)

        for i in range(int(lastViewedIssue) + 1, issues.totalCount):
            remainingIssues = issues.totalCount - i
            listIssueData(repoName, issues[i], remainingIssues)
            
            # Open issue in browser?
            openUrl = input('Open issue #{} in web browser? (y = yes, any other key = no)\n'.format(issues[i].number))
            if openUrl.lower() == 'y':
                webbrowser.open_new_tab(issues[i].html_url)
            
            # Enter Assessment Summary
            assessment = input('Enter Assessment Summary for issue #{}:\n'.format(issues[i].number))
            assessment = assessment.replace('\t', ' ')
            
            tag = enterIssueTag()
            # Save assessed issue to results file + remove from issues list
            writeAssessmentToFile(repoName, issues[i].number, issues[i].title, assessment, tag)
                
            # Continue/save
            if i == issues.totalCount - 1:
                break
            else:
                continueAssessment = input('Continue to next issue? (n = save & quit, any other key = continue)\n')
                if continueAssessment.lower() == 'n':
                    print ('Progress saved...')
                    exit()
                                
        
def writeAssessmentToFile(repoName, issueNum, issueTitle, assessment, tag):
    repoName = repoName.replace('/', '-')
    fileName = 'assessment_results_{0}.txt'.format(repoName)
    with open('.\\script_data\\results\\{}'.format(fileName), 'a', encoding = 'utf-8') as assessmentFile:
        # Write issue #, title, assessment summary
        assessmentFile.write('{0}\t{1}\t{2}\t{3}\n'.format(issueNum, issueTitle, assessment, tag))   
    
        
def updateRepoNames(newLines):
    with open('.\\script_data\\repo_names.txt', 'w', encoding = 'utf-8') as repoNamesFile:
        repoNamesFile.writelines(newLines)
        
        
def enterIssueTag():
    tags = {'1': '[N/A]', '2': '[Minor]', '3': '[Moderate]', '4': '[Major]'}
    issueTag = input('Enter number corresponding to issue tag:\n(1) [N/A]\n(2) [Minor]\n(3) [Moderate]\n(4) [Major]\n')
    while not issueTag in ['1', '2', '3', '4']:
        issueTag = input('Enter number corresponding to issue tag:\n(1) [N/A]\n(2) [Minor]\n(3) [Moderate]\n(4) [Major]\n')
    
    return tags[issueTag]
    
def exportToExcel(repoName):
    repoName = repoName.replace('/', '-')
    filePath = '.\\script_data\\results\\assessment_results_{}.txt'.format(repoName)
    dataFrame = pandas.read_csv(filePath, sep = '\t', header = None, names = ['Issue #', 'Issue Description', 'Assessment Description', 'Assessment'])
    dataFrame.to_excel('.\\script_data\\results\\excel_result_tables\\{0}_results.xlsx'.format(repoName), 'Assessment Results', index = False)
    print('Saved {0} assessment results to Excel'.format(repoName))
    
def checkFolders():
    # ensure results & excel_result_tables exist (create otherwise)
    resultsPath = '.\\script_data\\results'
    resultsExists = os.path.exists(resultsPath)
    if not resultsExists:
        os.makedirs(resultsPath)
        
    excelPath = '.\\script_data\\results\\excel_result_tables'
    excelExists = os.path.exists(excelPath)
    if not excelExists:
        os.makedirs(excelPath)


def getLastViewedIssue(repoName, issues):
    repoName = repoName.replace('/', '-')
    resultsFilePath = '.\\script_data\\results\\assessment_results_{}.txt'.format(repoName)
    
    if os.path.exists(resultsFilePath):
        # This isn't the most efficient way to get the last line, but it doesn't store the whole file in memory (e.g. f.readlines() method) just to get a single line (with small enough files this won't really matter regardless)
        with open(resultsFilePath) as f:
            for line in f:
                pass
            lastLineIssueNum = line.split('\t')[0]

            # Get index of matching issue number in issues list
            for i in range(issues.totalCount):
                if issues[i].number == int(lastLineIssueNum):
                    return i
    else:
        return -1
        
# WIP -- [TODO] tag       
# def writeIssueToTodoFile(issue):
    # with open('.\\script_data\\todo.txt', 'a', encoding = 'utf-8') as todoFile:
        # # Write issue #, title, assessment summary
        # todoFile.write('{0}\t{1}\t{2}\n'.format(issue.number, issue.title, issue.html_url))

# def readTodoFile():
    # todoList = []
    # with open('.\\script_data\\todo.txt', 'r', encoding = 'utf-8') as todoFile:
        # for line in todoFile:
            # todoList.append(line.rstrip().split('\t'))

            
        # return todoList
        
# def assessTodoIssues(repoName):
    # todoList = readTodoFile() #todoList[x] = [[number, title, html_url], [number, title, html_url],...]
    # #lastViewedTodo = loadSavedTodoProgress()
    
    # while len(todoList) > 0:
        # for issue in todoList:
            # # List todo issue data
            # os.system('cls')
            # print('TODO Issues\nIssue #{0}\t{1}\n{2}\n'.format(issue[0], issue[1], '##############' * 3))
            
            # # Assess (TODO: this works, but needs to be cleaned up a lot)
            # # Open issue in browser?
            # openUrl = input('Open issue #{} in web browser? (y = yes, any other key = no)\n'.format(issue[0]))
            # if openUrl.lower() == 'y':
                # webbrowser.open_new_tab(issue[2])
            
            # # Enter Assessment Summary
            # assessment = input('Enter Assessment Summary for issue #{}:\n'.format(issue[0]))
            # assessment = assessment.replace('\t', ' ')
            
            # # Enter Issue tag
            # tag = enterIssueTag()
            # if tag == '[TODO]':
                # todoList.insert(0, issue)
            # else:
                # # Save assessed issue to results file
                # writeAssessmentToFile(repoName, issue[0], issue[1], assessment, tag)
                
            # todoList.remove(issue)
            
            # # Continue/save
            # if len(todoList) == 0:
                # break 
            # else:
                # continueAssessment = input('Continue to next issue? (n = save & quit, any other key = continue)\n')
                # if continueAssessment.lower() == 'n':
                    # saveCurrentTodoProgress(todoList)
                    # exit()
            
    
# def loadSavedTodoProgress():
    # try:
        # with open('.\\script_data\\saved_todo_progress.txt', 'r', encoding = 'utf-8') as saveFile:
            # lastViewedTodo = saveFile.readline()
            # lastViewedTodo = lastViewedTodo.rstrip()
            # if lastViewedTodo == "":
                # return -1
            # else:
                # return int(lastViewedTodo)

    # except FileNotFoundError:
        # return -1 # file doesn't exist

# def saveCurrentTodoProgress(todoItems):
    # print('Saving progress...')
    # with open('.\\script_data\\todo.txt', 'w', encoding = 'utf-8') as saveFile:
        # for item in todoItems:
            # saveFile.write('{0}\t{1}\t{2}\n'.format(item[0], item[1], item[2]))
     
    


if __name__ == '__main__':
    main()
    


# TODOS:
# Move assessment logic to own function
# Prevent crash when enter wrong item in tag selection (this is an issue with assuming they enter an int) (DONE)
# Rather than saved_progress, make app resume at index immediately after latest result.txt line (DONE)
# Add issue-already-viewed skipping logic (add <TODO> tag which saves all TODO items to a separate file?)
# Add create directory if not exist logic (DONE)

