import json
from jsonConvert import JsonConvert
from datetime import datetime
import requests

class PullRequest:
    def __init__(self, token):
        self.number_token = 0
        self.tokens = token
        self.next_Token()

    def next_Token(self):
        if self.number_token == len(self.tokens):
            print('ACABOU OS TOKEN')
        else:
            self.token = self.tokens[self.number_token]
            self.number_token = self.number_token + 1

    def __get_query_pullrequests(self, owner, name, after, state):
        query = f"""
            {{
                repository(owner: "{owner}", name: "{name}") {{
                    REQUEST: pullRequests(states: {state}, first: 100, {after}) {{
                        pageInfo {{
                            endCursor
                            hasNextPage
                        }}
                        nodes {{
                            createdAt
                            closedAt
                            state
                            body
                            participants {{
                                totalCount
                            }}
                            comments {{
                                totalCount
                            }}
                            files(first: 10) {{
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
                            reviews(states: APPROVED, first: 10) {{
                                totalCount
                                nodes {{
                                    body
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        return query

    def get_pullrequests_git(self, state):
        res = []
        hasNextPage = True
        after = 'after: null'
        teste = 0

        with open('repositories.json', "r") as file:
            reader = json.load(file)
            data = reader[0]
            #for data in reader:
            owner_name = data['nameWithOwner'].split('/')
            
            while hasNextPage:
                teste = teste + 1
                response = self.get_request(owner_name[0], owner_name[1], after, state)
                if response.status_code == 200:
                    pageInfo = response.json()['data']['repository']['REQUEST']['pageInfo']
                    res = self.increment_result(response, res)
                    hasNextPage = pageInfo['hasNextPage']
                    after = f"""after: "{ pageInfo['endCursor'] }" """
                else:
                    print(response.status_code)
                    if response.status_code == 500:
                        self.next_Token()
                print(teste)
        
        return res

    def get_request(self, owner, name, after, state):
        headers = headers = {'Authorization': f'Bearer {self.token}'}
        query = self.__get_query_pullrequests(owner, name, after, state)
        result = requests.post("https://api.github.com/graphql", json={'query': query}, headers=headers)

        return result

    def increment_result(self, response, result):
        data = response.json()['data']['repository']['REQUEST']
        pullrequests = list(map(lambda x: x, data['nodes']))
        
        return result + pullrequests

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

        ''' pullrequests_closed = self.get_pullrequests_git('CLOSED')
        JsonConvert('pull_request_CLOSED.json').update(pullrequests_closed)'''

        pullrequest_availabled = []

        for pullrequest_merged in pullrequests_merged:
            is_available = self.get_pullrequest_available(pullrequest_merged)
            if is_available:
                pullrequest_availabled.append(pullrequest_merged)
        
        '''for pullrequest_closed in pullrequests_closed:
            is_available = self.get_pullrequest_available(pullrequest_closed)
            if is_available:
                pullrequest_availabled.append(pullrequest_closed)'''
      
        self.update_json_to_csv(pullrequest_availabled)
        return pullrequest_availabled
    
    