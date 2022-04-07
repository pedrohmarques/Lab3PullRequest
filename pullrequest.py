import json
from jsonConvert import JsonConvert
from datetime import datetime
import requests

class PullRequest:
    def __init__(self, token):
        self.token = token

    def __get_query_pullrequests(self, owner, name, type):
        query = f"""
            {{
                repository(owner: "{owner}", name: "{name}") {{
                    REQUEST: pullRequests(states: {type}, last: 50) {{
                        pageInfo {{
                            endCursor
                            hasNextPage
                        }}
                        nodes {{
                            createdAt
                            closedAt
                            state
                            bodyText
                            participants {{
                                totalCount
                            }}
                            comments {{
                                totalCount
                            }}
                            files(last: 10) {{
                                totalCount
                                nodes {{
                                    additions
                                    deletions
                                }}
                            }}
                            mergeCommit {{
                                additions
                                deletions
                            }}
                            reviews(states: APPROVED, last: 10) {{
                                totalCount
                                nodes {{
                                    createdAt
                                    publishedAt
                                    bodyText
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        return query

    def get_pullrequests_git(self, type):
        headers = headers = {'Authorization': f'Bearer {self.token}'}
        res = []

        with open('repositories.json', "r") as file:
            reader = json.load(file)
            for data in reader:
                owner_name = data['nameWithOwner'].split('/')
                query = self.__get_query_pullrequests(owner_name[0], owner_name[1], type)
                result = requests.post("https://api.github.com/graphql", json={'query': query}, headers=headers)
                if result.status_code == 200:
                    data = result.json()['data']['repository']['REQUEST']
                    pullrequests = list(map(lambda x: x, data['nodes']))
                    res = res + pullrequests

        return res

    def get_pullrequest_available(self, pullrequest):
        if pullrequest['reviews']['totalCount'] > 0:
            created_at = pullrequest['createdAt']
            merged_at = pullrequest['closedAt']

            created_at = datetime.strptime(created_at[0:10] + ' ' + created_at[11:16], '%Y-%m-%d %H:%M')
            merged_at = datetime.strptime(merged_at[0:10] + ' ' + merged_at[11:16], '%Y-%m-%d %H:%M')
            
            duration = merged_at - created_at
            duration_in_s = duration.total_seconds()
            hours = divmod(duration_in_s, 3600)[0]
            
            if(hours < 1):
                return False
            else:
                return True
        else:
            return False

    def update_json_to_csv(self, pullrequest_availabled):
        for repo in pullrequest_availabled:
            total_changes = self.sum_files_changes(repo['files'])
            repo['files']['total_Additions'] = total_changes['additions']
            repo['files']['total_Deletions'] = total_changes['deletions']
            del repo['files']['nodes']

    def sum_files_changes(self, data):
        addition = 0
        deletions = 0
        for node in data['nodes']:
            addition = addition + node['additions']
            deletions = deletions + node['deletions']
        
        return { "additions": addition, "deletions": deletions }
            
    def get_pullrequests(self):
        pullrequests_merged = self.get_pullrequests_git('MERGED')
        JsonConvert('pull_request_MERGED.json').update(pullrequests_merged)
        pullrequests_closed = self.get_pullrequests_git('CLOSED')
        JsonConvert('pull_request_CLOSED.json').update(pullrequests_closed)
        pullrequest_availabled = []

        for pullrequest_merged in pullrequests_merged:
            is_available = self.get_pullrequest_available(pullrequest_merged)
            if is_available:
                pullrequest_availabled.append(pullrequest_merged)

        for pullrequest_closed in pullrequests_closed:
            is_available = self.get_pullrequest_available(pullrequest_closed)
            if is_available:
                pullrequest_availabled.append(pullrequest_closed)
        

        self.update_json_to_csv(pullrequest_availabled)
        return pullrequest_availabled
    
    