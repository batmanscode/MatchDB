# AUTOGENERATED! DO NOT EDIT! File to edit: ../notebooks/00_pymatch.ipynb.

# %% auto 0
__all__ = ['deta_init', 'add_someone', 'find_by_userid', 'delete_user', 'match_interests', 'database_exists', 'fetch_all',
           'database_to_dataframe', 'count_interests', 'interestcount_to_dataframe', 'total_users']

# %% ../notebooks/00_pymatch.ipynb 4
from datetime import datetime
import time
from deta import Deta
import pandas as pd
import os
import ulid
from typing import Optional, List

# %% ../notebooks/00_pymatch.ipynb 6
def deta_init(
    project_key: str # the name of the environment variable
):
    "Initialize with a Deta project key"

    deta = Deta(os.environ["PROJECT_KEY"])
    
    return deta

# %% ../notebooks/00_pymatch.ipynb 9
def add_someone(name: Optional[str],
                username: str, 
                user_id: str, # unique identifier to authenticate users
                interests: List[str], 
                database_name: str # create or connect to an existing database
                ):

    "Add a new user"

    db = deta.Base(database_name)

    user = db.put(
        {
            'key': ulid.new().str,
            "date": datetime.now().strftime("%d-%m-%Y %H:00"),
            "user id": user_id,
            'name': name,
            'interests': interests
            }
    )

    return user

# %% ../notebooks/00_pymatch.ipynb 11
def find_by_userid(user_id: str):
    "Find a user from thier user_id"

    db = deta.Base(database_name)

    user = db.fetch(
        {
        "user id": user_id
        }
    ).items

    if bool(user):
        return user
    else:
        print("user doesn't exist")

# %% ../notebooks/00_pymatch.ipynb 13
def delete_user(user_id: str):
    "Deletes an entry using thier user_id if they exist"

    db = deta.Base(database_name)

    delete = db.fetch(
        {
        "user id": user_id
        }
    ).items

    # if exists, delete
    if bool(delete):
        key = delete[0]["key"]
        db.delete(key)
        print(f"user {user_id} deleted from {database_name}")
    else:
        print(f"user {user_id} not in {database_name}")

# %% ../notebooks/00_pymatch.ipynb 15
def match_interests(user_id: str, database_name: str):
    "Match users to a given user_id and return names and common/shared interests"

    db = deta.Base(database_name)

    # get interests for a user
    interests = users.get(user_id)['interests']

    # match
    match = users.fetch([{'interests?contains' : item} for item in interests]).items

    name = item['name']
    common_interests = set(interests) & set(item['interests'])

    matches = []
    for item in match:
        matches.append(
            {
                'name': item['name'],
                'common interests': set(interests) & set(item['interests'])
            }
        )

    return matches

# %% ../notebooks/00_pymatch.ipynb 18
def database_exists(database_name: str):
    "check if db exists by checking if there's at least one item"

    db = deta.Base(database_name)

    if db.fetch(limit=1).items:
        return True
    else:
        raise NameError(f"{database_name} doesn't exist")

# %% ../notebooks/00_pymatch.ipynb 19
def fetch_all(database_name: str):
    """
    fetches the whole database

    this is from deta's docs: https://docs.deta.sh/docs/base/sdk/#fetch-all-items-1

    uses `database_exists`
    """

    database_exists(database_name) # will create error if db doesn't exist

    db = deta.Base(database_name)
    
    res = db.fetch()
    all_items = res.items

    # fetch until last is 'None'
    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items   

    return all_items

# %% ../notebooks/00_pymatch.ipynb 20
def database_to_dataframe(database_name: str):
    """
    fetches the whole database and converts it to a pandas dataframe

    uses `fetch_all`
    """

    import pandas as pd

    all_items = fetch_all(database_name=database_name)

    return pd.DataFrame.from_dict(all_items)

# %% ../notebooks/00_pymatch.ipynb 22
def count_interests(database_name: str ='users'):
    """
    Shows each interest and how many times they occur. If needed, this can work for any column that contains a list of strings.

    Uses `database_to_dataframe`
    """

    count = []
    for item in database_to_dataframe(database_name)['interests'].explode().value_counts():
        count.append(item.to_dict())

    return count

# %% ../notebooks/00_pymatch.ipynb 23
def interestcount_to_dataframe(database_name: str ='users'):
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

# %% ../notebooks/00_pymatch.ipynb 25
def total_users(database_name: str):
    "Count total users. Uses `fetch_all`"

    return len(fetch_all(database_name))