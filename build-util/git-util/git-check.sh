#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # This comment is required.
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL.

#-----------------------------------------------------------------NoticeStart-
# Git Utilities
# Copyright 2017-2022 Open Water Foundation.
#
# License GPLv3+:  GNU GPL version 3 or later
#
# There is ABSOLUTELY NO WARRANTY; for details see the
# "Disclaimer of Warranty" section of the GPLv3 license in the LICENSE file.
# This is free software: you are free to change and redistribute it
# under the conditions of the GPLv3 license in the LICENSE file.
#-----------------------------------------------------------------NoticeEnd---
#
# git-check.sh
#
# Check the status of multiple repositories for this project and indicate whether pull
# or push or other action is needed:
# - see the main entry point at the bottom of the script for script configuration
# - currently must adhere to prescribed folder structure
# - useful when multiple repositories form a product
# - this script does not do anything to change repositories
# - warn if any repositories use Cygwin because mixing with Git for Windows can cause confusion in tools

# List functions in alphabetical order.

# Determine the operating system that is running the script:
# - mainly care whether Cygwin
checkOperatingSystem() {
  if [ ! -z "${operatingSystem}" ]; then
    # Have already checked operating system so return.
    return
  fi
  operatingSystem="unknown"
  os=$(uname | tr [a-z] [A-Z])
  case "${os}" in
    CYGWIN*)
      operatingSystem="cygwin"
      ;;
    LINUX*)
      operatingSystem="linux"
      ;;
    MINGW*)
      operatingSystem="mingw"
      ;;
  esac
  echo "operatingSystem=${operatingSystem} (used to check for Cygwin and filemode compatibility)."
}

# Function to confirm that proper command-line Git client is being used:
# - mainly to confirm that Cygwin is not used when filemode=false
# - in order to see local config associated with a repo must cd into the repo folder
checkCommandLineGitCompatibility() {
  # Make sure that the operating system has been determined:
  # - will set operatingSystem to "cygwin" if cygwin
  checkOperatingSystem
  filemodeLine=$(git config --list | grep filemode)
  #echo "${filemodeLine}"
  if [ ! -z "${filemodeLine}" ]; then
    # filemode is usually printed by Git bash but may not be printed by Cygwin:
    # - if repo was cloned using Git Bash:  core.filemode=false
    filemode=$(echo ${filemodeLine} | cut --delimiter='=' --fields=2)
    #echo "repository filemode=${filemode}"
    if [ "${filemode}" = "true" ] && [ "${operatingSystem}" = "cygwin" ]; then
      # Count Cygwin repos so message can be printed at the end.
      cygwinRepoCount=$(expr ${cygwinRepoCount} + 1)
      #echo "cygwinRepoCount=${cygwinRepoCount}"
    fi
    # The following messages are hints but may not be accurate so don't color or label as warnings.
    if [ "${operatingSystem}" = "linux" ]; then
      # No need for any special logic because no Git Bash or Cygwin.
      if [ "${repoCount}" -eq 0 ]; then
        echo "  Detected Linux operating system."
      fi
    elif [ "${operatingSystem}" = "cygwin" ] && [ "${filemode}" = "false" ]; then
      # Probably cloned using Git Bash or other Windows-centric Git client.
      ${echo2} "  DO NOT USE CygWin command line git with this repo (was likely NOT cloned with Cygwin, filemode=false)."
    elif [ "${operatingSystem}" = "cygwin" ] && [ "${filemode}" = "true" ]; then
      # Probably cloned using Cygwin so consistent with this environment.
      # A global warning is printed at the end if mixing filemodes.
      ${echo2} "  USE Cygwin or other filemode=true Git client with this repo (filemode=true)."
    elif [ "${operatingSystem}" = "mingw" ] && [ "${filemode}" = "true" ]; then
      # Probably cloned using Cygwin but for consistency recommend Windows-centric Git client.
      ${echo2} "  USE CygWin command line git with this repo (was likely cloned with Cygwin, filemode=true)."
    elif [ "${operatingSystem}" = "mingw" ] && [ "${filemode}" = "false" ]; then
      # Probably cloned using Git Bash or other Windows-centric Git client so OK.
      echo "  USE Git Bash or other Windows Git client with this repo (filemode=false)."
    else
      ${echo2} "  ${actionErrorColor}[ERROR] Unhandled operating system ${operatingSystem} - no git client recommendations provided.${colorEnd}"
    fi
  fi
}

