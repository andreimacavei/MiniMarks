from flask import Flask
app = Flask(__name__)

@app.route('/')
def login():
	html = """
		<h1>Welcome yo <b>Your</b> Queue</h1>
		<br><br><br><br><br>
		<h2>This is the right place to store interesting stuff you'd want to read later</h2>
		<br><br><br><br>
		<center>
			<form action="login.js" method="POST">
			<fieldset>
			<legend>Sign In</legend>
				Username: <input type="text" name="username">
				<br>
				Password: <input type="text" name="password">
				<br><br>
				<input type="submit" value="Submit">
			</fieldset>
			</form>
		</center>
		<p>Not a member yet? Register now and start manage your time properly!
		
	"""
	return html
	


	
	
if __name__ == '__main__':
	app.run(debug=True)