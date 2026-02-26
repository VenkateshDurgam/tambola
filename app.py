from flask import Flask, render_template_string, request, redirect, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "venkatesh_secret_key"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("tambola.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            numbers TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN PAGE ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <title>Login</title>
    <style>
    body{display:flex;justify-content:center;align-items:center;height:100vh;
    background:linear-gradient(135deg,#000428,#004e92);color:white;font-family:sans-serif}
    form{background:#001f3f;padding:30px;border-radius:10px}
    input{display:block;margin:10px 0;padding:10px;width:200px}
    button{padding:10px;background:gold;border:none;font-weight:bold}
    </style>
    </head>
    <body>
    <form method="POST">
    <h2>Admin Login</h2>
    <input name="username" placeholder="Username">
    <input name="password" type="password" placeholder="Password">
    <button>Login</button>
    </form>
    </body>
    </html>
    """)

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "admin" not in session:
        return redirect("/login")

    return render_template_string("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Professional Tambola</title>

<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:sans-serif;background:linear-gradient(135deg,#000428,#004e92);color:white}
.container{display:flex;min-height:100vh}
.sidebar{width:220px;background:#001f3f;padding:15px;display:flex;flex-direction:column;gap:10px}
.sidebar button{padding:10px;border:none;border-radius:8px;font-weight:bold;cursor:pointer}
.main{flex:1;padding:20px;text-align:center}
#numberDisplay{font-size:120px;font-weight:bold}
.number-animate{animation:zoomGlow 1s ease}
@keyframes zoomGlow{
0%{transform:scale(0.3);opacity:0;text-shadow:0 0 10px #fff}
50%{transform:scale(1.4);text-shadow:0 0 40px gold}
100%{transform:scale(1);opacity:1;text-shadow:0 0 20px gold}
}
.board{display:grid;grid-template-columns:repeat(10,40px);gap:5px;justify-content:center;margin-top:20px}
.cell{width:40px;height:40px;border-radius:50%;background:#5d4037;display:flex;align-items:center;justify-content:center;font-size:12px}
.called{background:gold;color:#003366}
#history{margin-top:20px;display:flex;flex-wrap:wrap;gap:5px;justify-content:center}
#history span{background:gold;color:#003366;padding:5px 10px;border-radius:20px;font-size:12px}
@media(max-width:800px){
.container{flex-direction:column}
.sidebar{width:100%;flex-direction:row;flex-wrap:wrap;justify-content:center}
#numberDisplay{font-size:70px}
}
</style>
</head>

<body>
<div class="container">

<div class="sidebar">
<button onclick="startGame()">▶ Start</button>
<button onclick="autoMode()">🔁 Auto</button>
<button onclick="pushNumber()">▶ Push</button>
<button onclick="saveGame()">💾 Save</button>
<button onclick="exportNumbers()">📤 Export</button>
<a href="/history"><button>📊 History</button></a>
<a href="/logout"><button>🚪 Logout</button></a>
</div>

<div class="main">
<h1>🎉 TAMBOLA 🎉</h1>
<div id="numberDisplay">--</div>
<div class="board" id="board"></div>
<h3>Called Numbers</h3>
<div id="history"></div>
</div>

</div>

<script>
let numbers=[],called=[],timer=null;

function createBoard(){
for(let i=1;i<=90;i++){
let d=document.createElement("div");
d.className="cell";
d.id="cell-"+i;
d.innerText=i;
document.getElementById("board").appendChild(d);
}}
createBoard();

function shuffle(){
numbers=[];called=[];
document.getElementById("history").innerHTML="";
for(let i=1;i<=90;i++)numbers.push(i);
numbers.sort(()=>Math.random()-0.5);
}

function startGame(){shuffle();}

function pushNumber(){showNumber();}

function autoMode(){
showNumber();
timer=setTimeout(autoMode,6000);
}

function showNumber(){
if(numbers.length===0){alert("Game Finished");return;}
let num=numbers.pop();
called.push(num);
let display=document.getElementById("numberDisplay");
display.innerText=num;
display.classList.remove("number-animate");
void display.offsetWidth;
display.classList.add("number-animate");
document.getElementById("cell-"+num).classList.add("called");
let span=document.createElement("span");
span.innerText=num;
document.getElementById("history").appendChild(span);
let msg=new SpeechSynthesisUtterance("Number "+num);
speechSynthesis.speak(msg);
}

function saveGame(){
fetch("/save",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({numbers:called.join(", ")})
}).then(()=>alert("Game Saved"));
}

function exportNumbers(){
let blob=new Blob([called.join(", ")],{type:"text/plain"});
let link=document.createElement("a");
link.href=URL.createObjectURL(blob);
link.download="Tambola.txt";
link.click();
}
</script>

</body>
</html>""")

# ---------------- SAVE ----------------
@app.route("/save", methods=["POST"])
def save():
    data=request.json
    date=datetime.now().strftime("%d-%m-%Y %H:%M")
    conn=sqlite3.connect("tambola.db")
    c=conn.cursor()
    c.execute("INSERT INTO games (date,numbers) VALUES (?,?)",(date,data["numbers"]))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    conn=sqlite3.connect("tambola.db")
    c=conn.cursor()
    c.execute("SELECT * FROM games ORDER BY id DESC")
    games=c.fetchall()
    conn.close()
    rows=""
    for g in games:
        rows+=f"<tr><td>{g[0]}</td><td>{g[1]}</td><td>{g[2]}</td></tr>"
    return f"""
    <html><body style='background:#000428;color:white;font-family:sans-serif'>
    <h2>Game History</h2>
    <table border=1 cellpadding=10>
    <tr><th>ID</th><th>Date</th><th>Numbers</th></tr>
    {rows}
    </table>
    <br><a href='/'><button>⬅ Back</button></a>
    </body></html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)