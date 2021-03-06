from repositories import Repository
from jsonConvert import JsonConvert
from pullrequest import PullRequest
from exportcsv import exportDataToCsv

print("Options")
print("1 - Atualiza Repositorios")
print("2 - Atualiza Pull Request")

op = input()
if op == '1':
    repository = Repository(["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", "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", "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",
        "ghp_m968hcrRbckWpcG3j4LgMvNAA5PRV42hvHp", "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", "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",
        "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", "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", "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"])
    print("Get Repositories")
    repositories = repository.get_repositories()
    JsonConvert('repositories.json').update(repositories)
    exportDataToCsv('repositories.json', 'repositories.csv')
elif op == '2':
    pullrequest = PullRequest(["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", "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", "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",
        "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", "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"])
    print("Get Pull Requests")
    pull_requests = pullrequest.get_pullrequests()
    JsonConvert('pull_request.json').update(pull_requests)
    exportDataToCsv('pull_request.json', 'pull_request.csv')
elif op == '3':
    exportDataToCsv('pull_request.json', 'pull_request.csv')
