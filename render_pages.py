import json
import datetime
import time

def read_whole_file(filename : str) -> str:
    descriptor = open(filename, 'r')
    result = descriptor.read()
    descriptor.close()
    return result

def generate_paper_html(paper, id) -> str:
    result = ""
    result += "<div class=\"post-row\" id=\"paper-%d\" style=""> <div class=\"post-heading\">" % id
    result += "<script>paper_id_list.push([\"paper-%d\", %s]);</script>" % (id, str(paper['topics']))
    for topic in paper['topics']:
        result += "<div><img src=\"%s.svg\" style=\"height: 17pt; margin-right: 1pt;\"></div>" % topic
    result += "<div> <h3 class=\"paper-header\" onclick=\"toggleVisibility(%d)\">%s</h3></div>" % (id, paper['title'])
    result += "</div>"
    result +=  """
                <div style='display: flex;  align-items: right' >
		        <div style='margin: 0.2rem; font-weight: 600'>Authors: </div>
            """
    for author in paper['author']:
        result += "<a href=\"%s\" class=\"inside-post\">%s</a>" % (author['url'], author['name'])
    result += """
                </div>
                <div style="display: flex; align-items: right; " >                      
                <div style='margin: 0.2rem; font-weight: 600'> Links: </div>
            """
    for link in paper['links']:
        result += "<a href=\"%s\" class=\"inside-post\">%s</a>" % (link['url'], link['name'])                           
    result += "</div>"
    result += "<div id = \"abstract%d\" class=\"abstract\" style=\"display: none;\">%s</div>" % (id, paper['abstract'] if 'abstract' in paper else "")
    result += "</div>"
    return result

papers = json.load(open('data.json', 'r'))
header_html = read_whole_file('header.html')
footer_html = read_whole_file('footer.html')
intro_html = read_whole_file('intro.html')


# Generate the main page
index = open('index2.html', 'w')

index.write(header_html)
index.write(intro_html)

index.write("""
            <div class=\"container\">
            <div class=\"papers-header-class\">
            <div class=\"papers-header-div\"><h2 id=\"papers-header\">Papers</h2></div>
            """)
for topic in ["all", "proof-complexity", "communication-complexity", "circuit-complexity", "combinatorics"]:
    svg_body = read_whole_file(topic + ".svg")
    index.write("<div id=\"%s-icon\" class=\"paper-topic-icon\" onclick=\"filterPapers('%s')\">%s</div>" % (topic, topic, svg_body))
index.write("""</div>
            <div id=\"papers-container\" style=\"display: none;\">
            """)
for id, paper in enumerate(sorted(papers, key=lambda paper: -datetime.datetime.fromisoformat(paper['date']).timestamp())):
    index.write(generate_paper_html(paper, id))
index.write("</div></div>")

index.write(footer_html % datetime.date.today())

index.close()