# Check whether any working files are different from commits in the repo:
# - have to include function before it is called
# - print a message if so
# - assumes that the current folder is a Git repository of interest
# - see:  https://stackoverflow.com/questions/3882838/whats-an-easy-way-to-detect-modified-files-in-a-git-workspace
checkWorkingFiles() {
  local emptyFolderCount exitCode untrackedFilesCount
  # The following won't work if run in Cygwin shell for non-Cygwin repo clone, or the other way:
  # --quiet causes --exit-code, which exits 0 if same, 1 if differences exist.
  git diff-index --quiet HEAD
  gitDiffExitCode=$?
  # Therefore, use the following (although this could ignore newline cleanup that needs to be committed):
  # - however, even though --quiet is specified, the following outputs a bunch of messages like:
  #   warning:  CRLF will be replaced by LF in ...
  #   The file will have its original line endings in your working directory.
  #git diff-index --ignore-cr-at-eol --quiet HEAD
  #echo "exitCode=$exitCode"
  if [ ${gitDiffExitCode} -eq 1 ]; then
    # The following is checked below to indicate whether local files need to be committed.
    ${echo2} "  ${actionColor}Working files contain modified files that need to be committed, or staged files.${colorEnd}"
  fi
  # The above won't detect untracked files but the following will find those:
  # - the following will return a value of 0 or greater
  # -o shows other (i.e., untracked) files in the output
  # --directory shows entire untracked directories as directory name followed by slash
  # --exclude-standard excludes standard files such as indicated by .gitignore
  # --no-empty-directory excludes empty directories,
  # which won't be committed anyhow because Git does not save empty directories
  untrackedFilesCount=$(git ls-files -o --directory --no-empty-directory --exclude-standard | wc -l)
  untrackedFilesAndEmptyFoldersCount=$(git ls-files -o --directory --exclude-standard | wc -l)
  if [ ${untrackedFilesCount} -ne 0 ]; then
    ${echo2} "  ${actionColor}Working files contain ${untrackedFilesCount} untracked files that need to be committed.${colorEnd}"
  fi
  # List empty folders that are not .git-ignored because may be an oversight:
  # - gitDiffExitCode will be nonzero
  # - to make sure it is not confusing, list the directories here
  # - will only be confusing if the untracked files are zero (since they ignore empty folders)
  untrackedEmptyFoldersCount=$(expr ${untrackedFilesAndEmptyFoldersCount} - ${untrackedFilesCount})
  #echo "untrackedEmptyFoldersCount=${untrackedEmptyFoldersCount}"
  if [ ${untrackedEmptyFoldersCount} -ne 0 ]; then
    # List modified files into a temporary file:
    # - include empty folders (will only list if not .gitignored)
    # - modified folders will also be listed
    now=$(date +%Y%m%d%H%M%S.%N)
    modifiedFilesTmpFile=/tmp/git-check-${now}-modified-files
    emptyFoldersTmpFile=/tmp/git-check-${now}-empty-folders
    # The following does not have the leading ./ like 'find' command output below:
    # - set 'line2' below to remove leading ./ and add / for grep call
    git ls-files -o --directory --exclude-standard > ${modifiedFilesTmpFile}
    touch ${emptyFoldersTmpFile}
    # Only list files that are not git ignored.
    # Example line from find:
    #   ./doxygen-project/doxygen-novastar-5.3.0.0.dev2/html/d1/d32
    find . -type d -empty | grep -v '.git' | while read -r line; do
      # See if the file matches a file in the temporary file:
      # - remove the leading ./ before finding
      # - add the trailing / before finding
      # - use line start and end to make sure the whole line is matched and not substring
      line2=$(echo ${line} | cut -c 3-)
      line2="${line2}/"
      #echo "Trying to match: '${line2}'"
      matchCount=$(grep --fixed-strings --line-regexp "${line2}" ${modifiedFilesTmpFile} | wc -l)
      if [ ${matchCount} -ge 1 ]; then
        # Empty folder found that is not git ignored.
        ${echo2} "  ${line2}" > ${emptyFoldersTmpFile}
      fi
      done
    # Track repositories with empty folders, often indicate an issue.
    emptyFoldersRepoCount=$(expr ${emptyFoldersRepoCount} + 1)
    # If any empty untracked folders were detected, print the following.
    if [ -s "${emptyFoldersTmpFile}" ]; then
      matchCountTotal=$(cat ${emptyFoldersTmpFile} | wc -l)
      ${echo2} "  ${actionColor}${matchCountTotal} empty folder(s) should be removed, added to .gitignore, add README to folder, etc.:"
      cat ${emptyFoldersTmpFile}
      ${echo2} "${colorEnd}"
    fi
    # Remove the temporary file.
    rm ${modifiedFilesTmpFile}
    rm ${emptyFoldersTmpFile}
  fi
  # Global script data.
  if [ ${gitDiffExitCode} -eq 1 -o ${untrackedFilesCount} -ne 0 ]; then
    # The local repository has uncommitted working files.
    localChangesRepoCount=$(expr ${localChangesRepoCount} + 1)
  fi
}

