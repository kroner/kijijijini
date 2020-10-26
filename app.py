from flask import Flask, render_template, request, redirect
import model


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
        Xdict = {
			'title':request.form['title'],
			'description':request.form['description'],
			'item':'bed-mattress'
			}
		price = model.predict_price(Xdict)
		price_str = '$' + '{:.0d}'.format(price)
    else:
        price_str = ''
	return render_template('index.html',price=price_str)

@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == '__main__':
	app.run(port=33507)
