from repositories import Repository
from jsonConvert import JsonConvert
from pullrequest import PullRequest

print("Options")
print("1 - Atualiza Repositorios")
print("2 - Atualiza Pull Request")

op = input()
if op == '1':
    repository = Repository("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")
    print("Get Repositories")
    repositories = repository.get_repositories()
    JsonConvert('repositories.json').update(repositories)
elif op == '2':
    pullrequest = PullRequest("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")
    print("Get Pull Requests")
    pull_requests = pullrequest.get_pullrequests()
    JsonConvert('pull_request.json').update(pull_requests)