# Function to check the status of local compared to remote repository:
# - see:  https://stackoverflow.com/questions/3258243/check-if-pull-needed-in-git
# - Code from above was used as is with some additional lines for checks out output messages
checkRepoStatus() {
  # Current branch.
  currentRepo=$(git branch | grep \* | cut -d ' ' -f2)
  # Repo that is the master, to which all work flows - used to check whether on a branch.
  mainRepo=$(getMainRepo)
  if [ "${debug}" = "true" ]; then
    echo "  [DEBUG] main branch is: ${mainRepo}"
  fi

  if [ ! "${currentRepo}" = "${mainRepo}" ]; then
    ${echo2} "  ${actionColor}Checked out branch:  ${currentRepo}${colorEnd}"
    ${echo2} "  ${actionColor}May need to pull remote before merging this branch.  Rerun check on master before merging this branch.${colorEnd}"
  else
    echo "  Checked out branch:  ${mainRepo}"
  fi

  # Get the remote information.
  git remote update
  # Start code from above StackOverflow article.
  errorCount=0
  UPSTREAM=${1:-'@{u}'}
  LOCAL=$(git rev-parse @)
  if [ $? -ne 0 ]; then
    errorCount=$(expr ${errorCount} + 1)
  fi
  REMOTE=$(git rev-parse "${UPSTREAM}")
  if [ $? -ne 0 ]; then
    errorCount=$(expr ${errorCount} + 1)
  fi
  BASE=$(git merge-base @ "${UPSTREAM}")
  if [ $? -ne 0 ]; then
    errorCount=$(expr ${errorCount} + 1)
  fi

  # There may be errors in the Git commands if working in a branch but there is no remote.
  # For example, this might be a local feature/topic branch that is checked out from master.
  if [ ${errorCount} -ne 0 ]; then
    ${echo2} "  ${actionColor}[WARNING] Error checking upstream repository.${colorEnd}"
    ${echo2} "  ${actionColor}[WARNING] May be a local branch that has not been pushed to remote.${colorEnd}"
    ${echo2} "  ${actionColor}[WARNING] Remote repository name may have changed.${colorEnd}"
  fi

  if [ "${debug}" = "true" ]; then
    echo "  [DEBUG] LOCAL  = ${LOCAL}"
    echo "  [DEBUG] REMOTE = ${REMOTE}"
    echo "  [DEBUG] BASE   = ${BASE}"
  fi

  lineDash="--------------------------------------------------------------------------------"
  repoCount=$(expr ${repoCount} + 1)
  if [ "${LOCAL}" = "${REMOTE}" ]; then
    echo "  ${lineDash}"
    ${echo2} "  ${okColor}Up-to-date (no remote files need pulled/merged)${colorEnd}"
    checkWorkingFiles
    upToDateRepoCount=$(expr ${upToDateRepoCount} + 1)
    echo "  ${lineDash}"
  elif [ "${LOCAL}" = "${BASE}" ]; then
    echo "  ${lineDash}"
    ${echo2} "  ${actionColor}Need to pull${colorEnd}"
    checkWorkingFiles
    needToPullRepoCount=$(expr ${needToPullRepoCount} + 1)
    echo "  ${lineDash}"
  elif [ "${REMOTE}" = "${BASE}" ]; then
    echo "  ${lineDash}"
    ${echo2} "  ${actionColor}Need to push${colorEnd}"
    checkWorkingFiles
    needToPushRepoCount=$(expr ${needToPushRepoCount} + 1)
    echo "  ${lineDash}"
  else
    echo "  ${lineDash}"
    ${echo2} "  ${actionColor}Diverged${colorEnd}"
    checkWorkingFiles
    divergedRepoCount=$(expr ${divergedRepoCount} + 1)
    echo "  ${lineDash}"
  fi
  # End code from above StackOverflow article.
}

