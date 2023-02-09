# AUTOGENERATED! DO NOT EDIT! File to edit: ../notebooks/00_pymatch.ipynb.

# %% auto 0
__all__ = ['add_someone', 'find_user', 'delete_user', 'show_interests', 'add_interests', 'delete_interests', 'match_interests',
           'database_exists', 'fetch_all', 'database_to_dataframe', 'count_interests', 'interestcount_to_dataframe',
           'total_users']

# %% ../notebooks/00_pymatch.ipynb 4
from datetime import datetime
import time
from deta import Deta
import pandas as pd
import os
import ulid
from typing import Optional, List, Dict

# %% ../notebooks/00_pymatch.ipynb 8
def add_someone(user_id: str, # unique identifier to authenticate users
                database_name: str, # create or connect to an existing database
                interests: List[str],
                group_id: Optional[str] = None, # id for the group/server the user is from
                project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                ):

    """
    Create a new user and add their interests. Will be used by `add_interests`.
    
    All interests will be made lowercase.
    """
    
    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)
      
    user = db.put(
        {
            'key': ulid.new().str,
            "date": datetime.now().strftime("%d-%m-%Y %H:00"),
            "user_id": user_id,
            "group_id": group_id,
            'interests': interests
            }
    )

# %% ../notebooks/00_pymatch.ipynb 11
def find_user(user_id: str,
              database_name: str,
              group_id: Optional[str] = None, # id for the group/server the user is from
              project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
             ) -> List[dict]:
    
    "Find all data on a user from thier user_id and/or group_id."

    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)

    # check if user exists
    # if there's group + user ID then check for the combination
    if group_id is None:
        user = db.fetch({"user_id": user_id}).items
    else:
        user = db.fetch({"group_id": user_id, "group_id": user_id}).items

    if bool(user):
        return user
    else:
        print("user doesn't exist")
        raise ValueError("user doesn't exist")

# %% ../notebooks/00_pymatch.ipynb 13
def delete_user(user_id: str,
                database_name: str,
                project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
               ):
    
    "Deletes an entry using thier user_id if they exist"

    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)

    delete = db.fetch(
        {
        "user_id": user_id
        }
    ).items

    # if exists, delete
    if bool(delete):
        key = delete[0]["key"]
        db.delete(key)
        print(f"user {user_id} deleted from {database_name}")
    else:
        print(f"user {user_id} not in {database_name}")

# %% ../notebooks/00_pymatch.ipynb 16
def show_interests(user_id: str, # unique identifier
                   database_name: str,
                   group_id: str, # id for the group/server the user is from
                   project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                  ) -> List[str]:
    
    "Gets a list of interests for a given user within a group_id. Uses `find_user`."
    
    return find_user(user_id, database_name, project_key)[0]["interests"]

# %% ../notebooks/00_pymatch.ipynb 18
def add_interests(user_id: str, # unique identifier to authenticate users
                  interests: List[str], 
                  database_name: str, # create or connect to an existing database
                  group_id: Optional[str] = None, # id for the group/server the user is from
                  project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                 ):

    "Add new interests to a user if they exist or creates a new user using `add_someone` if they don't."
    
    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)
    
    # check if user exists
    # if there's group + user ID then check for the combination
    if group_id is None:
        check = db.fetch({"user_id": user_id}).items
    else:
        check = db.fetch({"user_id": user_id, "group_id": group_id}).items
    
    if bool(check):
        # get key
        key = check[0]["key"]
        
        # get a list of existing interests
        current = show_interests(user_id, group_id, database_name, project_key)
        
        # concat the new interest(s) to the existing list
        # only add unique interests i.e. no duplicates
        new = list(set(current+interests))
        
        # update lowercase interests
        user = db.update({'interests': list(map(str.lower, new))}, key=key)

    else:
        # create new user if they don't exist
        add_someone(user_id = user_id,
                    group_id = group_id,
                    interests = interests, 
                    database_name = database_name
                   )

