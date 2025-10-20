# Aurvogh auth login  # si no lo has hecho
gh api -H "Accept: application/vnd.github+json" -X GET /user/repos \
  --paginate -f per_page=100 \
  -F affiliation=owner,collaborator,organization_member \
  --jq '.[] | [.full_name, .visibility, .fork, .archived, .updated_at, .html_url] | @csv' \
  > repos.csv/src
/tests
/scripts
/.github/ISSUE_TEMPLATE
/.github/workflows
.gitignore

README.md
LICENSE
CODE_OF_CONDUCT.md
SECURITY.md
CODEOWNERS