# Determine which echo to use, needs to support -e to output colored text:
# - normally built-in shell echo is OK, but on Debian Linux dash is used, and it does not support -e
configEcho() {
  echo2='echo -e'
  testEcho=$(echo -e test)
  if [ "${testEcho}" = '-e test' ]; then
    # The -e option did not work as intended:
    # - using the normal /bin/echo should work
    # - printf is also an option
    echo2='/bin/echo -e'
    # The following does not seem to work.
    #echo2='printf'
  fi

  # Strings to change colors on output, to make it easier to indicate when actions are needed:
  # - Bash colors and formatting:  https://misc.flogisoft.com/bash/tip_colors_and_formatting
  # - Colors in Git Bash:  https://stackoverflow.com/questions/21243172/how-to-change-rgb-colors-in-git-bash-for-windows
  # - Useful info:  http://webhome.csc.uvic.ca/~sae/seng265/fall04/tips/s265s047-tips/bash-using-colors.html
  # - See colors:  https://en.wikipedia.org/wiki/ANSI_escape_code#Unix-like_systems
  # - Set the background to black to ensure that white background window will clearly show colors contrasting on black.
  # - Yellow "33" in Linux can show as brown, see:  https://unix.stackexchange.com/questions/192660/yellow-appears-as-brown-in-konsole
  # - Tried to use RGB but could not get it to work - for now live with "yellow" as it is
  # - TODO smalers 2022-11-11 why is background hazy? Tried some different combinations to fix but no solutions in debian.
  # Warning.
  actionColor='\e[0;40;33m' # User needs to do something, 40=background black, 33=yellow.
  #actionColor='\e[48;5;0m\e[33m' # User needs to do something, 40=background black, 33=yellow.
  # Error.
  actionErrorColor='\e[0;40;31m' # Serious issue, 40=background black, 31=red.
  #actionErrorColor='\e[48;5;0m\e[31m' # Serious issue, 40=background black, 31=red.
  # OK.
  okColor='\e[0;40;32m' # Status is good, 40=background black, 32=green.
  # Reset.
  colorEnd='\e[0m' # To switch back to default color.
}

# Determine the main repo for the repository:
# - currently only handles 'main' and 'master'
# - may have * or other decorators
# - the branch is echoed to standard output and can be assigned to a variable
# - therefore don't echo anything else in the function
getMainRepo() {
  local mainCount masterCount

  masterCount=$(git branch | grep -E '* master$' | wc -l)
  mainCount=$(git branch | grep -E '* main$' | wc -l)
  if [ ${mainCount} -eq 1 ]; then
    # Have one occurrence of 'main' branch so assume it should be used.
    echo "main"
  else
    # Assume old default.  If wrong errors will be generated.
    echo "master"
  fi
}

# Parse the command parameters.
parseCommandLine() {
  local OPTIND opt d g h m p v
  optstring="dg:hm:p:v"
  while getopts ${optstring} opt; do
    #echo "[DEBUG] Command line option is: ${opt}"
    case ${opt} in
      d) # -d  Turn on debug.
        debug="true"
        ;;
      g) # -g  Specify folder containing Git repositories.
        gitReposFolder=${OPTARG}
        ;;
      h) # -h  Print the program usage.
        printUsage
        exit 0
        ;;
      m) # -m mainRepoName  Specify the main repository name, assumed that repository name will match folder for repository.
        mainRepo=${OPTARG}
        ;;
      p) # -p productHome   Specify the product home, relative to ${HOME}, being phased out.
        echo ""
        echo "[ERROR] -p is obsolete.  Use -g instead."
        exit 1
        ;;
      v) # -v  Print the program version.
        printVersion
        exit 0
        ;;
      \?)
        echo ""
        echo "[ERROR] Invalid option:  -${OPTARG}" >&2
        printUsage
        exit 1
        ;;
      :)
        echo ""
        echo "[ERROR] Option -${OPTARG} requires an argument" >&2
        printUsage
        exit 1
        ;;
    esac
  done
}

