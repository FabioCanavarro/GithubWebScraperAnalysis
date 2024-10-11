#libraries
import webbrowser
from threading import Timer
from flask import Flask, render_template_string
import requests as req
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import bs4
import datetime as dt
import google.generativeai as genai
import plotly
import contextlib

import time
import sys
GOOGLE_API_KEY=('AIzaSyDW-jOhDIzqx5Vs8kwEOX0NxO3vR1BRcYE')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)




def LLMreq(data: dict) -> str:
    prompt = "context: Tell me the prominent trends like the theme and other trends without the example \n prompt:summarize the trends in the data, these are the top starred github repositories stored in a tuple(name,firstparagraph, star count), since this is data scraped the first paragraph sometimes may have some errors:"+str([(i,data[i]["firstparagraph"],data[i]["watchers_count"]) for i in data])
    response = model.generate_content(prompt)
    return(response.text)



def get_data(url: str) -> dict:
    response = req.get(url,headers={"User-Agent": "siti21532704","Accept":"application/json, text/plain, */*","x-github-api-version-selected":"2022-11-28","authorization":"token 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"})
    print("Response status code:",response.status_code)
    responses = json.loads(response.text)["items"]
    repo = {
        i["full_name"]: {"name":i["full_name"],"html_url":i["html_url"],"language":i["language"],"watchers_count": i["watchers_count"], "firstparagraph": "","date":date,"forks":i["forks_count"],"Fork?":i["fork"]}
        for i in responses
    }
    total = len(repo)
    # get the first paragraph of the readme to get some context
    for index, _ in enumerate(repo):
        url = repo[_]["html_url"]
        soup = bs4.BeautifulSoup(req.get(url).text, "html.parser")
        try:
            main_paragraph = soup.find_all("div",class_="Box-sc-g0xbh4-0 vIPPs")[0]
            text = main_paragraph.find_all("article",class_="markdown-body entry-content container-lg")[0]
            firstparagraph = text.find_all("p")[0].text
        except Exception:
            firstparagraph = "No paragraph"
        repo[_]["firstparagraph"] = firstparagraph
        progress = (index + 1) / total
        bar_length = 20
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # Clear line and print progress
        sys.stdout.write('\r')
        sys.stdout.write(f"Processing repositories: [{bar}] {index + 1}/{total} {progress:.0%}")
        sys.stdout.flush()
        
        time.sleep(0.1)
    return repo


