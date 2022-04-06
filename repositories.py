import requests

class Repository:
    def __init__(self, token):
        self.token = token

    def __get_query_repositories(self, after):
        query = f"""
            {{
                search(first: 100, {after}, query: "stars:>100", type: REPOSITORY) {{
                    pageInfo {{
                        startCursor
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        ... on Repository {{
                            id
                            name
                            nameWithOwner
                            stargazers {{
                                totalCount
                            }}
                        }}
                    }}
                }}
            }}
            """
        return query

    def __availabe_repositorie(self, owner, name):
        query = f"""
            {{
                repository(owner:"{owner}", name: "{name}") {{
                    MERGED_REQUEST: pullRequests(states: MERGED) {{
                            totalCount
                        }}
                    CLOSED_REQUEST: pullRequests(states: CLOSED) {{
                            totalCount
                        }}
                }}
            }}
            """
        return query
    
    def get_repositories_git(self):
        headers = headers = {'Authorization': f'Bearer {self.token}'}
        after = 'after: null'
        res = []
        for i in range(10):
            query = self.__get_query_repositories(after)
            result = requests.post("https://api.github.com/graphql", json={'query': query}, headers=headers)
            if result.status_code == 200:
                data = result.json()['data']['search']
                after = f"""after: "{ data['pageInfo']['endCursor'] }" """
                repositories = list(map(lambda x: x, data['nodes']))
                res = res + repositories
        return res
    
    def repo_available(self, owner_name):
        headers = headers = {'Authorization': f'Bearer {self.token}'}
        query = self.__availabe_repositorie(owner_name[0], owner_name[1])
        result = requests.post("https://api.github.com/graphql", json={'query': query}, headers=headers)
        if result.status_code == 200:
            data = result.json()['data']['repository']
            total_merged_closed = data['MERGED_REQUEST']['totalCount'] + data['CLOSED_REQUEST']['totalCount']
            
            if (total_merged_closed < 1000):
                return False
            else:
                return True

    def get_repositories(self):
        repositories = self.get_repositories_git()
        returned_repo = []

        for repo in repositories:
            owner_name = repo['nameWithOwner'].split('/')
            is_available = self.repo_available(owner_name)
            if(is_available):
                returned_repo.append(repo)

        return returned_repo
        


        

            