# Print the script usage:
# - calling code must exist with appropriate code
printUsage() {
  echo ""
  echo "Usage:  ${scriptName} -m product-main-repo -g gitReposFolder"
  echo ""
  echo "Check the status of all repositories that comprise a product."
  echo ""
  echo "Example:"
  echo "  ${scriptName} -m owf-util-git -g \$HOME/owf-dev/Util-Git/git-repos"
  echo ""
  echo "-d  Print additional debug messages."
  echo "-g  Specify the folder containing 1+ Git repositories for the product."
  echo "-h  Print the usage"
  echo "-m  Specify the main repository name."
  echo "-v  Print the version"
  echo ""
}

# Print the script version and copyright/license notices:
# - calling code must exist with appropriate code
printVersion() {
  echo ""
  echo "${scriptName} version ${version}"
  echo ""
  echo "Git Utilities"
  echo "Copyright 2017-2022 Open Water Foundation."
  echo ""
  echo "License GPLv3+:  GNU GPL version 3 or later"
  echo ""
  echo "There is ABSOLUTELY NO WARRANTY; for details see the"
  echo "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file."
  echo "This is free software: you are free to change and redistribute it"
  echo "under the conditions of the GPLv3 license in the LICENSE file."
  echo ""
}

# Entry point into main script:
# - call functions from above as needed

# Script location and name:
# - absolute location is typically only needed in development environment
# - name is used in some output, use the actual script in case file was renamed
scriptFolder=$(cd $(dirname "$0") && pwd)
scriptName=$(basename $0)

version="1.9.1 2022-11-15"

# Set initial values.
debug="false"

# Configure the echo command to print colors.
configEcho

# Parse the command line.
parseCommandLine "$@"

# Output some blank lines to make it easier to scroll back in window to see the start of output.

echo ""
echo ""

# Check the operating system.
checkOperatingSystem

if [ -z "${gitReposFolder}" ]; then
  echo ""
  echo "[ERROR] The Git repositories folder is not specified with -g.  Exiting."
  printUsage
  exit 1
fi

# Git repsitories folder is relative to the user's files in a standard development location, for example:
# $HOME/                     User's files.
#    DevFiles/               Development files grouped by a system, product line, etc.
#      ProductHome/          Development files for a specific product.
#        git-repos/          Git repositories that comprise the product.
#          repo-name1/       Git repository folders (each containing .git, etc.)
#          repo-name2/
#          ...
#
# Main repository in a group of repositories for a product:
# - this is where the product repository list file will live
mainRepoAbs="${gitReposFolder}/${mainRepo}"
# The following is a list of repositories including the main repository:
# - one repo per line, no URL, just the repo name
# - repositories must have previously been cloned to local files
repoListFile="${mainRepoAbs}/build-util/product-repo-list.txt"

# Check for local folder existence and exit if not as expected:
# - ensures that other logic will work as expected in folder structure

if [ ! -d "${mainRepoAbs}" ]; then
  echo ""
  echo "[ERROR] Main repo folder does not exist:  ${mainRepoAbs}"
  echo "[ERROR] Exiting."
  echo ""
  exit 1
fi
if [ ! -f "${repoListFile}" ]; then
  echo ""
  echo "[ERROR] Product repo list file does not exist:  ${repoListFile}"
  echo "[ERROR] Exiting."
  echo ""
  exit 1
fi

# Count the number of Cygwin repositories so can remind developer at the end.
cygwinRepoCount=0
repoCount=0
upToDateRepoCount=0
needToPullRepoCount=0
needToPushRepoCount=0
divergedRepoCount=0
localChangesRepoCount=0
emptyFoldersRepoCount=0

