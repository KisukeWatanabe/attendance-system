from flask import render_template,url_for,redirect,flash,request,abort,jsonify
from flask_login import login_user,logout_user,login_required,current_user
from time_project import db
from time_project.main.form import Loginform,Registrationform,UpdateUserform,TimeCorrectform
from time_project.models import User , Timepage
from flask import Blueprint
from datetime import datetime,date,timedelta
import calendar
from collections import defaultdict

main = Blueprint('main',__name__,)

#ログインページ
@main.route('/login', methods = ['GET','POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(users_id =form.users_id.data).first()
        if user is not None:
            if not user.is_administrator:
                flash('管理者以外はログインできません')
                return redirect(url_for('main.login'))
            
            if user.checkpassword(form.password.data):
                login_user(user)
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('main.user_maintenance')
                return redirect(next)
            else:
                flash('パスワードが一致しません')
        else:
           flash('入力されたユーザーは存在しません')


    return render_template('login.html',form = form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.user_maintenance'))

#従業員管理ページ　
@main.route('/user_maintenance')
@login_required
def user_maintenance():
    page = request.args.get('page',1,type = int)
    users = User.query.order_by(User.id).paginate(page=page)
    return render_template('user_maintenance.html',users=users)

#ユーザー修正ページ
@main.route('/<int:user_id>/user_account',methods = ['GET','POST'])
@login_required
def user_account(user_id):
    user =  User.query.get_or_404(user_id)
    form = UpdateUserform(user_id=user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.users_id = form.users_id.data
        user.employment_type = form.employment_type.data
        hw = form.hourly_wage.data
        fw = form.fixed_wage.data
        user.hourly_wage = int(hw) if hw and hw.isdigit() else None
        user.fixed_wage = int(fw) if fw and fw.isdigit() else None

        if form.password.data:
            user.passoword = form.password.data

        db.session.commit()
        flash('ユーザーアカウントが更新されました。')
        return redirect(url_for('main.user_maintenance'))    
    elif request.method == 'GET':
        form.username.data = user.username
        form.users_id.data = user.users_id
        form.employment_type.data = user.employment_type
        form.hourly_wage.data = str(user.hourly_wage) if user.hourly_wage is not None else ''
        form.fixed_wage.data = str(user.fixed_wage) if user.fixed_wage is not None else ''
    return render_template('user_account.html',form = form)

#ユーザー追加ページ
@main.route('/user_register', methods = ['GET','POST'])
@login_required
def user_register():
    form = Registrationform()
    if not current_user.is_administrator:
         abort(403)
    if form.validate_on_submit():
        user = User(username = form.username.data,
                    users_id = form.users_id.data,
                    password = form.password.data,
                    administrator="0",
                    employment_type= form.employment_type.data,
                    hourly_wage=form.hourly_wage.data,
                    fixed_wage=form.fixed_wage.data)
        db.session.add(user)
        db.session.commit()
        flash('ユーザーが追加されました。')
        return redirect(url_for('main.user_maintenance'))
    return render_template('user_register.html',form = form)

#ユーザー削除ページ
@main.route('/<int:user_id>/delete',methods = ['GET','POST'])
@login_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_administrator:
        flash('管理者アカウントは削除できません！')
        return redirect(url_for('main.user_maintenance'))
    Timepage.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main.user_maintenance'))

#出退勤管理ページ
@main.route('/work_timepage')
@login_required
def work_timepage():
    def get_salary_period(year, month):
        #前月21日から今月20日まで表示
        if month == 1:
            start = date(year - 1, 12, 21)
            end = date(year, 1, 20)
        else:
            start = date(year, month - 1, 21)
            end = date(year, month, 20)
        return start, end

    users = User.query.all()
    today = datetime.today().date()

    # 今日の日付で表示月を決定
    if today.day >= 21:
        if today.month == 12:
            default_year = today.year + 1
            default_month = 1
        else:
            default_year = today.year
            default_month = today.month + 1
    else:
        default_year = today.year
        default_month = today.month

    

    select_user_id = request.args.get('user_id', type=int, default=1)
    select_user = User.query.get_or_404(select_user_id)
    select_username = request.args.get('username')
    select_year = request.args.get('year', default_year, type=int)
    select_month = request.args.get('month', default_month, type=int)

    if select_month == 12:
        next_month = 1
    else:
        next_month = select_month + 1

    # 前月21日〜当月20日
    period_start, period_end = get_salary_period(select_year, select_month)
    days_in_period = (period_end - period_start).days + 1

    def round_up(dt):
        #15分単位で切り上げ
        minutes = dt.hour * 60 + dt.minute
        return ((minutes + 14) // 15) * 15

    def round_down(dt):
        #15分単位で切り捨て
        minutes = dt.hour * 60 + dt.minute
        return (minutes // 15) * 15

    daily_records = {}
    summary = {
        'working_days': 0,
        'total_minutes': 0,
        'overtime_minutes': 0,
        'dayly_salary': 0,
        'basic_salary': 0,
        'employment_type': select_user.employment_type,
        'hourly_wage': select_user.hourly_wage,
        'fixed_wage': select_user.fixed_wage,
    }
    records_raw = Timepage.query.filter(
        Timepage.user_id == select_user_id,
        Timepage.date >= period_start,
        Timepage.date <= period_end
    ).all()

    for r in records_raw:
        check_in = r.check_in
        check_out = r.check_out
        rest_in = r.rest_in
        rest_out = r.rest_out

        regular_minutes = 0
        overtime_minutes = 0
        daily_salary = 0
        
        if check_in and check_out:
            # 丸め処理
            in_minutes = round_up(check_in)
            out_minutes = round_down(check_out)

           
            if out_minutes < in_minutes:
                # 日をまたぐ場合の対応
                rolled_over_minutes = out_minutes + 1440 - in_minutes
                # 15分未満の早退（誤操作など）を無効にする
                if rolled_over_minutes == 1425: 
                    work_minutes = 0
                else:
                    out_minutes += 1440
                    work_minutes = out_minutes - in_minutes
            else:
                work_minutes = out_minutes - in_minutes
            # 休憩時間の処理
            rest_minutes = 0
            if rest_in and rest_out:
                rest_start = round_up(rest_in)
                rest_end = round_down(rest_out)
                #日をまたぐ場合の対応
                if rest_end < rest_start:
                    rest_end += 1440
                rest_minutes = rest_end - rest_start

            # 正味労働時間
            net_minutes = max(work_minutes - rest_minutes, 0)

            # 15分未満は無効
            if net_minutes < 15:
                net_minutes = 0
                regular_minutes = 0
                overtime_minutes = 0
                daily_salary = 0
            else:
                # 残業処理（22時以降）
                normal_limit = 22 * 60
                if out_minutes <= normal_limit:
                    regular_minutes = net_minutes
                    overtime_minutes = 0
                else:
                    regular_minutes = max(normal_limit - in_minutes - rest_minutes, 0)
                    overtime_minutes = max(out_minutes - normal_limit, 0)

                total_work_minutes = regular_minutes + (overtime_minutes * 1.5)

                # 給与計算
                if summary['employment_type'] == "parttime":
                    adjusted_minutes = (total_work_minutes // 15) * 15
                    daily_salary = (adjusted_minutes / 60) * summary['hourly_wage']
                    summary['basic_salary'] += daily_salary
                elif summary['employment_type'] == "fulltime":
                    daily_salary = 0
            # 集計（15分以上勤務がある日のみ）
            if net_minutes >= 15:
                summary['working_days'] += 1
                summary['total_minutes'] += regular_minutes
                summary['overtime_minutes'] += overtime_minutes

            # 日別記録に追加
            daily_records[r.date] = {
                'record': r,
                'regular_minutes': regular_minutes,
                'overtime_minutes': overtime_minutes,
                'daily_salary': daily_salary
            }
        
    return render_template('work_timepage.html',
                           users = users,
                           select_username = select_username,
                           select_user = select_user,
                           select_year = select_year,
                           select_month = select_month,
                           next_month = next_month,
                           period_start=period_start,
                           period_end=period_end,
                           days_in_period = days_in_period,
                           current_year = today.year,
                           daily_records = daily_records,
                           summary = summary,
                           timedelta=timedelta)
#メインの出退勤ページ
@main.route('/', methods=['GET', 'POST'])
def index():
    users = User.query.order_by(User.id).all()
    today = datetime.now().date()
    user_status = {}

    for user in users:
        record = Timepage.query.filter_by(user_id=user.id, date=today).first()
        if record:
            if record.rest_in and not record.rest_out:
                user_status[user.id] = "on_break"    #休憩中
            elif record.check_in and not record.check_out:
                user_status[user.id] = "working"     #出勤中
            else:
                user_status[user.id] = "none"        #退勤済み
        else:
            user_status[user.id] = "none"

    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'データが受け取れませんでした'}), 400

        user_id = data.get('user_id')
        time_str = data.get('time')
        event_type = data.get('eventType')
        time = datetime.strptime(time_str, '%H:%M:%S').time()

        record = Timepage.query.filter_by(user_id=user_id, date=today).first()
        if not record:
            record = Timepage(user_id=user_id, date=today)
            db.session.add(record)

        if event_type == "出勤":
            if record.check_in:
                return jsonify({'error': '既に本日出勤しています！'}), 400
            else:
                record.check_in = time
        elif event_type == "退勤":
            check_out_datetime = datetime.combine(today, time)
            if time < record.check_in:
                check_out_datetime += timedelta(days=1)
            record.check_out = check_out_datetime.time()
        elif event_type == "休憩":
            record.rest_in = time
        elif event_type == "復帰":
            record.rest_out = time

        db.session.commit()
        
        return jsonify({'message': '打刻成功'}), 200
    else:
        # GETのときは普通にテンプレートを返す
        return render_template('index.html', users=users, user_status=user_status)
    
#打刻修正ページ
@main.route('/<int:user_id>/<int:year>/<int:month>/<int:day>/time_correct',methods=['GET','POST'])
@login_required
def time_correct(user_id,year,month,day):
    form = TimeCorrectform()
    target_date = date(year,month,day)
    record = Timepage.query.filter_by(user_id=user_id,date=target_date).first()

    if form.validate_on_submit():
        
        if not record:
            record = Timepage(user_id=user_id,date=target_date)
            db.session.add(record)
        record.check_in = form.check_in.data
        record.check_out = form.check_out.data
        record.rest_in = form.rest_in.data
        record.rest_out = form.rest_out.data
        db.session.commit()
        flash('打刻修正が完了しました')
        return redirect(url_for('main.work_timepage'))
    
    if record:
        form.check_in.data = record.check_in
        form.check_out.data = record.check_out
        form.rest_in.data = record.rest_in
        form.rest_out.data = record.rest_out

    return render_template('time_correct.html',form=form,record=record)


@main.route('/<int:timepage_id>/time_delete',methods=['GET','POST'])
@login_required
def time_delete(timepage_id):
    record= Timepage.query.get_or_404(timepage_id)
    db.session.delete(record)
    db.session.commit()
    flash('打刻記録を削除しました。')
    return redirect(url_for('main.work_timepage'))
    







