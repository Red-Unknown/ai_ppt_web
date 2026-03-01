import json
import glob
import os

def generate_html_summary():
    score_files = glob.glob(os.path.join(os.path.dirname(__file__), "evaluation", "*_score.json"))
    
    html = """
    <html>
    <head>
        <title>Test Plan Summary</title>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .score { font-weight: bold; }
            .pass { color: green; }
            .fail { color: red; }
        </style>
    </head>
    <body>
        <h1>Test Plan Summary</h1>
        <h2>Tool Evaluation Scores</h2>
        <table>
            <tr>
                <th>Tool Name</th>
                <th>Final Score</th>
                <th>Functionality</th>
                <th>Latency</th>
                <th>Stability</th>
                <th>Error Handling</th>
                <th>Resource</th>
                <th>Scalability</th>
                <th>Security</th>
            </tr>
    """
    
    for file_path in score_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            dims = data.get("dimension_scores", {})
            html += f"""
            <tr>
                <td>{data.get('tool_name')}</td>
                <td class="score">{data.get('final_score')}</td>
                <td>{dims.get('functionality')}</td>
                <td>{dims.get('latency')}</td>
                <td>{dims.get('stability')}</td>
                <td>{dims.get('error_handling')}</td>
                <td>{dims.get('resource_usage')}</td>
                <td>{dims.get('scalability')}</td>
                <td>{dims.get('security')}</td>
            </tr>
            """
            
    html += """
        </table>
        
        <h2>ReAct Benchmark</h2>
        <p><a href="react_benchmark_report.md">View Detailed ReAct Benchmark Report</a></p>
        
    </body>
    </html>
    """
    
    output_path = os.path.join(os.path.dirname(__file__), "test_plan_summary.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Summary generated: {output_path}")

if __name__ == "__main__":
    generate_html_summary()
