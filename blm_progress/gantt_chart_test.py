# %%
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import altair as alt
from altair_saver import save



# %%
def gantt_chart(wd=None, inf=None, shtname=None, export=None, width=None):
    if wd is None:
        wd = os.getcwd()
    if inf is None:
        inf = 'tasks.xlsx'
    if shtname is None:
        shtname = 0
    if width is None:
        width = 0

    # Use the progress to find how much of the bars should be filled
    # (i.e. another end date)
    df = pd.read_excel(os.path.join(wd,'tasks.xlsx'), sheet_name=shtname)
    df["progress date"] =  (df["end date"] - df["start date"]) * df["progress %"] / 100 + df["start date"]
    # Concatenate the two 
    newdf = np.concatenate([df[["Tasks", "start date", "end date", "progress %"]].values,  
                            df[["Tasks", "start date", "progress date", "progress %"]].values])
    newdf = pd.DataFrame(newdf, columns=["Tasks", "start date", "end date", "progress %"])
    # Reconvert back to datetime
    newdf["start date"] = pd.to_datetime(newdf["start date"])
    newdf["end date"] = pd.to_datetime(newdf["end date"])
    # This is the indicator variable (duration vs progress) where the grouping takes place
    newdf["progress_"] = np.concatenate([np.ones(len(newdf)//2), np.zeros(len(newdf)//2), ])
    # color for first half, color for second half
    if shtname == 'papers':
        range_ = ['#9b45c9', '#ce78fc',]
    else:
        range_ = ['#1f77b4', '#5fa0d4',]
    # The stacked bar chart will be our "gantt with progress"
    chart = alt.Chart(newdf).mark_bar().encode(
        x=alt.X('start date', stack=None),
        x2='end date',
        # y='Tasks',
        y=alt.Y(
            'Tasks',
            # sort=list(df.sort_values(["end date", "start date"])["Tasks"])*2
            sort=None,
            ),
        color=alt.Color('progress_', scale=alt.Scale(range=range_), legend=None)
    ).properties(width=width)
    # Create appropriate labels
    # newdf["text%"] = newdf["progress %"].astype(str) + " %"
    newdf["text%"] = newdf["progress %"].map('{:.0f}'.format) + " %"

    # And now add those as text in the graph
    text = alt.Chart(newdf).mark_text(align='right', baseline='middle', dx=3, color="white",  fontWeight="bold").encode(
        y=alt.Y(
            'Tasks',
            # sort=list(df.sort_values(["end date", "start date"])["Tasks"])*2
            sort=None,
            ),
        # y='Tasks',
        x=alt.X('start date'),
        text='text%',
    ).properties(width=width)
    alt.layer(chart, text).configure_axis(
        # labelFontSize=15,
        # titleFontSize=15
    )
    if export is True:
        alt.layer(chart, text).save('chart.html', embed_options={'renderer':'svg'})


def gantt_chart_gspread(shtname=None, width=None):

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
        ]
    if width is None:
        width = 0

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    if shtname is None:
        sheet = client.open("BLM_progress").get_worksheet(0)
    else:
        sheet = client.open("BLM_progress").worksheet(shtname)
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    df.loc[:, 'start date'] = pd.to_datetime(df.loc[:, 'start date'])
    df.loc[:, 'end date'] = pd.to_datetime(df.loc[:, 'end date'])
    df.loc[:, 'progress %'] = df.loc[:, 'progress %'].astype(float)

    df["progress date"] =  (df["end date"] - df["start date"]) * df["progress %"] / 100 + df["start date"]
    # Concatenate the two 
    newdf = np.concatenate([df[["Tasks", "start date", "end date", "progress %", "leader"]].values,  
                            df[["Tasks", "start date", "progress date", "progress %", "leader"]].values])
    newdf = pd.DataFrame(newdf, columns=["Tasks", "start date", "end date", "progress %", "leader"])
    
    # Reconvert back to datetime
    newdf["start date"] = pd.to_datetime(newdf["start date"])
    newdf["end date"] = pd.to_datetime(newdf["end date"])
    # This is the indicator variable (duration vs progress) where the grouping takes place
    newdf["progress_"] = np.concatenate([np.ones(len(newdf)//2), np.zeros(len(newdf)//2), ])
    # color for first half, color for second half
    if shtname == 'papers':
        range_ = ['#9b45c9', '#ce78fc',]
    else:
        range_ = ['#1f77b4', '#5fa0d4',]

    # # The stacked bar chart will be our "gantt with progress"
    # chart = alt.Chart(newdf).mark_bar().transform_calculate(
    #     Tasks="split(datum.Tasks, ':')"
    #     ).encode(
    #     x=alt.X('start date', stack=None),
    #     x2='end date',
    #     # y='Tasks',
    #     y=alt.Y(
    #         'Tasks',
    #         # sort=list(df.sort_values(["end date", "start date"])["Tasks"])*2
    #         sort=None,
    #         ),
    #     color=alt.Color('progress_', scale=alt.Scale(range=range_), legend=None)
    # )
    # The stacked bar chart will be our "gantt with progress"
    chart = alt.Chart(newdf).mark_bar().encode(
        x=alt.X('start date', stack=None),
        x2='end date',
        # y='Tasks',
        y=alt.Y(
            'Tasks',
            # sort=list(df.sort_values(["end date", "start date"])["Tasks"])*2
            sort=None,
            ),
        color=alt.Color('progress_', scale=alt.Scale(range=range_), legend=None)
    )


    # .mark_text(align='left',baseline='middle', lineBreak='\n').encode(text='Tasks:N')

    # Create appropriate labels
    # newdf["text%"] = newdf["progress %"].astype(str) + " %"
    newdf["text%"] = newdf["progress %"].map('{:.0f}'.format) + " %"

    # And now add those as text in the graph
    text = alt.Chart(
        newdf, title=f"BLM Watershed Modeling Progress (Gantt) Chart"
        ).mark_text(
            align='left', baseline='middle', dx=3, color="white",  fontWeight="bold"
            ).encode(
                y=alt.Y(
                    'Tasks',
                    # sort=list(df.sort_values(["end date", "start date"])["Tasks"])*2
                    sort=None,
                    ),
                # y='Tasks',
                x=alt.X('start date'),
                text='text%',
    )

    # And now add those as text in the graph
    leader = alt.Chart(
        newdf, title=f"BLM Watershed Modeling Progress (Gantt) Chart"
        ).mark_text(
            align='left', baseline='middle', dx=40, color="grey",  fontWeight="normal"
            ).encode(
                y=alt.Y(
                    'Tasks',
                    # sort=list(df.sort_values(["end date", "start date"])["Tasks"])*2
                    sort=None,
                    ),
                # y='Tasks',
                x=alt.X('start date'),
                text='leader',
    )
    final =  chart + text + leader
    final = final.properties(width=width).configure_axisY(
        # titleAngle=0, 
        # titleY=-10,
        # titleX=-60,
        # labelPadding=100, 
        # labelAlign='right',
        labelLimit=0,
        ).configure_axis(
        # labelFontSize=20,
        # titleFontSize=20
    ).interactive()


    os.chdir(os.getcwd())
    if shtname is None:
        final.save('index.html', embed_options={'renderer':'svg'})
    else:
        final.save('timeline-{}.html'.format(shtname), embed_options={'renderer':'svg'})
    print('Printed!')
    print(newdf)

if __name__ == '__main__':
    # gantt_chart(export=True, shtname='papers', width=700)
    gantt_chart_gspread(width=800)
    print('Hi there!')

