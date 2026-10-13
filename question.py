import sqlite3
from flask import Flask, request, render_template_string, abort

app = Flask(__name__)
DB = "crush.db"
ADMIN_KEY = "change-this-secret"   # change this to your own password


def get_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        your_name TEXT,
        crush_name TEXT,
        created TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return conn


FORM = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crush Confession</title>
  <style>
    body { font-family: Arial, sans-serif; background: #ffe6ee; display: flex;
           justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .box { background: white; padding: 24px; border-radius: 12px; width: 90%;
           max-width: 340px; box-shadow: 0 4px 12px rgba(0,0,0,.1); }
    h2 { text-align: center; color: #d6336c; }
    input, button { width: 100%; padding: 10px; margin-top: 10px; box-sizing: border-box;
                    border-radius: 8px; border: 1px solid #ccc; }
    button { background: #d6336c; color: white; border: none; cursor: pointer; }
    small { color: #777; display: block; margin-top: 10px; text-align: center; }
  </style>
</head>
<body>
  <div class="box">
    {% if done %}
      <h2>Thanks! 💘</h2>
      <p style="text-align:center">Your answer was sent.</p>
    {% else %}
      <h2>💘 Who's your crush?</h2>
      <form method="POST">
        <input type="text" name="your_name" placeholder="Your name (optional)">
        <input type="text" name="crush_name" placeholder="Crush's name" required>
        <button type="submit">Send</button>
      </form>
      <small>Note: let see your match with your crush...nobody will know ,its a secret.</small>
    {% endif %}
  </div>
</body>
</html>
"""

RESULTS = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Answers</title>
<style>
  body { font-family: Arial, sans-serif; padding: 20px; }
  table { border-collapse: collapse; width: 100%; max-width: 600px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background: #ffe6ee; }
</style></head>
<body>
  <h2>Answers ({{ rows|length }})</h2>
  <table>
    <tr><th>From</th><th>Crush</th><th>Time</th></tr>
    {% for r in rows %}
      <tr><td>{{ r[0] or "Anonymous" }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        your_name = request.form.get("your_name", "").strip()[:100]
        crush_name = request.form.get("crush_name", "").strip()[:100]
        if crush_name:
            conn = get_db()
            conn.execute("INSERT INTO answers (your_name, crush_name) VALUES (?, ?)",
                         (your_name, crush_name))
            conn.commit()
            conn.close()
        return render_template_string(FORM, done=True)
    return render_template_string(FORM, done=False)


@app.route("/results")
def results():
    if request.args.get("key") != ADMIN_KEY:
        abort(403)
    conn = get_db()
    rows = conn.execute(
        "SELECT your_name, crush_name, created FROM answers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(RESULTS, rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
