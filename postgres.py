import pandas as pd
import numpy as np

from database.DatabaseUtil import DatabaseUtil
from database.models import Collisions, map_collision_columns


# Get reference to 'motor_db' database
client = DatabaseUtil.get_mongo_client()
db = client.motor_db

# fetch all collections
collisions_collection = db.motor_collisions
collisions = pd.DataFrame(list(collisions_collection.find()))
client.close()

#data cleaning/processing
collisions.replace({np.nan: None}, inplace=True)
collisions['CRASH TIME'] = pd.to_datetime(collisions['CRASH TIME'], format='mixed')
# collisions = collisions.loc[~collisions['CONTRIBUTING FACTOR VEHICLE 1'].isna()]
collisions.rename(columns=map_collision_columns, inplace=True)
collisions_df = collisions[map_collision_columns.values()]

try:
    session = DatabaseUtil.get_session()
    DatabaseUtil.save_df_to_DB_with_session(collisions_df, str(Collisions.metadata.sorted_tables[0]).split('.')[1],
                                            append=False, session=session) #truncate and insert
    # DatabaseUtil.insert_data(Collisions, collisions_df, session)
    session.commit()
except Exception as err:
    session.rollback()
    raise err
finally:
    DatabaseUtil.close_session(session)

