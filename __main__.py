from repositories import Repository
from jsonConvert import JsonConvert
from pullrequest import PullRequest
from exportcsv import exportDataToCsv

print("Options")
print("1 - Atualiza Repositorios")
print("2 - Atualiza Pull Request")

op = input()
if op == '1':
    repository = Repository(["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", "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"])
    print("Get Repositories")
    repositories = repository.get_repositories()
    JsonConvert('repositories.json').update(repositories)
    exportDataToCsv('repositories.json', 'repositories.csv')
elif op == '2':
    pullrequest = PullRequest(["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", "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"])
    print("Get Pull Requests")
    pull_requests = pullrequest.get_pullrequests()
    JsonConvert('pull_request.json').update(pull_requests)
    exportDataToCsv('pull_request.json', 'pull_request.csv')
