import datetime

from airflow import models
from airflow.operators.bash_operator import BashOperator

default_dag_args = {
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date
    'start_date': datetime.datetime(2019, 4, 1)
}

raw_dataset = 'college' # dataset with raw tables
new_dataset = 'college_workflow' # empty dataset for destination tables
sql_cmd_start = 'bq query --use_legacy_sql=false '

sql_student = 'create table ' + new_dataset + '.Student_Temp as select distinct sid, fname, lname, dob ' \
           'from ' + raw_dataset + '.Current_Student ' \
           'union distinct ' \
           'select distinct sid, fname, lname, cast(dob as string) as dob ' \
           'from college.New_Student'
       
sql_teacher = 'create table ' + new_dataset + '.Teacher_Temp as ' \
            'select distinct tid, instructor, dept ' \
            'from ' + raw_dataset + '.Class ' \
            'where tid is not null ' \
            'order by tid'

sql_class = 'create table '+ new_dataset + '.Class as ' \
            'select distinct cno, cname, cast(credits as int64) as credits ' \
            'from ' + raw_dataset + '.Class ' \
            'where cno is not null ' \
            'order by cno '

sql_teaches = 'create table ' + new_dataset + '.Teaches as ' \
            'select distinct tid, cno ' \
            'from ' + raw_dataset + '.Class ' \
            'where tid is not null ' \
            'and cno is not null ' \
            'order by tid'
            
sql_takes = 'create table ' + new_dataset + '.Takes_Temp as ' \
            'select distinct sid, cno, grade ' \
            'from ' + raw_dataset + '.Current_Student ' \
            'where sid is not null ' \
            'and cno is not null ' \
            'order by sid'


with models.DAG(
        'college_workflow1',
        schedule_interval=datetime.timedelta(days=1),
        default_args=default_dag_args) as dag:

    create_student_table = BashOperator(
            task_id='create_student_table',
            bash_command=sql_cmd_start + '"' + sql_student + '"')
            
    create_teacher_table = BashOperator(
            task_id='create_teacher_table',
            bash_command=sql_cmd_start + '"' + sql_teacher + '"')
            
    create_class_table = BashOperator(
            task_id='create_class_table',
            bash_command=sql_cmd_start + '"' + sql_class + '"')
            
    create_teaches_table = BashOperator(
            task_id='create_teaches_table',
            bash_command=sql_cmd_start + '"' + sql_teaches + '"')    
            
    create_takes_table = BashOperator(
            task_id='create_takes_table',
            bash_command=sql_cmd_start + '"' + sql_takes + '"')
            
    create_student_table >> create_teacher_table >> create_class_table >> create_teaches_table >> create_takes_table