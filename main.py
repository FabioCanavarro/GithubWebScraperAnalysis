#libraries
import markdown
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

def open_browser() -> None:
        print("Opening browser")
        webbrowser.open_new("http://127.0.0.1:5000")

def main():
    def LLMreq(data: dict) -> str:
        prompt = "context: Tell me the prominent trends like the theme and other trends without the example \n prompt:summarize the trends in the data, these are the top 10 most starred github repositories in the last 30 days stored in a tuple(name,firstparagraph, star count), since this is data scraped the first paragraph sometimes may have some errors:"+str([(i,data["firstparagraph"],data["watchers_count"]) for i in data])
        response = model.generate_content(prompt)
        return(response.text)
    def get_data(url: str) -> dict:
    
        response = req.get(url,headers={"User-Agent": "siti21532704","Accept":"application/json, text/plain, */*","x-github-api-version-selected":"2022-11-28","authorization":"token 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"})
        print("Response status code:",response.status_code)
        if str(response.status_code)[0] == 4:
            return _extracted_from_get_data_6(response, "Error in response")
        if json.loads(response.text)["total_count"] == 0:
            return _extracted_from_get_data_6(response, "No repositories found")
        responses = json.loads(response.text)["items"]
        repo = {
            i["full_name"]: {"name":i["full_name"],"html_url":i["html_url"],"language":i["language"],"watchers_count": i["watchers_count"], "firstparagraph": "","date":date,"forks":i["forks_count"],"Fork?":i["fork"]}
            for i in responses
        }
        total = len(repo)
        bar_length = 20
        # Get the first paragraph of the readme to get some context
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
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)

            # Clear line and print progress
            sys.stdout.write('\r')
            sys.stdout.write(f"Processing repositories: [{bar}] {index + 1}/{total} {progress:.0%}")
            sys.stdout.flush()

            time.sleep(0.1)
        return repo

    def _extracted_from_get_data_6(response, arg1):
        print(response.text)
        print(arg1)

        return {}
    
    
    # Initiate the date
    presentDate = dt.datetime.now()
    date = str(presentDate).split(" ")[0]
    tempdatetimedate = presentDate- dt.timedelta(days=7)
    tempdate = str(tempdatetimedate).split(" ")[0]
    data = {}
    starterdate = presentDate - dt.timedelta(days=30)
    # Check if a data.csv file with present info exists
    try:
        data = pd.read_csv("data.csv").sort_values(by="date",ascending=False).to_dict(orient='index')
        datetemp = dt.datetime.strptime(data[list(data.keys())[0]]["date"],"%Y-%m-%d")
        print("Data.csv found")
        if datetemp != presentDate:
            with contextlib.suppress(Exception):
                if ((presentDate- datetemp).days //7) > 0:
                    print("data.csv is outdated, updating")
                    for _ in range((presentDate- datetemp).days //7):
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
        for _ in range((presentDate- starterdate).days //7):
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
    df["index"] = [str(i)for i in range(len(data))]
    df['watchers_count'] = pd.to_numeric(df['watchers_count'])

    # Data cleaning and repairing
    df["language"] = df["language"].fillna("No language")
    df["firstparagraph"] = df["firstparagraph"].fillna("No paragraph")
    data = df.to_dict(orient='index')

    # Saving data
    df.to_csv("data.csv", index=False)

    # Generate summary using an LLM
    summary = LLMreq(df[:10]) 
    summary_html = markdown.markdown(summary)


    # Web app
    print("Loading html and website")
    @app.route('/')
    def index() -> None:
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
        
        # First subplot
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
        
        # Second subplot
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
            width=1123,
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
        <title>Trending GitHub Repositories - LeetCode Style</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.22/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            :root {
                --leetcode-black: #1a1a1a;
                --leetcode-dark-gray: #2d2d2d;
                --leetcode-gray: #3e3e3e;
                --leetcode-light-gray: #eff1f6;
                --leetcode-green: #00b8a3;
                --leetcode-yellow: #ffc01e;
                --leetcode-blue: #02a4ff;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: var(--leetcode-light-gray);
                margin: 0;
                padding: 0;
                background-color: var(--leetcode-black);
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            h1, h2 {
                color: var(--leetcode-green);
                text-align: center;
                margin-bottom: 30px;
            }
            
            h1 {
                font-size: 2.5em;
                border-bottom: 2px solid var(--leetcode-green);
                padding-bottom: 10px;
            }
            
            h2 {
                font-size: 1.5em;
                margin-top: 30px; 
                margin-bottom: 20px;
            }
            
            #repoTable {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin-bottom: 30px;
                background-color: var(--leetcode-dark-gray);
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                overflow: hidden;
                color: #eff1f6;
            }
            
            #repoTable th, #repoTable td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid var(--leetcode-gray);
            }
            
            #repoTable th {
                background-color: var(--leetcode-gray);
                font-weight: bold;
                text-transform: uppercase;
                color: #00b8a3;
            }
            #repoTable td {
                background-color: #2d2d2d;
            }
            #repoTable tr:hover td {
                background-color: #3e3e3e;
            }
            #repoTable tr:hover {
                background-color: var(--leetcode-gray);
            }
            
            #repoTable a {
                color: var(--leetcode-blue);
                text-decoration: none;
            }
            
            #repoTable a:hover {
                text-decoration: underline;
            }
            
            #chart-container {
                position: relative;
                background-color: var(--leetcode-dark-gray);
                border-radius: 8px;
                margin-top: 40px;
                padding: 40px;
            }

            #chart-container::before {
                content: '';
                position: absolute;
                top: 20px;
                left: 20px;
                right: 20px;
                bottom: 20px;
                z-index: -1;
                background-color: var(--leetcode-dark-gray);
                border-radius: 8px;
                box-shadow: 0 0 40px rgba(0, 0, 0, 0.3);
            }
            
            #chart {
                width: 100%;
                height: 100%;
            }
            
            .dataTables_wrapper .dataTables_length, 
            .dataTables_wrapper .dataTables_filter, 
            .dataTables_wrapper .dataTables_info, 
            .dataTables_wrapper .dataTables_processing, 
            .dataTables_wrapper .dataTables_paginate {
                margin-bottom: 10px;
                color: var(--leetcode-light-gray);
            }
            
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                color: var(--leetcode-light-gray) !important;
                background-color: var(--leetcode-gray) !important;
                border: none !important;
            }
            
            .dataTables_wrapper .dataTables_paginate .paginate_button.current, 
            .dataTables_wrapper .dataTables_paginate .paginate_button.current:hover {
                background: var(--leetcode-green) !important;
                color: var(--leetcode-black) !important;
                border: none !important;
            }
            
            #ai-summary {
                background-color: var(--leetcode-dark-gray);
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-top: 40px;
                padding: 30px;
            }
            
            #ai-summary h2 {
                color: var(--leetcode-yellow);
                font-size: 24px;
                margin-bottom: 20px;
                text-align: left;
                border-bottom: 2px solid var(--leetcode-yellow);
                padding-bottom: 10px;
            }
            
            .summary-content {
                display: flex;
                align-items: flex-start;
            }
            
            .summary-icon {
                flex-shrink: 0;
                margin-right: 20px;
            }
            
            .ai-icon {
                width: 40px;
                height: 40px;
                color: var(--leetcode-yellow);
            }
            
            .summary-text {
                flex-grow: 1;
            }
            
            .summary-text p {
                font-size: 16px;
                line-height: 1.6;
                color: var(--leetcode-light-gray);
                margin: 0;
                white-space: pre-wrap;
            }
            
            @media (max-width: 768px) {
                .summary-content {
                    flex-direction: column;
                }
                
                .summary-icon {
                    margin-bottom: 15px;
                }
            }
            .chart-info {
                text-align: center;
                color: var(--leetcode-light-gray);
                font-style: italic;
                margin-top: 10px;
            }
        </style>
        </head>
        <body>
        <div class="container">
            <h1>Trending GitHub Repositories</h1>
            
            <h2>Repository Table</h2>
            <table id="repoTable" class="display">
                <thead>
                    <tr>
                        <th>Ranking</th>
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
            <div id="chart-container">
                <div id="chart"></div>
                <p class="chart-info">Hover over the datapoints for more detailed information about each repository.</p>
            </div>
            <div style="display: none;">Debug: {{ summary_text }}</div>
            <div id="ai-summary">
                <h2>AI-Generated Insights</h2>
                <div class="summary-content">
                    <div class="summary-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ai-icon">
                            <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2Z"></path>
                            <path d="M12 16v-4"></path>
                            <path d="M12 8h.01"></path>
                        </svg>
                    </div>
                    <div class="summary-text">
                        <p>{{ summary_text | safe}}</p>
                    </div>
                </div>
            </div>
        </div>
        
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
        return render_template_string(html, graphJSON=graphJSON, data=data, summary_text=summary_html)
    print("Html and website loaded")
    print()


if __name__ == "__main__":
    main()
    Timer(1, open_browser).start()
    app.run()
    
    
