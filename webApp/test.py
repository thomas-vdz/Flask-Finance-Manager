from webApp import db , create_app
from webApp.models import Transaction
import pandas as pd
import matplotlib.pyplot as plt


app = create_app()
app.app_context().push()

df = pd.read_sql("transaction",db.engine)

df['Date'] = pd.to_datetime(df['date'])
df = df.loc[df['category'] != 'abbonement']
df = df.groupby([pd.Grouper(key='date', freq='M'),'category'])

fig, ax = plt.subplots(figsize=(15,10))
plot = df.sum()['amount'].unstack().plot(ax=ax)