presentDate = dt.datetime.now()
date = str(presentDate).split(" ")[0]
tempdatetimedate = presentDate- dt.timedelta(days=7)
tempdate = str(tempdatetimedate).split(" ")[0]
data = {}
starterdate = presentDate - dt.timedelta(days=30)
#check if there is a data.csv file with present info
try:
    data = pd.read_csv("data.csv").sort_values(by="date",ascending=False).to_dict(orient='index')
    datetemp = dt.datetime.strptime(data[list(data.keys())[0]]["date"],"%Y-%m-%d")
    print("Data.csv found")
    if datetemp != presentDate:
        with contextlib.suppress(Exception):
            if ((presentDate- datetemp).days //7) > 0:
                print("data.csv is outdated, updating")
                for _ in range(0,(presentDate- datetemp).days //7):
                    print(f"Starting collection {_+1}/{(presentDate- datetemp).days //7}")
                    mainurl = f"https://api.github.com/search/repositories?q=created:{tempdate}T00:00:00%2B07:00..{date}T00:00:00%2B07:00&sort=stars&order=desc"
                    tempdict = get_data(mainurl)
                    date = tempdate
                    tempdatetimedate-= dt.timedelta(days=7)
                    tempdate = str(tempdatetimedate).split(" ")[0]
                    data |= tempdict
                    print("finished collection")
                print("finished all collections")
            else:
                print("Data.csv is up to date")
    else:
        print("Data.csv is up to date")
    print()
except Exception:
    # Data collection
    print("No data.csv found, starting data collection")
    for _ in range(0,((presentDate- starterdate).days //7)):
        print(f"starting collection {_+1}/{((presentDate- starterdate).days //7)}")
        mainurl = f"https://api.github.com/search/repositories?q=created:{tempdate}T00:00:00%2B07:00..{date}T00:00:00%2B07:00&sort=stars&order=desc"
        tempdict = get_data(mainurl)
        date = tempdate
        tempdatetimedate-= dt.timedelta(days=7)
        tempdate = str(tempdatetimedate).split(" ")[0]
        data |= tempdict
        print("finished collection")
    print("finished all collections")
    print()



# Data initiation
df = pd.DataFrame.from_dict(data, orient='index').sort_values(by='watchers_count',ascending=False)
df["index"] = [str(i)for i in range(0,len(data))]
df['watchers_count'] = pd.to_numeric(df['watchers_count'])

# Data cleaning and repairing
df["language"] = df["language"].fillna("No language")
df["firstparagraph"] = df["firstparagraph"].fillna("No paragraph")
data = df.to_dict(orient='index')
df.to_csv("data.csv")




#web app
@app.route('/')

def index() -> None:
    # Assuming 'data' is your dictionary of GitHub repositories

    # Create the DataFrame for the chart
    langstar = pd.DataFrame({
        'Language': np.array(df["language"]),
        'Stars': np.array(df["watchers_count"]),
        "name": np.array(df["name"])
    })
    
    # Calculate averages for second subplot
    langstar_grouped = langstar.groupby('Language')['Stars'].mean().reset_index()
    langstar_grouped = langstar_grouped.sort_values('Stars', ascending=False)
    
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Individual Repository Stars by Language',
                                        'Average Stars by Language'),
                        vertical_spacing=0.15)
    
    # First subplot - Individual points with trend line
    for language in langstar['Language'].unique():
        mask = langstar['Language'] == language
        fig.add_trace(
            go.Scatter(
                x=langstar[mask].index,
                y=langstar[mask]['Stars'],
                name=language,
                mode='markers',
                marker=dict(size=6),
                hovertemplate=f"{language}<br>Stars: %{{y}}<br>Index: %{{x}}<br>Name: %{{text}}",
                text=langstar[mask]['name']
            ),
            row=1, col=1
        )
    
    # Second subplot - Averages
    fig.add_trace(
        go.Bar(
            x=langstar_grouped['Language'],
            y=langstar_grouped['Stars'],
            name='Average Stars',
            hovertemplate='Language: %{x}<br>Average Stars: %{y:.0f}',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=1200,
        width=1200,
        title_text='Programming Languages Repository Stars Analysis',
        title_x=0.5,
        showlegend=True,
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.6,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150)
    )
    
    # Update axes
    fig.update_yaxes(type="log", title_text="Number of Stars", row=1, col=1)
    fig.update_xaxes(title_text="Index", row=1, col=1)
    fig.update_yaxes(title_text="Average Number of Stars", row=2, col=1)
    fig.update_xaxes(title_text="Programming Language", tickangle=45, row=2, col=1)
    
    # Create graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # HTML template
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trending GitHub Repositories</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.22/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>Trending GitHub Repositories</h1>
        
        <h2>Repository Table</h2>
        <table id="repoTable" class="display">
            <thead>
                <tr>
                    <th>ranking</th>
                    <th>Name</th>
                    <th>Language</th>
                    <th>Stars</th>
                    <th>URL</th>
                    <th>Date</th>
                    <th>Forks</th>
                    <th>Fork?</th>
                    
                </tr>
            </thead>
            <tbody>
                {% for repo in data.values() %}
                <tr>
                    <td>{{ repo["index"] }}</td>
                    <td>{{ repo["name"] }}</td>
                    <td>{{ repo["language"] or "N/A" }}</td>
                    <td>{{ repo["watchers_count"] }}</td>
                    <td><a href="{{ repo["html_url"] }}" target="_blank">{{ repo["html_url"] }}</a></td>
                    <td>{{ repo["date"] }}</td>
                    <td>{{ repo["forks"] }}</td>
                    <td>{{ repo["Fork?"] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h2>Repository Charts</h2>
        <div id="chart" style="width:100%;height:1200px;"></div>
        
        <script>
            $(document).ready(function() {
                $('#repoTable').DataTable();
            });
            
            var graphs = {{graphJSON | safe}};
            Plotly.plot('chart', graphs, {});
        </script>
    </body>
    </html>
    """
    return render_template_string(html, graphJSON=graphJSON, data=data)

def open_browser() -> None:
        webbrowser.open_new("http://127.0.0.1:5000")

Timer(1, open_browser).start()
app.run(port=5000)
    

