from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Logging setup
logging.basicConfig(filename="scrapper.log", level=logging.INFO)

# Flask app setup
app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            print(f"Flipkart URL: {flipkart_url}") # debugging
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")

            bigboxes = flipkart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            print(f"Big Boxes Found: {len(bigboxes)}")

            del bigboxes[0:3]

            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            print(f"Product Link: {productLink}")

            prodRes = requests.get(productLink)
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "RcXBOT"})  
            print(f"Comment Boxes Found: {len(commentboxes)}")

            # filename = searchString + ".csv"
            # fw = open(filename, "w")
            # headers = "Product, Customer Name, Rating, Heading, Comment \n"
            # fw.write(headers)
            reviews = []

            for commentbox in commentboxes:
                # print(f"Name: {name}, Rating: {rating}, Comment Head: {commentHead}, Comment: {custComment}")

                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2NsDsF AwS1CA'})[0].text
                    print(name)
                    # name = commentbox.div.div.div.div.find_all('p', {'class': '_2NsDsF AwS1CA'})[0]
                except:
                    logging.info("name")

                try:
                    rating = commentbox.div.div.div.div.text
                    print(rating)
                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    commentHead = commentbox.div.div.div.p.text
                    print(commentHead)
                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                    print(custComment)
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead, "Comment": custComment}
                reviews.append(mydict)

            logging.info("log my final result {}".format(reviews))
            
    
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run()