# Change folders to each repository and run the function to check that repository status
# against its upstream repository:
# - use syntax that does not use pipe so that internal variables are in same scope as main script
#   and can be processed after the loop
# - ignore comment lines starting with #
while IFS= read -r repoName
do
  # Make sure there are no carriage returns in the string:
  # - can happen because file may have Windows-like endings but Git Bash is Linux-like
  # - use sed because it is more likely to be installed than dos2unix
  repoName=$(echo ${repoName} | sed 's/\r$//')
  if [ -z "${repoName}" ]; then
    # Blank line.
    continue
  fi
  firstChar=$(expr substr "${repoName}" 1 1)
  if [ "${firstChar}" = "#" ]; then
    # Comment line.
    continue
  fi
  # Check the status on the specific repository:
  # - initial output is not indented
  # - everything under the initial lines are indented
  productRepoFolder="${gitReposFolder}/${repoName}"
  lineDoubleDash="=================================================================================="
  echo "${lineDoubleDash}"
  echo "Checking status of repo:  ${repoName}"
  echo "${lineDoubleDash}"
  if [ ! -d "${productRepoFolder}" ]; then
    echo ""
    ${echo2} "  ${actionColor}[WARNING] Product repo folder does not exist:  ${productRepoFolder}${colorEnd}"
    ${echo2} "  ${actionColor}[WARNING] Skipping.${colorEnd}"
    continue
  else
    # Change to repo folder (otherwise Git commands don't know what to do).
    cd ${productRepoFolder}
    checkRepoStatus
    # Check to make sure that proper Git command line tool is being used:
    # - filemode=false indicates that Cygwin should not be used
    checkCommandLineGitCompatibility
  fi
#done
done < ${repoListFile}

echo ""
echo "${lineDoubleDash}"
echo "Summary of all repositories - see above for details."
echo "Run with -d to print additional debug information."
echo "Sometimes changes are indicated due to CRLF issues (cd to the repo folder once may fix)."
# Print a message to encourage not using Cygwin to clone repositories.
if [ "${operatingSystem}" != "linux" ]; then
  # On windows so make sure that Cygwin and Git Bash is not mixed
  # because can lead to confusion and technical issues.
  if [ ${cygwinRepoCount} -ne 0 ] && [ ${repoCount} -ne ${cygwinRepoCount} ]; then
    ${echo2} "${actionColor}Number of Cygwin-cloned repos (filemode=true) is ${cygwinRepoCount}, which is not = the repo count ${repoCount}.${colorEnd}"
    ${echo2} "${actionColor}Mixing Cygwin (filemode=true) and Git Bash (filemode=false) can cause issues.${colorEnd}"
  fi
fi
# Print message to alert about attention needed on any repository.
# Don't need to color the number of repositories.
echo "Product Git repositories folder: ${gitReposFolder}"
echo "Repository repository list file: ${repoListFile}"
echo "${lineDoubleDash}"
echo "Number of repositories:                                                   ${repoCount}"
if [ ${upToDateRepoCount} -eq ${repoCount} ]; then
  ${echo2} "Number of up-to-date repositories:                                        ${okColor}${upToDateRepoCount}${colorEnd}"
else
  ${echo2} "Number of up-to-date repositories:                                        ${actionColor}${upToDateRepoCount}${colorEnd}"
fi
if [ ${needToPullRepoCount} -eq 0 ]; then
  ${echo2} "Number of 'need to pull' repositories (remote commits available):         ${okColor}${needToPullRepoCount}${colorEnd}"
else
  ${echo2} "${actionColor}Number of 'need to pull' repositories (remote commits available):         ${needToPullRepoCount}${colorEnd}"
fi
if [ ${needToPushRepoCount} -eq 0 ]; then
  ${echo2} "Number of 'need to push' repositories (local commits saved):              ${okColor}${needToPushRepoCount}${colorEnd}"
else
  ${echo2} "${actionColor}Number of 'need to push' repositories (local commits saved):              ${needToPushRepoCount}${colorEnd}"
fi
if [ ${divergedRepoCount} -eq 0 ]; then
  ${echo2} "Number of diverged repositories (need to pull and push):                  ${okColor}${divergedRepoCount}${colorEnd}"
else
  ${echo2} "${actionColor}Number of diverged repositories (need to pull and push):                  ${divergedRepoCount}${colorEnd}"
fi
if [ ${localChangesRepoCount} -eq 0 ]; then
  ${echo2} "Number of repositories with local changes (working and/or staged files):  ${okColor}${localChangesRepoCount}${colorEnd}"
else
  ${echo2} "${actionColor}Number of repositories with local changes (working and/or staged files):  ${localChangesRepoCount}${colorEnd}"
fi
if [ ${emptyFoldersRepoCount} -eq 0 ]; then
  ${echo2} "Number of repositories with empty folders:                                ${okColor}${emptyFoldersRepoCount}${colorEnd}"
else
  ${echo2} "${actionColor}Number of repositories with empty folders:                                ${emptyFoldersRepoCount}${colorEnd}"
fi
echo "${lineDoubleDash}"

# Done.
exit 0
