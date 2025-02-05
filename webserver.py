from flask import Flask, render_template, redirect
from multiprocessing import Process
import time


s = "not okei"

app = Flask(__name__)

@app.route('/main')
@app.route('/')
def home():
	return render_template("main.html")

@app.route('/zones')
def zones():
	return render_template("zones.html", content=s)

def run_app():
	app.run()
	
process = Process(target=run_app)
process.start()

print('Okei')

for i in range(120):
	time.sleep(2)
	s = "okei!"
	render_template("zones.html", content=s)
	print(i)

#if __name__ == "__main__":
	#app.run(debug=True)