# %% ../notebooks/00_pymatch.ipynb 20
def delete_interests(user_id: str, # unique identifier to authenticate users
                     remove_interests: List[str], 
                     database_name: str, # create or connect to an existing database
                     group_id: Optional[str] = None, # id for the group/server the user is from
                     project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                    ):

    "Delete interest(s). If group_is is `None` then interests of the user will be deleted in all groups."
    
    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)
    
    if group_id is not None:
        # get a list of existing interests
        current = show_interests(user_id, group_id, database_name, project_key)

        # check if the thing they want to delete is in the list at all
        # https://stackoverflow.com/questions/20238281/check-whether-an-item-in-a-list-exist-in-another-list-or-not-python#
        if bool(set(current)&set(remove_interests)) is False:
            raise ValueError("interest(s) to be removed don't even exist bro")

        # remove item(s)
        new = list(set(current) - set(remove_interests))

        # get key
        from_user = db.fetch({"user_id": user_id, "group_id": group_id}).items
        key = from_user[0]["key"]

        # update interests
        user = db.update({'interests': list(map(str.lower, new))}, key=key)
        
    else:
        # do the same thing, for every group
        all_groups = find_user(user_id, database_name, project_key)
        
        for each_group in all_groups:
            # get a list of existing interests
            current = each_group["interests"]
            
            if bool(set(current)&set(remove_interests)) is False:
                raise ValueError("interest(s) to be removed don't even exist bro")

            # remove item(s)
            new = list(set(current) - set(remove_interests))

            # get key
            key = each_group["key"]

            # update interests
            user = db.update({'interests': list(map(str.lower, new))}, key=key)

# %% ../notebooks/00_pymatch.ipynb 22
def match_interests(user_id: str,
                    database_name: str,
                    project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                   ) -> List[dict]:
    
    "Match users to a given user_id and return names and common/shared interests"

    deta = Deta(os.environ[project_key])
    users = deta.Base(database_name)
    
    # get key
    from_user = users.fetch({"user_id": user_id}).items
    key = from_user[0]["key"]

    # get interests for a user
    interests = users.get(key)['interests']

    # match
    match = users.fetch([{'interests?contains' : item} for item in interests]).items

    # name = item['name']
    # common_interests = set(interests) & set(item['interests'])

    matches = []
    for item in match:
        matches.append(
            {
                'group_id': item['group_id'],
                'user_id': item['user_id'],
                'common interests': list(set(interests) & set(item['interests'])),
                'common interests count': len(set(interests) & set(item['interests']))
            }
        )

    return matches

# %% ../notebooks/00_pymatch.ipynb 25
def database_exists(database_name: str,
                    project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                   ) -> bool:
    
    "check if db exists by checking if there's at least one item"

    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)

    if db.fetch(limit=1).items:
        return True
    else:
        raise NameError(f"{database_name} doesn't exist")

# %% ../notebooks/00_pymatch.ipynb 26
def fetch_all(database_name: str,
              project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
             ) -> List[dict]:
    """
    fetches the whole database

    this is from deta's docs: https://docs.deta.sh/docs/base/sdk/#fetch-all-items-1

    uses `database_exists`
    """

    database_exists(database_name, project_key) # will create error if db doesn't exist

    deta = Deta(os.environ[project_key])
    db = deta.Base(database_name)
    
    res = db.fetch()
    all_items = res.items

    # fetch until last is 'None'
    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items   

    return all_items

# %% ../notebooks/00_pymatch.ipynb 27
def database_to_dataframe(database_name: str,
                          project_key: str = "DETA_PROJECT_KEY" # the environment variable name where your Deta project key is stored
                         ) -> pd.DataFrame:
    """
    fetches the whole database and converts it to a pandas dataframe

    uses `fetch_all`
    """

    import pandas as pd

    all_items = fetch_all(database_name, project_key)

    return pd.DataFrame.from_dict(all_items)

# %% ../notebooks/00_pymatch.ipynb 29
def count_interests(database_name: str ='users') -> List[dict]:
    """
    Shows each interest and how many times they occur. If needed, this can work for any column that contains a list of strings.

    Uses `database_to_dataframe`
    """

    count = []
    for item in database_to_dataframe(database_name)['interests'].explode().value_counts():
        count.append(item.to_dict())

    return count

# %% ../notebooks/00_pymatch.ipynb 30
def interestcount_to_dataframe(database_name: str ='users') -> pd.DataFrame:
    """
    Get interest counts as a pandas dataframe

    Uses `database_to_dataframe`
    """

    # https://re-thought.com/pandas-value_counts/

    value_counts = database_to_dataframe(database_name)['interests'].explode().value_counts()

    # converting to df and assigning new names to the columns
    df_value_counts = pd.DataFrame(value_counts)
    df_value_counts = df_value_counts.reset_index()
    df_value_counts.columns = ['interests', 'count'] # change column names
    
    return df_value_counts

# %% ../notebooks/00_pymatch.ipynb 32
def total_users(database_name: str) -> int:
    "Count total users. Uses `fetch_all`"

    return len(fetch_all(database_name))
