
from flask import *
import warnings
warnings.filterwarnings("ignore")
import pymysql
from config import *
import time

app = Flask(__name__)
app.config.from_object(__name__)

# 连接数据库
def connectdb():
	db = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE, port=PORT, use_unicode=True, charset=CHARSET)
	db.autocommit(True)
	cursor = db.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')
	return (db,cursor)

# 关闭数据库
def closedb(db,cursor):
	db.close()
	cursor.close()

# 首页
@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html',label=0)
	else:
		data = request.form
		xn = data.get('xn')
		xq = data.get('xq')
		if xq =='第一学期':
			xq = '0'
		else:
			xq = '1'
		if data.get('number'):
			number = data.get('number')
			return redirect(url_for('getscore',number=number,xn=xn,xq=xq))
		else:
			name = data.get('name')
			# 连接数据库
			(db,cursor) = connectdb()

			# 获取学生信息
			cursor.execute("select * from stu_info where name=%s", name)
			stu_info = cursor.fetchall()
			length = len(stu_info)
			print(length)
			posts = []
			if length>1:
				for i in range(length):
					posts.append(stu_info[i][2:])
				return render_template('index.html',label=1,posts=posts,xn=xn,xq=xq)
			elif length==1:
				return redirect(url_for('getscore',number=stu_info[0][2],xn=xn,xq=xq))
			else:
				return render_template('index.html', label = 2,xn=xn,xq=xq)
				
# 处理表单提交
@app.route('/getscore/')
def getscore():
	# 获取get数据
	number = request.values.get('number')
	xn = request.values.get('xn')
	xq= request.values.get('xq')
	
	# 连接数据库
	(db,cursor) = connectdb()

	# 获取学生信息
	cursor.execute("select * from stu_info where number=%s", number)
	stu_info = cursor.fetchall()[0]
	stu_info = stu_info[2:]
	
	# 获取学生成绩
	cursor.execute("select * from stu_score where number=%s and xn=%s and xq=%s", (number, xn, xq))
	stu_score = cursor.fetchall()

	posts = []
	posts.append(stu_info)
	for L in stu_score:
		posts.append(L[2:-3])
	posts.append(xn)
	posts.append(str(int(xn) + 1))
	if xq =='0':
		xq = '第一学期'
	else:
		xq = '第二学期'
	posts.append(xq)
	search_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	posts.append(search_time)
	# 关闭数据库
	closedb(db,cursor)

	return render_template('score.html', posts=posts)



if __name__ == '__main__':
	app.run(debug=True)